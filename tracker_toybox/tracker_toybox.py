import hid
import struct
import numpy as np
import time

from enums_usb import *
from enums_horusd_hid import *
from enums_horusd_wifi import * # currently unused
from enums_horusd_misc import * # currently unused
from enums_horusd_status import *
from enums_horusd_rf_report import *
from enums_horusd_ack import *
from enums_horusd_dongle import *

# GLOBALS
calib_1 = ""
calib_2 = ""
device_macs = []
got_a_pair = False
num_paired = 0
device_hid1 = None
switch_tracking_once = True
map_once = True
poses_recvd = 0

pose_quat = [0.0, 0.0, 0.0, 1.0]
pose_pos = [0.0, 0.0, 0.0]
pose_time = 0

def current_milli_time():
    return round(time.time() * 1000)

def hex_dump(b, prefix=""):
    p = prefix
    b = bytes(b)
    for i in range(0, len(b)):
        if i != 0 and i % 16 == 0:
            print (p)
            p = prefix
        p += ("%02x " % b[i])
    print (p)

def mac_str(b):
    return hex(b[0])[2:] + ":" + hex(b[1])[2:] + ":" + hex(b[2])[2:] + ":" + hex(b[3])[2:] + ":" + hex(b[4])[2:] + ":" + hex(b[5])[2:] 

def do_u8_checksum(data):
    out = 0
    for i in range(0, len(data)):
        out ^= data[i]
    return out

def dongle_parse_response(data):
    err_ret, cmd_id, data_len, unk2 = struct.unpack("<BBBH", data[:5])
    #print(f"unk: {hex(unk)} cmd_id: {hex(cmd_id)} data_len: {hex(data_len)} unk2: {hex(unk2)} ")

    ret = data[5:5+data_len-4]
    return err_ret, cmd_id, ret

def dongle_parse_incoming(data):
    cmd_id, data_len, unk = struct.unpack("<BBH", data[:4])
    #print(f"unk: {hex(unk)} cmd_id: {hex(cmd_id)} data_len: {hex(data_len)} unk2: {hex(unk2)} ")

    ret = data[4:4+data_len-4]
    return cmd_id, ret

def dongle_parse_tracker_status(data):
    unk, data_len = struct.unpack("<BB", data[:2])
    #print(f"unk: {hex(unk)} data_len: {hex(data_len)}")
    hex_dump(data[:2])
    data = data[2:2+data_len]
    hex_dump(data[0:1])
    data = data[1:]
    pair_state = [0,0,0,0]
    a,b,c, pair_state[0],pair_state[1],pair_state[2],pair_state[3], h = struct.unpack("<HHBLLLLB", data)
    print(hex(a),hex(b),hex(c),hex(pair_state[0]),hex(pair_state[1]),hex(pair_state[2]),hex(pair_state[3]),hex(h))


def dongle_send_raw(data=None, pad=True):
    global device_hid1
    if data is None:
        data = []
    out = bytes(data)

    if pad:
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

def dongle_send_cmd(cmd_id, data=None):
    global device_hid1
    if data is None:
        data = []
    if type(data) is str:
        data = data.encode("utf-8")
    out = struct.pack("<BBB", 0, cmd_id, len(data)+2)
    out += bytes(data)

    out += bytes([0x0] * (0x41 - len(out)))

    #print(f"Sending idk:")
    #hex_dump(out)

    try:
        ret = device_hid1.send_feature_report(out)
        for i in range(0, 10):
            resp = device_hid1.get_feature_report(0, 0x40)
            #hex_dump(resp)
            err_ret, cmd_ret, data_ret = dongle_parse_response(resp)
            #hex_dump(data_ret)
            if err_ret:
                print(f"Got error response: {hex(err_ret)}")
            if cmd_ret == cmd_id:
                return data_ret
    except:
        return bytes([])

    return bytes([])

def dongle_send_F4(trackers, subcmd, data=None):
    if data is None:
        data = []
    if len(trackers) != 5:
        return bytes([])
    checksummed_data = bytes(trackers) + bytes([subcmd]) + bytes(data)
    out_data = bytes([do_u8_checksum(checksummed_data)]) + checksummed_data
    hex_dump(out_data)
    return dongle_send_cmd(DCMD_F4, out_data)

def parse_pose_data(data):
    global map_once, poses_recvd, switch_tracking_once, pose_pos, pose_quat, pose_time
    poses_recvd += 1

    if len(data) != 0x25:
        print("Weird pose data.")
        hex_dump(data)
        if switch_tracking_once and poses_recvd > 10:
            #dongle_send_ack_to_all(ACK_TRACKING_MODE + "1")
            switch_tracking_once = False
        return
    idx, unk0, pos, rot, acc, unk8, unk10 = struct.unpack("<BB12s8s6s8sB", data)
    
    pos_arr = np.frombuffer(pos, dtype=np.float32, count=3)
    rot_arr = np.frombuffer(rot, dtype=np.float16, count=4)
    acc_arr = np.frombuffer(acc, dtype=np.float16, count=3)
    unk8_arr = np.frombuffer(unk8, dtype=np.float16, count=4)
    print(hex(idx), hex(unk0), "pos:", pos_arr, "rot:", rot_arr, "acc?:", acc_arr, "unk?:", unk8_arr, unk10, "time_delta", current_milli_time() - pose_time)

    pose_quat = rot_arr
    pose_pos = pos_arr
    pose_time = current_milli_time()

    if map_once and poses_recvd > 1000:
        dongle_send_ack_to_all(ACK_END_MAP)
        map_once = False

def dongle_get_pos():
    global pose_pos
    return np.array(pose_pos)

def dongle_get_rot():
    global pose_quat
    return np.array(pose_quat)

def dongle_parse_tracker_incoming(resp):
    global calib_1, calib_2
    cmd_id, pkt_idx, device_addr, type_maybe, data_len = struct.unpack("<BH6sHB", resp[:0xC])
    #hex_dump(resp)
    print(hex(cmd_id), hex(pkt_idx), mac_str(device_addr), hex(type_maybe), "data_len:", hex(data_len))

    if type_maybe == 0x101:
        data_raw = resp[0xC:0xC+data_len]
        data = data_raw.decode("utf-8")
        if data[0:1] == ACK_CATEGORY_CALIB_1:
            data_real = data[1:]
            calib_1 += data_real
            print("   Got CALIB_1:", calib_1)
        elif data[0:1] == ACK_CATEGORY_CALIB_2:
            data_real = data[1:]
            calib_2 += data_real
            print("   Got CALIB_2:", calib_2)
        elif data[0:1] == ACK_CATEGORY_DEVICE_INFO:
            data_real = data[1:]
            print("   Got device info ACK:", data_real[:3], data_real[3:])
        elif data[0:2] == ACK_LP:
            data_real = data[2:]
            print("   Got LP ACK:", data_real)
        elif data[0:4] == ACK_ERROR_CODE:
            data_real = data[4:]
            print("   Got ERROR:", data_real)
        elif data[0:2] == ACK_MAP_STATUS:
            data_real = data[2:]
            print("   Got MAP_STATUS:", data_real)
            #dongle_send_ack_to_all(ACK_END_MAP)
        else:
            print("   Got ACK:", data, "(", data_raw, ")")
        print("")
        return
    elif type_maybe == 0x110:
        data = resp[0xC:0xC+data_len]
        parse_pose_data(data)
        return

    data = resp[0xC:0xC+data_len]
    data_id = data[0]
    data_real = data[1:]
    print("   data_id:", hex(data_id), "data:", data_real)

def dongle_get_PCBID():
    return dongle_send_cmd(DCMD_GET_CR_ID, [CR_ID_PCBID]).decode("utf-8")

def dongle_get_SKUID():
    return dongle_send_cmd(DCMD_GET_CR_ID, [CR_ID_SKUID]).decode("utf-8")

def dongle_get_SN():
    return dongle_send_cmd(DCMD_GET_CR_ID, [CR_ID_SN]).decode("utf-8")

def dongle_get_ShipSN():
    return dongle_send_cmd(DCMD_GET_CR_ID, [CR_ID_SHIP_SN]).decode("utf-8")

def dongle_get_CapFPC():
    return dongle_send_cmd(DCMD_GET_CR_ID, [CR_ID_CAP_FPC]).decode("utf-8")

def dongle_get_ROMVersion():
    return dongle_send_cmd(DCMD_QUERY_ROM_VERSION, [0x00]).decode("utf-8")

def dongle_send_ack_to(idx, ack):
    mac = [0x23, 0x30, 0x42, 0xB7, 0x82, 0xD3]
    mac[1] |= idx

    # TX_ACK_TO_MAC checks all MAC bytes,
    # TX_ACK_TO_PARTIAL_MAC checks the first 2
    preamble = struct.pack("<BBBBBBBBB", TX_ACK_TO_PARTIAL_MAC, mac[0],mac[1],mac[2],mac[3],mac[4],mac[5],0, 1)
    ack = struct.pack("<B", len(ack)) + ack.encode("utf-8")

    data = preamble + ack

    return dongle_send_cmd(DCMD_TX, data)

def dongle_send_ack_to_all(ack):
    for i in range(0, 5):
        dongle_send_ack_to(i, ack)

print(dongle_get_PCBID()) # RequestPCBID
print(dongle_get_SKUID()) # RequestSKUID
print(dongle_get_SN()) # RequestSN
print(dongle_get_ShipSN()) # RequestShipSN
print(dongle_get_CapFPC()) # RequestCapFPC
print(dongle_get_ROMVersion()) # QueryROMVersion

#print(dongle_send_cmd(0xEF, bytes([0x06]) + "800001FF".encode("utf-8"))) # Write PCB ID
#print(dongle_send_cmd(0xEF, bytes([0x07]) + "00059E00".encode("utf-8"))) # Write SKU ID
#print(dongle_send_cmd(0xEF, bytes([0x08]) + "43AD339B07725".encode("utf-8"))) # Write SN
#print(dongle_send_cmd(0xEF, bytes([0x09]) + "FA3983C06815".encode("utf-8"))) # Write Ship SN

# hex_dump(dongle_send_cmd(0x21, [0])) # bricked my dongle :(

# 0x1D = ReportRequestRFChangeBehavior?
bEnabled = 1
print(dongle_send_cmd(DCMD_REQUEST_RF_CHANGE_BEHAVIOR, struct.pack("<BBBBBBB", RF_BEHAVIOR_PAIR_DEVICE, bEnabled, 1, 1, 1, 0, 0))) # PairDevice
#print(dongle_send_cmd(DCMD_REQUEST_RF_CHANGE_BEHAVIOR, struct.pack("<BBBBBBB", RF_BEHAVIOR_RX_POWER_SAVING, bEnabled, 1, 0, 0, 0, 0))) # RxPowerSaving?
#print(dongle_send_cmd(DCMD_REQUEST_RF_CHANGE_BEHAVIOR, struct.pack("<BBBBBB", RF_BEHAVIOR_RESTART_RF, 1, 0, 0, 0, 0))) # Same as 1 w/ bEnabled
# 3 = SetLpf (7,8,9,10), not available
# what is 4?
#print(dongle_send_cmd(DCMD_REQUEST_RF_CHANGE_BEHAVIOR, struct.pack("<B", RF_BEHAVIOR_FACTORY_RESET))) # FactoryReset?
#print(dongle_send_cmd(DCMD_REQUEST_RF_CHANGE_BEHAVIOR, struct.pack("<BBBBBB", RF_BEHAVIOR_6, 1, 0, 0, 0, 0))) # ClearPairingInfo?

def do_usb_init():
    global device_hid1
    device_list = hid.enumerate(VID_VIVE, PID_DONGLE)
    print(device_list)

    #Find the device with the particular usage you want
    device_dict_hid1 = [device for device in device_list if device['interface_number'] == HID1_INTERFACE_NUM][0]
    device_hid1 = hid.Device(path=device_dict_hid1['path'])

def do_loop():
    global device_hid1, num_paired, device_macs, got_a_pair
    resp = device_hid1.read(0x400)
    if len(resp) <= 0:
        return
    #print("dump:")
    #hex_dump(resp)
    #print("parsed:")
    # 0x18 = paired event, gives the 
    if resp[0] == DRESP_PAIR_EVENT:
        num_paired += 1
        got_a_pair = True
        #print("dump:")
        #hex_dump(resp)
        cmd_ret, data_ret = dongle_parse_incoming(resp)
        hex_dump(data_ret)
        unk = data_ret[0]
        is_repair = data_ret[1] # 0x1, id?
        paired_mac = mac_str(data_ret[2:])
        if [data_ret[2:]] not in device_macs:
            device_macs += [data_ret[2:]]
        print(f"Paired {paired_mac}, {hex(unk)}, {hex(is_repair)}")
        print(device_macs)
        calib_1 = ""
        calib_2 = ""

        dongle_send_ack_to_all(ACK_TRACKING_MODE + "-1")
        dongle_send_ack_to_all(ACK_TRACKING_MODE + "22")
        #dongle_send_ack_to_all(ACK_TRACKING_HOST + "-1")
        #dongle_send_ack_to_all(ACK_ROLE_ID + "1")
        #dongle_send_ack_to_all(ACK_NEW_ID + "0")
        #dongle_send_ack_to_all(ACK_GET_INFO + "3,1")
    elif resp[0] == DRESP_TRACKER_RF_STATUS or resp[0] == DRESP_TRACKER_NEW_RF_STATUS or resp[0] == 0x29:
        print(f"dump for {hex(resp[0])}:")
        #hex_dump(resp)
        cmd_ret, data_ret = dongle_parse_incoming(resp)
        if resp[0] == DRESP_TRACKER_RF_STATUS or resp[0] == DRESP_TRACKER_NEW_RF_STATUS:
            dongle_parse_tracker_status(data_ret)
        else:
            hex_dump(data_ret)
    elif resp[0] == DRESP_TRACKER_INCOMING:
        dongle_parse_tracker_incoming(resp)
        #dongle_send_raw(bytes([0]) + resp)

        #hex_dump(dongle_send_cmd(DCMD_28, struct.pack("<BBBBBBBB", DCMD_28_SUBCMD_8, 1, 0, 0, 0, 0, 0x22, 0x3) + "APF".encode("utf-8")))
        #hex_dump(dongle_send_cmd(DCMD_28, struct.pack("<BBBBBB", DCMD_28_SUBCMD_9, 1, 0, 0, 0, 0)))

        #hex_dump(dongle_send_cmd(DCMD_98, struct.pack("<BB", 0x22, 0x3) + "APF".encode("utf-8"))) 
        #hex_dump(dongle_send_cmd(DCMD_99, struct.pack("<BB", 0x22, 0x3) + "APF".encode("utf-8"))) 

        # These commands feel sketchy...
        #hex_dump(dongle_send_F4([1,1,1,1,1], 0))
        #hex_dump(dongle_send_F4([1,1,1,1,1], 1, struct.pack("<BL", 0, 0)))

        
        #dongle_send_ack_to_all(ACK_TRACKING_MODE + "1")
        #dongle_send_ack_to_all("ATW")
    else:
        print("dump:")
        hex_dump(resp)

if __name__ == '__main__':
    do_usb_init()

    while True:
        do_loop()


# What USB-HID PCVR does internally, could be useful for BTLE?
'''
              send_horus_cmd(0,0); // HORUS_CMD_POWER 0
              send_horus_cmd(0xb,0xffff); // HORUS_CMD_UPDATE_DEVICE_ID
              send_horus_cmd(0xc,bVar9); // HORUS_CMD_SET_TRACKING_MODE
              if (command_ == 0xa101) { // ocvr
                uVar24 = 8;
              }
              else {
                uVar24 = 9;
              }
              idk_pcvr_mode(0,uVar24); // HORUS_CMD_POWER, 
'''