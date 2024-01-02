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

BT_CMD_INIT = 0x0
BT_CMD_ONOFF = 0x1
BT_CMD_REPAIR = 0x2
BT_CMD_RESTART = 0x3
BT_CMD_SEND_ACK = 0x4
BT_CMD_SEND_DATA = 0x5
BT_CMD_QUIT = 0x6

# Internal Horus CMD thread
HORUS_CMD_POWER = 0x0
HORUS_CMD_UVC = 0x1
HORUS_CMD_LED_STATUS_UPDATE = 0x2
HORUS_CMD_VRC_APPEAR = 0x3
HORUS_CMD_VRC_DISAPPEAR = 0x4
HORUS_CMD_VRC_POWEROFF = 0x5
HORUS_CMD_CAMERA_SSR = 0x6
HORUS_CMD_IMU_SSR = 0x7
HORUS_CMD_DO_FT = 0x8
HORUS_CMD_FT_APPEAR = 0x9
HORUS_CMD_FT_DISAPPEAR = 0xA
HORUS_CMD_UPDATE_DEVICE_ID = 0xB
HORUS_CMD_SET_TRACKING_MODE = 0xC

# Wait state enum
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

# maybe?
BT_CMD_ACK = 0xc9

# idk, "ack"s
ACK_WIFI_CONNECT = 0x43
ACK_SEND_WIFI_HOST_SSID = 0x48
ACK_SET_TRACKING_HOST_IP = 0x49
ACK_RECV_ACK = 0x50
ACK_SEND_WIFI_SSID = 0x74

# There is some level of abstraction between the RF dongle's HID and these commands,
# but these report IDs are still used in the responses.
# 0x0
RF_REPORT_HID_CMD = 0x01
# 0x02
RF_REPORT_RECENTLY_CMD_DEBUG_CMD = 0x03
RF_REPORT_ACTR_STATUS = 0x4
# 0x5 .. 0xF
RF_REPORT_FLAG_OP_A = 0x10 # FW_INFO?
RF_REPORT_FLAG_OP_B = 0x11 # GG_FLAG?
RF_REPORT_NEW_CR_FLAGS = 0x12
RF_REPORT_RATE = 0x13
RF_REPORT_BATTERY_LEVEL = 0x14
RF_REPORT_MCU_VERSION = 0x15
RF_REPORT_RF_IDS = 0x16
RF_REPORT_CHANGE_BEHAVIOR = 0x17 # handleReportRequestRFChangeBehavior
RF_REPORT_RF_VERSION = 0x18
RF_REPORT_RF_DETAIL_STATUS = 0x19
RF_REPORT_RF_STATUS = 0x1A
RF_REPORT_FINISH_COMMAND_MODE = 0x1B # rf_spi_gotResult
# 0x1C, 0x1D, 0x1E
RF_REPORT_RF_REBOOT = 0x1F
# 0x20 .. 0x2F
RF_REPORT_FOTA_INIT = 0x30
RF_REPORT_FOTA_MODE_SWITCH = 0x31
RF_REPORT_FOTA_DEINIT = 0x32
RF_REPORT_FOTA_WRITE_FW = 0x33
RF_REPORT_FOTA_MARK_TARGET = 0x34
# 0x35 .. 0x3F
RF_REPORT_FWU_INIT = 0x40
RF_REPORT_FWU_ERASE = 0x43
RF_REPORT_FWU_WRITE = 0x44
RF_REPORT_FWU_COMPUTE_CRC = 0x45
RF_REPORT_FWU_GET_CRC = 0x46
RF_REPORT_FWU_SIGN = 0x48
# 0x49 .. 0x4F
RF_REPORT_RF_MODE_OP = 0x50
RF_REPORT_WRITE_RF = 0x51
# 0x52 .. 0x5F
RF_REPORT_WATCHDOG_TEST = 0x68
RF_REPORT_BATTERY_OP = 0x6A
RF_REPORT_USB_REPAIR = 0x6E
RF_REPORT_CALIB_OP = 0x6F


# Known valid dongle commands:
# 0x18 -> RF_REPORT_RF_VERSION, [0]->[0,0,0], [1]->[0,0], [2]->[2,0,0,0,...], [3]->[3], [4]->[4]
# 0x1A -> GetFusionMode, GetRoleId?
# 0x1D -> RF_REPORT_CHANGE_BEHAVIOR
# 0x1E -> gets RF_REPORT_CHANGE_BEHAVIOR w/o changing anything
# 0x21 -> RF_REPORT_RF_MODE_OP?
# 0x26 -> ??, returns 0x40 00s
# 0x27 -> RF_REPORT_RF_IDS, "Proprietary" in string
# 0x98 -> ??
# 0x99 -> ??
# 0x9A -> ??
# 0x9E -> ??
# 0x9F -> ?? always returns 0x10 00s
# 0xEB -> Reboot
# 0xEF -> ??
# 0xF0 -> a lot of ID stuff
# 0xF4 -> ?
# 0xFA -> used in DisableCharging?

'''
from: libftm_lib_rfcmd_ble.so

cmd_read_battery_level: 02 14 02 00/01 00
cmd_read_ids: 02 16 02 xx xx
read_version: 02 18 00
cmd_rf_status: 02 1a 00
'''

device_list = hid.enumerate(VID_VIVE, PID_DONGLE)
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
    err_ret, cmd_id, data_len, unk2 = struct.unpack("<BBBH", data[:5])
    #print(f"unk: {hex(unk)} cmd_id: {hex(cmd_id)} data_len: {hex(data_len)} unk2: {hex(unk2)} ")

    ret = data[5:5+data_len-4]
    return err_ret, cmd_id, ret

def parse_rf_incoming(data):
    cmd_id, data_len, unk = struct.unpack("<BBH", data[:4])
    #print(f"unk: {hex(unk)} cmd_id: {hex(cmd_id)} data_len: {hex(data_len)} unk2: {hex(unk2)} ")

    ret = data[4:4+data_len-4]
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


def send_raw(data=None):
    if data is None:
        data = []
    out = bytes(data)

    out += bytes([0x0] * (0x40 - len(out)))
    #print("Sending raw:")
    #hex_dump(out)

    try:
        ret = device_hid1.send_feature_report(out)

        resp = device_hid1.get_feature_report(0, 0x40)
        #hex_dump(resp)
            
        return resp
    except:
        return bytes([])

    return bytes([])

def send_rf_command(cmd_id, data=None):
    if data is None:
        data = []
    out = struct.pack("<BB", cmd_id, len(data)+2)
    out += bytes(data)

    out += bytes([0x0] * (0x40 - len(out)))

    try:
        ret = device_hid1.send_feature_report(out)
        for i in range(0, 10):
            resp = device_hid1.get_feature_report(0, 0x40)
            #hex_dump(resp)
            err_ret, cmd_ret, data_ret = parse_rf_response(resp)
            hex_dump(data_ret)
            if err_ret:
                print(f"Got error response: {hex(err_ret)}")
            if cmd_ret == cmd_id:
                return data_ret
    except:
        return bytes([])

    return bytes([])

def send_rf_command_to_id(to_id, cmd_id, data=None, do_read=True):
    if data is None:
        data = []
    out = struct.pack("<BBB", 0, cmd_id, len(data)+4)
    out += bytes(data)
    out += struct.pack("<BB", to_id ^ 1, to_id & 1)

    out += bytes([0x0] * (0x40 - len(out)))
    print(f"Sending to id {to_id}:")
    hex_dump(out)


    try:
        ret = device_hid1.send_feature_report(out)
        if not do_read:
            return bytes([])
        for i in range(0, 10):
            resp = device_hid1.get_feature_report(0, 0x40)
            if resp == out:
                continue
            hex_dump(resp[:5])
            err_ret, cmd_ret, data_ret = parse_rf_response(resp)
            hex_dump(data_ret)
            if err_ret:
                print(f"Got error response: {hex(err_ret)}")
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

def mac_str(b):
    return hex(b[0])[2:] + ":" + hex(b[1])[2:] + ":" + hex(b[2])[2:] + ":" + hex(b[3])[2:] + ":" + hex(b[4])[2:] + ":" + hex(b[5])[2:] 

def parse_incoming(resp):
    cmd_id, pkt_idx, device_addr, unk3, data_len = struct.unpack("<BH6sHB", resp[:0xC])
    #hex_dump(resp)
    print(hex(cmd_id), hex(pkt_idx), mac_str(device_addr), hex(unk3), "data_len:", hex(data_len))

    data = resp[0xC:0xC+data_len]
    data_id = data[0]
    data_real = data[1:]
    #hex_dump(data)
    print("data_id:", hex(data_id), "data:", data_real)

    '''
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
    '''

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

'''
set_camera_policy(3)
set_camera_fps(60)

# Seems to get packets flowing?
set_power_pcvr(1)
#for i in range(0, 1000):
while True:
    parse_incoming()
    kick_watchdog()
    #get_ack()
'''



#ret = device_hid1.send_feature_report(bytes([0xFF]) + bytes([0xFF]*0x3F))

#ret = device_hid1.send_feature_report(bytes([0xF0, 0x03, 0x06]) + bytes([0x00]*0x3F))


#print(send_rf_command(0x1A, struct.pack("<BBL", 1, 0, mode))) # SetFusionMode, len is +1?
print(send_rf_command(0x1A, [0x01, 0x01])) # GetFusionMode
#print(send_rf_command(0x1A, struct.pack("<BBL", 2, 0, role_id))) # SetRoleId, len is +1?
print(send_rf_command(0x1A, [0x02, 0x01])) # GetRoleId

print(send_rf_command(0xF0, [0x06])) # RequestPCBID
print(send_rf_command(0xF0, [0x07])) # RequestSKUID
print(send_rf_command(0xF0, [0x08])) # RequestSN
print(send_rf_command(0xF0, [0x09])) # RequestShipSN
print(send_rf_command(0xF0, [0x11])) # RequestCapFPC
print(send_rf_command(0xFF, [0x00])) # QueryROMVersion
print(send_rf_command(0xA4, [0x05, 0x0])) # RequestCap1
print(send_rf_command(0xA4, [0x05, 0x1])) # RequestCap2

#print(send_rf_command_to_id(0, 0x28, struct.pack("<BBLHBB", 3, 0, 0x10000, 0, which, 0))) #SetHand
#print(send_rf_command_to_id(0, 0x28, struct.pack("<BBHHH", 3, 0, nDutyCycle, nOnOff, 0))) #CarIrLed
nFrequency = 1
nDuration = 2
nAmplitude = 3
#print(send_rf_command_to_id(0, 0x28, struct.pack("<BBHHHH", 3, 1, nFrequency, nDuration, nAmplitude, 0))) #RfHaptic
#print(send_rf_command_to_id(0, 0x28, struct.pack("<BBHHHH", 3, 1, nFrequency, nDuration, nAmplitude, 1))) #IdenfityController
#print(send_rf_command_to_id(0, 0x28, struct.pack("<BBB", 3, 5, val))) #SetFingerOutput (3,4,5,6)
#print(send_rf_command_to_id(0, 0x28, struct.pack("<BBB", 3, 5, val))) #SilenceCalibration (1,2)
#print(send_rf_command_to_id(0, 0x28, struct.pack("<BBB", 3, 3))) #PowerOffCr standby=0
#print(send_rf_command_to_id(0, 0x28, struct.pack("<BBB", 3, 6))) #PowerOffCr standby=1


# 0x1D = ReportRequestRFChangeBehavior?
bEnabled = 1
print(send_rf_command_to_id(0, 0x1D, struct.pack("<BB", 0, bEnabled))) # PairDevice
#print(send_rf_command_to_id(0, 0x1D, struct.pack("<BB", 1, 1))) # RxPowerSaving
#print(send_rf_command_to_id(0, 0x1D, struct.pack("<BB", 2, 0))) # RxPowerSaving


#for i in range(0, 0x100):
#send_rf_command_to_id(1, 0x1D, [4, 1]) # RfChangeBehavior resp?


#send_rf_command_to_id(0, 0x21, []) # rf mode op?


#print(send_rf_command_to_id(0, 0xEB)) # reboots dongle


'''
for i in range(0, 256):
    if i == 0xEB: continue
    
    #resp = send_raw([0x00, i, 0x05, 0x0, 0x01] + [0x0] * (0x40-4))
    #if resp[2] != 0x5:
    #    print(f"resp for {hex(i)}:")
    #    hex_dump(resp)
    
    
    print(send_rf_command_to_id(0, i, [0]))
'''

#print(send_rf_command_to_id(0, 0x1D, struct.pack("<BB", 1, val))) # RxPowerSaving
#print(send_rf_command_to_id(0, 0x1D, struct.pack("<BB", 2, 0))) # RestartRf / hndl_restart_rx
#print(send_rf_command_to_id(0, 0x1D, struct.pack("<BBB", 3, 5, type))) # SetLpf (7,8,9,10)
#print(send_rf_command_to_id(0, 0x1D, struct.pack("<B", 5))) # hndl_factory_reset

#print(send_rf_command_to_id(0, 0xFA, [0x02, 0x6A, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x01, 0x00, 0xC4])) # DisableCharging

'''
for i in range(0, 10):
    print("dump:")
    resp = device_hid1.get_feature_report(0, 0x40)
    hex_dump(resp)
    print("parsed:")
    cmd_ret, data_ret = parse_rf_response(resp)
    hex_dump(data_ret)
'''

'''
for i in range(0, 0x100):
    print("dump feature report:")
    resp = device_hid1.get_feature_report(i, 0x1000)
    hex_dump(resp)
'''


# {"trackref_from_head":[-0.017001,0.010084,0.015520,0.000000,1.000000,0.000000,0.000000],"trackref_from_imu":[0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000]}

'''

02-16 20:12:21.140   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 01
02-16 20:12:21.140   478   620 D HDbt    : BT_CMD_SEND_ACK: C10084,0.015520,0.000000,1.000000,0.0, seq=02
02-16 20:12:21.148   478   620 D HDbt    : BT_CMD_SEND_ACK--
02-16 20:12:21.172   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 02
02-16 20:12:21.172   478   620 D HDbt    : BT_CMD_SEND_ACK: C00000,0.000000],"trackref_from_imu":, seq=03
02-16 20:12:21.180   478   620 D HDbt    : BT_CMD_SEND_ACK--
02-16 20:12:21.212   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 03
02-16 20:12:21.212   478   620 D HDbt    : BT_CMD_SEND_ACK: C[0.000000,0.000000,0.000000,0.000000, seq=04
02-16 20:12:21.220   478   620 D HDbt    : BT_CMD_SEND_ACK--
02-16 20:12:21.244   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 04
02-16 20:12:21.244   478   620 D HDbt    : BT_CMD_SEND_ACK: C,0.000000,0.000000,0.000000]}, seq=05
02-16 20:12:21.252   478   620 D HDbt    : BT_CMD_SEND_ACK--
02-16 20:12:21.276   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 05
02-16 20:12:21.276   478   620 D HDbt    : BT_CMD_SEND_ACK: c0,0,173,06DA2370, seq=06
02-16 20:12:21.284   478   620 D HDbt    : BT_CMD_SEND_ACK--
02-16 20:12:21.316   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 06
02-16 20:12:21.316   478   620 D HDbt    : BT_CMD_SEND_ACK: NANAOT1, seq=07
02-16 20:12:21.324   478   620 D HDbt    : BT_CMD_SEND_ACK--
02-16 20:12:21.348   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 07
02-16 20:12:21.348   478   620 D HDbt    : BT_CMD_SEND_ACK: NADS******B00053, seq=08
02-16 20:12:21.356   478   620 D HDbt    : BT_CMD_SEND_ACK--
02-16 20:12:21.380   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 08
02-16 20:12:21.380   478   620 D HDbt    : BT_CMD_SEND_ACK: NASS******B00053, seq=09
02-16 20:12:21.388   478   620 D HDbt    : BT_CMD_SEND_ACK--
02-16 20:12:21.420   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 09
02-16 20:12:21.420   478   620 D HDbt    : BT_CMD_SEND_ACK: NASI00059600, seq=0A
02-16 20:12:21.428   478   620 D HDbt    : BT_CMD_SEND_ACK--
02-16 20:12:21.452   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 0A
02-16 20:12:21.452   478   620 D HDbt    : BT_CMD_SEND_ACK: NAPI505001FF, seq=0B
02-16 20:12:21.460   478   620 D HDbt    : BT_CMD_SEND_ACK--
02-16 20:12:21.492   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 0B
02-16 20:12:21.492   478   620 D HDbt    : BT_CMD_SEND_ACK: NAV11.0.999.84, seq=0C
02-16 20:12:21.500   478   620 D HDbt    : BT_CMD_SEND_ACK--
02-16 20:12:21.524   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 0C
02-16 20:12:21.524   478   620 D HDbt    : BT_CMD_SEND_ACK: NARI0, seq=0D
02-16 20:12:21.532   478   620 D HDbt    : BT_CMD_SEND_ACK--
02-16 20:12:21.556   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 0D
02-16 20:12:21.556   478   620 D HDbt    : BT_CMD_SEND_ACK: NAGN0,1,0, seq=0E
02-16 20:12:21.564   478   620 D HDbt    : BT_CMD_SEND_ACK--
02-16 20:12:21.588   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 0E
02-16 20:12:21.588   478   620 D HDbt    : BT_CMD_SEND_ACK: LP0,1,0, seq=0F
02-16 20:12:21.596   478   620 D HDbt    : BT_CMD_SEND_ACK--
02-16 20:12:21.620   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 0F
02-16 20:12:21.620   478   620 D HDbt    : BT_CMD_SEND_ACK: NAZZ, seq=10
02-16 20:12:21.628   478   620 D HDbt    : BT_CMD_SEND_ACK--
02-16 20:12:21.652   478   621 D HDbt    : bt_thread: [RECV-0x22 0x01] detect send_ack complete: 10
02-16 20:12:25.331   478   620 D HDbt    : BT_CMD_SEND_DATA: len=2
'''

# CMD 0x1D crashes the dongle?

got_a_pair = False
num_paired = 0
idx = 0
while True:
    idx += 1
    if idx > 10 and got_a_pair and num_paired < 2:
        send_rf_command_to_id(1, 0x1D, struct.pack("<BB", 0, bEnabled)) # PairDevice
        idx = 0

    #print(send_rf_command_to_id(0, 0x28, struct.pack("<BBHHHH", 3, 1, nFrequency, nDuration, nAmplitude, 1))) #IdenfityController
    #print(send_rf_command_to_id(1, 0x28, struct.pack("<BBHHHH", 3, 1, nFrequency, nDuration, nAmplitude, 1))) #IdenfityController

    #print(send_rf_command_to_id(0, 0x9C, struct.pack("<B", 3))) #test
    #print(send_rf_command_to_id(1, 0x9C, struct.pack("<B", 3))) #test

    resp = device_hid1.read(0x400)
    if len(resp) <= 0:
        continue
    #print("dump:")
    #hex_dump(resp)
    #print("parsed:")
    # 0x18 = paired event, gives the 
    if resp[0] == 0x18:
        num_paired += 1
        got_a_pair = True
        #print("dump:")
        #hex_dump(resp)
        cmd_ret, data_ret = parse_rf_incoming(resp)
        hex_dump(data_ret)
        unk = data_ret[0]
        is_repair = data_ret[1] # 0x1, id?
        paired_mac = mac_str(data_ret[2:])
        print(f"Paired {paired_mac}")
    elif resp[0] == 0x1e or resp[0] == 0x1d or resp[0] == 0x29:
        print(f"dump for {hex(resp[0])}:")
        hex_dump(resp)
        cmd_ret, data_ret = parse_rf_incoming(resp)
        hex_dump(data_ret)
    elif resp[0] == 0x28:
        parse_incoming(resp)

        #print(send_rf_command_to_id(0, 0x28, struct.pack("<BB", 0, 0))) # RxPowerSaving
        #print(send_rf_command_to_id(0, 0x1D, struct.pack("<BB", 2, 0))) # RestartRf
        #print(send_rf_command_to_id(0, 0x28, struct.pack("<BB", 3, 3))) #PowerOffCr standby=0
        #print(send_rf_command(0xFA, [0x02, 0x6A, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x01, 0x00, 0xC4])) # DisableCharging
        #print(send_rf_command_to_id(0, 0x14, [])) #  read_battery_level
        #print(send_raw([0x02, 0x1A, 0x00]))
        #print(send_rf_command_to_id(0, 0x1E, []))
        #send_raw([0x02, 0x1D, 0x02, 0x1A, 0x00])

        #print(send_rf_command_to_id(0, 0xFA, [0x02, 0x6A, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x01, 0x00, 0xC4])) # DisableCharging

        #print(send_rf_command_to_id(0, 0x28, struct.pack("<BBHHHH", 3, 1, nFrequency, nDuration, nAmplitude, 0))) #RfHaptic

        for i in range(1, 256):
            #print(send_rf_command_to_id(0, 0x1D, struct.pack("<BB", i, bEnabled))) # PairDevice
            #print(send_rf_command_to_id(0, i))
            #print(send_rf_command_to_id(0, i, None, False))
            #print(send_rf_command_to_id(0, i, None, False)) #IdenfityController
            a='a'
    else:
        print("dump:")
        hex_dump(resp)

    
'''
00 1d 1d 00 00 02 17 16 01 00 03 00 00 04 03 00 
00 04 03 00 00 01 03 00 00 01 03 00 00 01 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 

'''

'''
  uStack_79[1] = 0x1d;
  uStack_79[2] = 6;
  uStack_79[3] = 2;
  uStack_79[4] = 0;
  uStack_79[5] = uStack_79[6] ^ 1;
  uStack_79[6] = (byte)param_1 & 1;
'''

'''
              idk_pcvr_mode(0,0); // HORUS_CMD_POWER 0
              idk_pcvr_mode(0xb,0xffff); // HORUS_CMD_UPDATE_DEVICE_ID
              idk_pcvr_mode(0xc,bVar9); // HORUS_CMD_SET_TRACKING_MODE
              if (command_ == 0xa101) { // ocvr
                uVar24 = 8;
              }
              else {
                uVar24 = 9;
              }
              idk_pcvr_mode(0,uVar24); // HORUS_CMD_POWER, 
'''