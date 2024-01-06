# FILE OPERATIONS
PACKET_FILE_READ = 0x10
PACKET_READ_FILEDATA = 0x11
PACKET_READ_FILEDATA_END = 0x12
PACKET_READ_FILEBIGDATA = 0x13
PACKET_WRITE_FILESIZE = 0x16
PACKET_WRITE_FILEDATA = 0x17
PACKET_FILE_WRITE = 0x18
PACKET_FILE_DELETE = 0x19

# ACCESSORY B4
PACKET_ACCESSORY_B4 = 0xab4

# INFO/STATUS
PACKET_GET_STR_INFO = 0xa001
PACKET_GET_STATUS = 0xa002
PACKET_SET_TRACKING_MODE =  0xa003
PACKET_SET_REBOOT =  0xa004
PACKET_SET_STR_INFO = 0xa005

# CAMERA
PACKET_SET_POWER_OCVR = 0xa101
PACKET_SET_POWER_PCVR = 0xa102
PACKET_SET_POWER_EYVR = 0xa103
#?
PACKET_SET_CAMERA_FPS = 0xa105
PACKET_SET_CAMERA_POLICY = 0xa106

# ??
PACKET_SET_USER_TIME = 0xa111
PACKET_SET_OT_STATUS = 0xa112
PACKET_GET_ACK = 0xa113
PACKET_SET_PLAYER_STR = 0xa114
PACKET_SET_HAPTIC = 0xa115
PACKET_SET_ACK = 0xa116

PACKET_SET_WATCHDOG_KICK = 0xa121
PACKET_SET_FOTA_BY_PC = 0xa122

# WIFI
PACKET_SET_WIFI_SSID_PW = 0xa151
PACKET_SET_WIFI_FREQ = 0xa152
PACKET_SET_WIFI_SSID = 0xa153
PACKET_SET_WIFI_PW = 0xa154
PACKET_SET_WIFI_COUNTRY = 0xa155
PACKET_GET_WIFI_HOST_INFO = 0xa156
PACKET_SET_WIFI_ONLY_MODE = 0xa157
PACKET_GET_WIFI_ONLY_MODE = 0xa158

# FACE TRACKING?
PACKET_SET_FT_LOCK = 0xa171
PACKET_SET_FT_UNLOCK = 0xa172
PACKET_SET_FT_FAIL = 0xa173

# MISC/FACTORY
PACKET_GET_PROPERTY = 0xa201
PACKET_SET_PROPERTY = 0xa202

PACKET_SET_FACTORY = 0xafff