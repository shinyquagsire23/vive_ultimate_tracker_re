
#
# ACK CMDs
#
# Wifi is limited to those starting with: P, FE?
ACK_CATEGORY_CALIB_1 = "C"
ACK_CATEGORY_CALIB_2 = "c"
ACK_CATEGORY_DEVICE_INFO = "N"
ACK_CATEGORY_PLAYER = "P" # Lambda (SLAM) related cmds

# ACK_CATEGORY_DEVICE_INFO
ACK_ANA = "ANA" # TODO, "OT1"? recv'd from tracker on connect (NANA?)
ACK_DEVICE_SN = "ADS" # recv'd from tracker on connect (NADS?)
ACK_SHIP_SN = "ASS" # recv'd from tracker on connect (NASS?)
ACK_SKU_ID = "ASI" # recv'd from tracker on connect (NASI?)
ACK_PCB_ID = "API" # recv'd from tracker on connect (NAPI?)
ACK_VERSION = "AV1" # recv'd from tracker on connect (NAV?)
ACK_VERSION_ALT = "Av1" # not actually sent
ACK_AZZ = "AZZ" # NAZZ? no data.
ACK_AGN = "AGN" # NAGN? 0,1,0
ACK_ARI = "ARI" # NARI?
ACK_AGN = "AGN" # NAGN?

ACK_LAMBDA_PROPERTY = "LP" # identical to AGN? 0,1,0 -- trans_setup, normalmode, 3rdhost. Can also be sent to check status.
ACK_LAMBDA_STATUS = "LS"

ACK_START_FOTA = "AFM"
ACK_CAMERA_FPS = "ACF"
ACK_CAMERA_POLICY = "ACP"
ACK_TRACKING_MODE = "ATM"
ACK_TRACKING_HOST = "ATH"
ACK_WIFI_HOST = "AWH"
ACK_TIME_SET = "ATS" # SetUserTime, calls clock_settime in seconds
ACK_ROLE_ID = "ARI"
ACK_GET_INFO = "AGI" # complicated for some reason, takes a list of ints, fusionmode related
ACK_END_MAP = "ALE"
ACK_NEW_ID = "ANI" # sets DeviceID, WiFi related?
ACK_ATW = "ATW" # enables acceleration data?

ACK_POWER_OFF_CLEAR_PAIRING_LIST = "APC"
ACK_POWER_OFF = "APF"
ACK_STANDBY = "APS"
ACK_RESET = "APR"

ACK_WIFI_SSID_PASS = "WS"
ACK_WIFI_SSID_FULL = "Ws"
ACK_WIFI_IP = "WI"
ACK_WIFI_IP_2 = "Wi"
ACK_WIFI_CONNECT = "WC"
ACK_WIFI_COUNTRY = "Wc"
ACK_WIFI_FREQ = "Wf"
ACK_WIFI_PW = "Wp"
ACK_WIFI_SSID_APPEND = "Wt"
ACK_WIFI_ERROR = "WE"
ACK_WIFI_HOST_SSID = "WH"

ACK_FT_KEEPALIVE = "FK"
ACK_FW = "FW" # TODO
ACK_FILE_DOWNLOAD = "FD"

# ACK_CATEGORY_PLAYER
ACK_LAMBDA_SET_STATUS = "P61:"
ACK_LAMBDA_ASK_STATUS = "P63:"
ACK_LAMBDA_COMMAND = "P64:"
ACK_LAMBDA_MESSAGE = "P82:" # PR?

LAMBDA_GET_STATUS = 61

LAMBDA_CMD_ASK_ED = 0
LAMBDA_CMD_ASK_MAP = 1
LAMBDA_CMD_ASK_KEYFRAME_SYNC = 2
LAMBDA_CMD_RESET_MAP = 3

# P61:0,1

ACK_ERROR_CODE = "DEC" # DEC?
ACK_NA = "NA" # resends device info?
ACK_MAP_STATUS = "MS"

ERROR_NO_CAMERA = 1100
ERROR_CAMERA_SSR_1 = 1121
ERROR_CAMERA_SSR_2 = 1122
ERROR_NO_IMU = 1200
ERROR_NO_POSE = 1300

# ACK_LAMBDA_MESSAGE
LAMBDA_MESSAGE_ERROR = 0
LAMBDA_MESSAGE_UPDATE_MAP_UUID = 1