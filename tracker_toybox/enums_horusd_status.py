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


PAIRSTATE_1 = 0x0001
PAIRSTATE_2 = 0x0002
PAIRSTATE_4 = 0x0004
PAIR_STATE_PAIRED = 0x0008
PAIRSTATE_10 = 0x0010

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

TRACKING_MODE_NONE = -1 # checks persist.lambda.3rdhost
TRACKING_MODE_1 = 1 # gyro only? persist.lambda.3rdhost=0, persist.lambda.normalmode=1 persist.lambda.trans_setup=0
TRACKING_MODE_2 = 2 # body?
TRACKING_MODE_SLAM_CLIENT = 11 # gyro only? persist.lambda.3rdhost=0, persist.lambda.normalmode=0 # client?
TRACKING_MODE_21 = 21 # body tracking? persist.lambda.3rdhost
TRACKING_MODE_SLAM_HOST = 22 # SLAM persist.lambda.3rdhost=1, persist.lambda.normalmode=0
TRACKING_MODE_51 = 51 # SetUVCStatus?

# GET_STATUS
KEY_TRANSMISSION_READY = 0
KEY_RECEIVED_FIRST_FILE = 1
KEY_RECEIVED_HOST_ED = 2
KEY_RECEIVED_HOST_MAP = 3
KEY_CURRENT_MAP_ID = 4
KEY_MAP_STATE = 5
KEY_CURRENT_TRACKING_STATE = 6

_slam_key_strs = ["TRANSMISSION_READY", "RECEIVED_FIRST_FILE", "RECEIVED_HOST_ED", "RECEIVED_HOST_MAP", "CURRENT_MAP_ID", "MAP_STATE", "CURRENT_TRACKING_STATE"]

def slam_key_to_str(idx):
    return _slam_key_strs[idx]

# Commands
ASK_ED = 0
ASK_MAP = 1
KF_SYNC = 2
RESET_MAP = 3