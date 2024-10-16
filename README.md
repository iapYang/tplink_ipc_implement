# tplink_ipc_implement
本插件提供tplink摄像头除onvif外其它功能接入HomeAssistant，理论上支持所有TL-IPC设备。

> [!NOTE]
> 提交问题时请按Issues模版填写，未按模板填写问题会被忽略和关闭!!!

## 已支持功能
- Lens Mask(镜头遮蔽)

## 安装

方法1：下载并复制`custom_components/tplink_ipc_implement`文件夹到HomeAssistant根目录下的`custom_components`文件夹即可完成安装

方法2：已经安装了HACS，可以点击按钮快速安装 [![通过HACS添加集成](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=iapyang&repository=tplink_ipc_implement&category=integration)

## 配置

配置 > 设备与服务 >  集成 >  添加集成 > 搜索`TPLink IPC Implement`

或者点击: [![添加集成](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=tplink_ipc_implement)

## 调试
在`configuration.yaml`中加入以下配置来打开调试日志。

```yaml
logger:
  default: warn
  logs:
    custom_components.tplink_ipc_implement: debug
```

## 感谢
[水星 Mercury MIPC251C-4 网络摄像头 ONVIF 与 PTZ 云台控制](https://blog.xiazhiri.com/Mercury-MIPC251C-4-Reverse)