import logging
import base64
import json
from urllib.parse import unquote

import requests
import rsa
from asn1crypto.keys import PublicKeyInfo
import binascii
import aiohttp

_LOGGER = logging.getLogger(__name__)


class TplinkIpcCore:
    def __init__(self, username: str, password: str, ip: str, port: int):
        self._username = username
        self._password = password
        self._base_url = f"http://{ip}:{port}"

    async def post_data(self, data):
        """发送数据到TP-Link IPC."""
        try:
            await post_data(
                self._base_url,
                data,
                await get_stok(self._base_url, self._username, self._password),
            )
            _LOGGER.debug("Data posted successfully")
        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"Failed to post data: {e}")


def tp_encrypt(password):
    a = "RDpbLfCPsJZ7fiv"
    c = "yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW "
    b = password
    e = ""
    f, g, h, k, l = 187, 187, 187, 187, 187
    n = 187
    g = len(a)
    h = len(b)
    k = len(c)
    if g > h:
        f = g
    else:
        f = h
    for p in list(range(0, f)):
        n = l = 187
        if p >= g:
            n = ord(b[p])
        else:
            if p >= h:
                l = ord(a[p])
            else:
                l = ord(a[p])
                n = ord(b[p])
        e += c[(l ^ n) % k]
    return e


def convert_rsa_key(s):
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
    key = convert_rsa_key(pubkey)
    modulus = int(key[0], 16)
    exponent = int(key[1], 16)
    rsa_pubkey = rsa.PublicKey(modulus, exponent)
    crypto = rsa.encrypt(string.encode(), rsa_pubkey)
    return base64.b64encode(crypto)


async def get_stok(url, username, password):
    print("-get rsa and nonce")
    j = await post_data(url, json.dumps({"method": "do", "login": {}}))
    key = unquote(j["data"]["key"])
    nonce = str(j["data"]["nonce"])
    print("rsa: ", key)
    print("nonce: ", nonce)

    print("--encrypt password by tp")
    tp_password = tp_encrypt(password)
    tp_password += ":" + nonce
    print("tp_password: ", tp_password)

    print("--encrypt password by rsa")
    rsa_password = rsa_encrypt(tp_password, key)
    print("rsa_password: ", rsa_password)

    d = {
        "method": "do",
        "login": {
            "username": username,
            "encrypt_type": "2",
            "password": rsa_password.decode(),
        },
    }
    print("--login")
    j = await post_data(url, json.dumps(d))
    stok = j["stok"]
    return stok


async def post_data(base_url, data, stok=""):
    url = base_url + (("/stok=" + stok + "/ds") if stok else "")
    print("post: ", url, " data: ", data)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            print("response: ", str(response.status), " ", await response.text())
            return await response.json()
