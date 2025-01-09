"""tplink_ipc_implement core.

This module provides the core functionality for interacting with tplink_ipc_implement devices.
"""

import base64
import binascii
import json
import logging
from urllib.parse import unquote

import aiohttp
from asn1crypto.keys import PublicKeyInfo
import requests
import rsa

_LOGGER = logging.getLogger(__name__)


class TPLinkIPCCore:
    """TPLink IPC核心类."""

    def __init__(self, username: str, password: str, ip: str, port: int) -> None:
        """初始化TPLink IPC核心类."""
        self._username = None
        self._password = None
        self._base_url = None
        self._stok = None
        self.update(username, password, ip, port)

    def update(self, username: str, password: str, ip: str, port: int) -> None:
        """更新TPLink IPC核心类."""
        self._username = username
        self._password = password
        self._base_url = f"http://{ip}:{port}"
        self._stok = None

    async def post_data(self, data, times=1):
        """发送数据到TPLink IPC."""

        if times > 6:
            _LOGGER.error("Retry %s times", times - 1)

            return None

        # 目前观察下来stok的一段时间是固定的，所以这里不再每次都获取
        if not self._stok:
            await self.update_stok()

        try:
            data = await post_data(
                self._base_url,
                data,
                self._stok,
            )

            # 如果stok过期，重新获取stok
            if data["error_code"] == -40401:
                self._stok = None   
                _LOGGER.error("stok expired, retry %s times", times)
                return await self.post_data(data, times + 1)

            # 如果40210错误，重新发送数据
            if data["error_code"] == -40210:
                _LOGGER.error("Failed to post data: %s", data)
                return await self.post_data(data, times + 1)

            # 如果有错误，打印错误信息
            if data["error_code"] != 0:
                _LOGGER.error("Failed to post data: %s", data)
            else:
                return data
        except requests.exceptions.RequestException as e:
            _LOGGER.error("Failed to post data: %s", e)

    async def update_stok(self):
        """更新stok."""
        self._stok = await get_stok(self._base_url, self._username, self._password)


def tp_encrypt(password):
    """Encrypt the password using a custom algorithm."""
    a = "RDpbLfCPsJZ7fiv"
    c = "yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW "
    b = password
    e = ""
    f, g, h, k, var_l = 187, 187, 187, 187, 187
    n = 187
    g = len(a)
    h = len(b)
    k = len(c)
    if g > h:
        f = g
    else:
        f = h
    for p in list(range(f)):
        n = var_l = 187
        if p >= g:
            n = ord(b[p])
        elif p >= h:
            var_l = ord(a[p])
        else:
            var_l = ord(a[p])
            n = ord(b[p])
        e += c[(var_l ^ n) % k]
    return e


def convert_rsa_key(s):
    """Convert the RSA key from base."""
    # b_str = base64.b64decode(s)
    # if len(b_str) < 162:
    #     return False
    # hex_str = b_str.hex()
    # m_start = 29 * 2
    # e_start = 159 * 2
    # m_len = 128 * 2
    # e_len = 3 * 2
    # modulus = hex_str[m_start:m_start + m_len]
    # exponent = hex_str[e_start:e_start + e_len]
    # return modulus, exponent

    b_str = base64.b64decode(s)
    public_key = PublicKeyInfo.load(b_str)["public_key"].parsed
    return binascii.hexlify(public_key["modulus"].contents), binascii.hexlify(
        public_key["public_exponent"].contents
    )


def rsa_encrypt(string, pubkey):
    """Encrypt the string using the RSA public key."""
    key = convert_rsa_key(pubkey)
    modulus = int(key[0], 16)
    exponent = int(key[1], 16)
    rsa_pubkey = rsa.PublicKey(modulus, exponent)
    crypto = rsa.encrypt(string.encode(), rsa_pubkey)
    return base64.b64encode(crypto)


async def get_stok(url, username, password):
    """Get the stok value."""
    _LOGGER.debug("--get rsa and nonce")
    j = await post_data(url, json.dumps({"method": "do", "login": {}}))
    key = unquote(j["data"]["key"])
    nonce = str(j["data"]["nonce"])
    _LOGGER.debug("rsa: %s", key)
    _LOGGER.debug("nonce: %s", nonce)

    _LOGGER.debug("--encrypt password by tp")
    tp_password = tp_encrypt(password)
    tp_password += ":" + nonce
    _LOGGER.debug("tp_password: %s", tp_password)

    _LOGGER.debug("--encrypt password by rsa")
    rsa_password = rsa_encrypt(tp_password, key)
    _LOGGER.debug("rsa_password: %s", rsa_password)

    d = {
        "method": "do",
        "login": {
            "username": username,
            "encrypt_type": "2",
            "password": rsa_password.decode(),
        },
    }
    _LOGGER.debug("--login")
    j = await post_data(url, json.dumps(d))
    return j["stok"]


async def post_data(base_url, data, stok=""):
    """Post data to the TPLink IPC."""
    url = base_url + (("/stok=" + stok + "/ds") if stok else "")
    _LOGGER.debug("post: %s data: %s", url, data)

    # headers = {
    #     "Content-Type": "application/json; charset=UTF-8",
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    #     "Accept": "application/json, text/javascript, */*; q=0.01",
    #     "X-Requested-With": "XMLHttpRequest",
    #     "Referer": base_url + "/",
    #     "Content-Length": str(len(data)),
    # }

    async with (
        aiohttp.ClientSession() as session,
        session.post(url, data=data) as response,
    ):
        _LOGGER.debug("response: %s %s", str(response.status), await response.text())
        return await response.json()
