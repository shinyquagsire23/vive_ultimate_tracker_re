# Work state enum, set by HORUS_CMD_POWER
WS_STANDBY = 0x0
WS_CONNECTING = 0x1
WS_REPAIRING = 0x2
WS_CONNECTED = 0x3
WS_TRACKING = 0x4
WS_RECOVERY = 0x5
WS_REBOOT = 0x6
WS_SHUTDOWN = 0x7
WS_OCVR = 0x8
WS_PCVR = 0x9
WS_EYVR = 0xa
WS_RESTART = 0xb

# Error returns
ERR_BUSY = 0x2
ERR_03 = 0x3
ERR_UNSUPPORTED = 0xEE

# 0xfa80832 - connected standby?
# 0xfa80804 - connected standby?
# 0xfc00804 - connected standby?
# 0x304 = disconnected, pairing info present
# 0x301 = connected once, disconnected?
# 0x1 = never connected
PAIRSTATE_1 = 0x0001
PAIRSTATE_2 = 0x0002

# SetStatus/GetStatus
HDCC_BATTERY = 0x0
HDCC_IS_CHARGING = 0x1
HDCC_POGO_PINS = 0x3
HDCC_DEVICE_ID = 0x4
HDCC_TRACKING_HOST = 0x5
HDCC_WIFI_HOST = 0x6
HDCC_7 = 0x7 # LED?
HDCC_FT_OVER_WIFI = 0x8
HDCC_ROLE_ID = 0xA
HDCC_WIFI_CONNECTED = 0xC
HDCC_HID_CONNECTED = 0xD
HDCC_E = 0xE # related to ROLE_ID? Sent on pairing.
HDCC_WIFI_ONLY_MODE = 0xF
HDCC_10 = 0x10 # pose related