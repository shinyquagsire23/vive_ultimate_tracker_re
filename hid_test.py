import hid
import struct
import numpy as np

VID_VIVE = 0x0bb4
PID_TRACKER = 0x06a3
PID_DONGLE = 0x0350

VID_VALVE = 0x28de
PID_VALVE_TRACKER = 0x2300
PID_VALVE_DONGLE = 0x2101

HID1_INTERFACE_NUM = 0
HID3_INTERFACE_NUM = 1

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

# WiFi 5GHz cmd ids
WIFI_CMD_INIT = 0x0
WIFI_CMD_ONOFF = 0x1
WIFI_CMD_UPDATE_SSID_APPEND = 0x2
WIFI_CMD_UPDATE_SSID_FULL = 0x3
WIFI_CMD_UPDATE_PW = 0x4
WIFI_CMD_UPDATE_FREQ = 0x5
WIFI_CMD_UPDATE_COUNTRY = 0x6
WIFI_CMD_UPDATE_SSID_PW = 0x7
WIFI_CMD_UPDATE_DEVICE_ID = 0x8
WIFI_CMD_REQ_HOST = 0x9
WIFI_CMD_REQ_CONNECT = 0xA
WIFI_CMD_REQ_DISCONNECT = 0xB
WIFI_CMD_CONNECTED = 0xC
WIFI_CMD_DISCONNECTED = 0xD
WIFI_CMD_QUIT = 0xE

# Internal LED thread
LED_CMD_INIT = 0x0
LED_CMD_SET_LED = 0x1

# RF cmds
RF_CMD_SET_CTL_HAPTIC = 0x0
RF_CMD_SET_CTL_POWERON = 0x1
RF_CMD_SET_CTL_POWEROFF = 0x2
RF_CMD_SET_CTL_REBOOT = 0x3
RF_CMD_SET_CTL_CAR_LED = 0x4
RF_CMD_SET_CTL_POWEROFF_CLEAR_PAIR_LIST = 0x5
RF_CMD_SET_FINGER_OUTPUT = 0x6
RF_CMD_SET_SILENT_CALIBRATION = 0x7
RF_CMD_SET_LPF = 0x8
RF_CMD_SET_HAND = 0x9
# ?
RF_CMD_SET_ROLE_ID = 0xB
RF_CMD_SET_FUSION_MODE = 0xC
RF_CMD_SET_EVENT_ON = 0xD
RF_CMD_SET_WAIT_START_IMU = 0xE
RF_CMD_QUIT = 0xF


device_list = hid.enumerate(VID_VIVE, PID_TRACKER)
print(device_list)

#Find the device with the particular usage you want
device_dict_hid1 = [device for device in device_list if device['interface_number'] == HID1_INTERFACE_NUM][0]
device_hid1 = hid.Device(path=device_dict_hid1['path'])

'''
device_dict_hid3 = [device for device in device_list if device['interface_number'] == HID3_INTERFACE_NUM][0]
device_hid3 = hid.Device(path=device_dict_hid3['path'])
'''

def hex_dump(b, prefix=""):
    p = prefix
    b = bytes(b)
    for i in range(0, len(b)):
        if i != 0 and i % 16 == 0:
            print (p)
            p = prefix
        p += ("%02x " % b[i])
    print (p)

def parse_response(data):
    unk, cmd_id, data_len, unk2 = struct.unpack("<BHBB", data[:5])
    #print(f"unk: {hex(unk)} cmd_id: {hex(cmd_id)} data_len: {hex(data_len)} unk2: {hex(unk2)} ")

    ret = data[5:5+data_len]
    return cmd_id, ret

def parse_rf_response(data):
    unk, cmd_id, data_len, unk2 = struct.unpack("<BBBH", data[:5])
    #print(f"unk: {hex(unk)} cmd_id: {hex(cmd_id)} data_len: {hex(data_len)} unk2: {hex(unk2)} ")

    ret = data[5:5+data_len-4]
    return cmd_id, ret

def parse_rf_response_2(data):
    cmd_id, data_len = struct.unpack("<BB", data[:2])
    #print(f"unk: {hex(unk)} cmd_id: {hex(cmd_id)} data_len: {hex(data_len)} unk2: {hex(unk2)} ")

    ret = data[2:2+data_len-2]
    return cmd_id, ret

def send_command(cmd_id, data=None):
    if data is None:
        data = []
    out = struct.pack("<HBB", cmd_id, len(data), 0)
    out += bytes(data)

    out += bytes([0x0] * (0x40 - len(out)))

    try:
        ret = device_hid1.send_feature_report(out)
        for i in range(0, 10):
            resp = device_hid1.get_feature_report(0, 0x40)
            #hex_dump(resp)
            cmd_ret, data_ret = parse_response(resp)
            #hex_dump(data_ret)
            if cmd_ret == cmd_id:
                return data_ret
    except:
        return bytes([])

    return bytes([])

def send_rf_command(cmd_id, data=None):
    if data is None:
        data = []
    out = struct.pack("<B", cmd_id)
    out += bytes(data)

    out += bytes([0x0] * (0x40 - len(out)))

    try:
        ret = device_hid1.send_feature_report(out)
        for i in range(0, 10):
            resp = device_hid1.get_feature_report(0, 0x40)
            hex_dump(resp)
            cmd_ret, data_ret = parse_rf_response(resp)
            hex_dump(data_ret)
            if cmd_ret == cmd_id:
                return data_ret
    except:
        return bytes([])

    return bytes([])

def send_haptic(nDuration, nFrequency, nAmplitude, identify):
    send_command(PACKET_SET_HAPTIC, struct.pack("<HHHH", nDuration, nFrequency, nAmplitude, identify))

def get_str_info(idx):
    return send_command(PACKET_GET_STR_INFO, [idx]).decode("utf-8")

def set_str_info(idx, val):
    return send_command(PACKET_SET_STR_INFO, struct.pack("<BS", idx, val))

def get_status():
    ret = send_command(PACKET_GET_STATUS)
    tracking_mode, power, batt, hmd_init, device_status_mask, btn = struct.unpack("<BBBBBL", ret)
    print(f"tracking_mode={tracking_mode}, power={power}, batt={batt}, hmd_init={hmd_init}, device_status_mask={hex(device_status_mask)}, btn={hex(btn)}")

def set_tracking_mode(mode):
    send_command(PACKET_SET_TRACKING_MODE, [mode])

# ex: bootloader, fastboot, etc. I think.
def set_reboot(reason=""):
    send_command(PACKET_SET_REBOOT, reason.encode("utf-8"))

def get_property(key):
    send_command(PACKET_GET_PROPERTY, key.encode("utf-8"))

def parse_pose_data(data):
    if len(data) != 0x25:
        hex_dump(data)
        return
    idx, unk0, unk1, unk2, unk3, moves, pos, unk8, unk10 = struct.unpack("<BBLLL8s6s8sB", data)
    
    moves_arr = np.frombuffer(moves, dtype=np.float16, count=4)
    pos_arr = np.frombuffer(pos, dtype=np.float16, count=3)
    unk8_arr = np.frombuffer(unk8, dtype=np.float16, count=4)
    print(hex(idx), unk0, unk1, unk2, unk3, "moves:", moves_arr, "pos?:", pos_arr, "unk?:", unk8_arr, unk10)

def parse_incoming():
    resp = device_hid1.read(0x400)
    if len(resp) <= 0:
        return
    unk0, pkt_idx, mask, hmd_us, hdcc_status0, hdcc_status1, ack_in_queue, device_status, unk3 = struct.unpack("<BHLQBBBL17s", resp[:0x27])
    #hex_dump(resp)
    print(unk0, pkt_idx, hex(mask), hmd_us, hex(hdcc_status0), hex(hdcc_status1), ack_in_queue, hex(device_status), unk3)

    for i in range(0, 7):
        pose_len = resp[0x27 + (0x61*i)]
        pose_data = resp[0x28 + (0x61*i) : 0x28 + (0x61*i) + pose_len]
        pose_timestamp, = struct.unpack("<Q", resp[0x27 + (0x61*i) + 0x59 : 0x27 + (0x61*i) + 0x59 + 0x8])
        if pose_len:
            print("Pose data", i, "len", hex(pose_len), "ts", pose_timestamp)
            #hex_dump(pose_data)
            parse_pose_data(pose_data)
    netsync_str = "netsync: "
    for i in range(0, 7):
        a,b = struct.unpack("<QQ", resp[0x2ce+(i*0x10):0x2ce+(i*0x10)+0x10])
        netsync_str += f"({a},{b}) "
    print(netsync_str)
    print("")
    print("")

# 1=gyro, 2=body tracking(?), 3=body?
def set_power_pcvr(mode):
    send_command(PACKET_SET_POWER_PCVR, [mode])

def get_ack():
    hex_dump(send_command(PACKET_GET_ACK))

watchdog_delay = 0
def kick_watchdog():
    global watchdog_delay
    watchdog_delay += 1
    if watchdog_delay < 1000:
        return
    send_command(PACKET_SET_WATCHDOG_KICK)
    watchdog_delay = 0

# default 3?
def set_camera_policy(val):
    send_command(PACKET_SET_CAMERA_POLICY, [val])

# default 3?
def set_camera_fps(val):
    send_command(PACKET_SET_CAMERA_FPS, [val])

#send_haptic(1,2,3,4)
#set_tracking_mode(1)
#get_status()
#set_reboot()

#print(get_str_info(8))

#get_property("ro.build.fingerprint")


set_camera_policy(3)
set_camera_fps(60)

# Seems to get packets flowing?
set_power_pcvr(1)
#for i in range(0, 1000):
#while True:
#    parse_incoming()
#    kick_watchdog()
    #get_ack()
