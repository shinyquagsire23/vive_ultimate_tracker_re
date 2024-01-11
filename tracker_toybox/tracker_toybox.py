import hid
import struct
import numpy as np
import time
import json

from enums_usb import *
from enums_horusd_hid import *
from enums_horusd_wifi import * # currently unused
from enums_horusd_misc import * # currently unused
from enums_horusd_status import *
from enums_horusd_rf_report import *
from enums_horusd_ack import *
from enums_horusd_dongle import *

# Sometimes it will not track w/o:
# adb shell setprop persist.lambda.trans_setup 1
# adb shell setprop persist.lambda.normalmode 0 
# adb shell setprop persist.lambda.3rdhost 1 
# tracking_mode 1 seems to fuck up trans_setup?

# client trackers sometimes need:
# adb shell rm -rf /data/lambda/ 
# adb shell mkdir -p /data/lambda/

# adb shell cat /data/tracking_log/horusd.log.0
# adb shell cat /data/tracking_log/slam.log.1
# adb shell cat /data/tracking_log/slam.log.\* > test_slam_client.log 
# adb shell cat /data/tracking_log/slam.log.\* > test_slam_host.log 

# Doesn't work :(
# cp /data/property/persist.lambda.3rdhost /data/property/persist.tracking.mode.largescale
# rm /data/property/persist.tracking.mode.largescale

#Unpaired 23:31:fd:c2:7b:cd, 0x1
#Unpaired 23:30:42:b7:82:d3, 0x1
# Unpaired 23:32:fd:c2:7b:cd, 0x1

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

def mac_to_idx(b):
    return b[1] & 0xF

def do_u8_checksum(data):
    out = 0
    for i in range(0, len(data)):
        out ^= data[i]
    return out

class DongleHID:

    def __init__(self):
        self.calib_1 = ""
        self.calib_2 = ""
        self.device_macs = []
        self.got_a_pair = False
        self.num_paired = 0
        self.device_hid1 = None
        self.map_once = [True]*5
        self.poses_recvd = [0]*5
        self.slam_online = [False]*5
        self.current_host_id = -1
        self.tick_periodic = 0

        self.pose_quat = [[0.0, 0.0, 0.0, 1.0]] * 5
        self.pose_pos = [[0.0, 0.0, 0.0]] * 5
        self.pose_time = [0] * 5
        self.pair_state = [0,0,0,0,0]
        self.bump_map_once = [True]*5
        self.bump_map_once_2 = [True]*5

        self.host_ssid = ""
        self.host_passwd = ""
        self.host_freq = ""

        device_list = hid.enumerate(VID_VIVE, PID_DONGLE)
        print(device_list)

        # TODO better error handling
        device_dict_hid1 = [device for device in device_list if device['interface_number'] == HID1_INTERFACE_NUM][0]
        self.device_hid1 = hid.Device(path=device_dict_hid1['path'])

        print(self.get_PCBID()) # RequestPCBID
        print(self.get_SKUID()) # RequestSKUID
        print(self.get_SN()) # RequestSN
        print(self.get_ShipSN()) # RequestShipSN
        print(self.get_CapFPC()) # RequestCapFPC
        print(self.get_ROMVersion()) # QueryROMVersion

        #print(self.send_cmd(0xEF, bytes([0x06]) + "800001FF".encode("utf-8"))) # Write PCB ID
        #print(self.send_cmd(0xEF, bytes([0x07]) + "00059E00".encode("utf-8"))) # Write SKU ID
        #print(self.send_cmd(0xEF, bytes([0x08]) + "43AD339B07725".encode("utf-8"))) # Write SN
        #print(self.send_cmd(0xEF, bytes([0x09]) + "FA3983C06815".encode("utf-8"))) # Write Ship SN

        # hex_dump(self.send_cmd(0x21, [0])) # bricked my dongle :(

        # 0x1D = ReportRequestRFChangeBehavior?
        bEnabled = 1
        print(self.send_cmd(DCMD_REQUEST_RF_CHANGE_BEHAVIOR, struct.pack("<BBBBBBB", RF_BEHAVIOR_PAIR_DEVICE, bEnabled, 1, 1, 1, 0, 0))) # PairDevice
        #print(self.send_cmd(DCMD_REQUEST_RF_CHANGE_BEHAVIOR, struct.pack("<BBBBBBB", RF_BEHAVIOR_RX_POWER_SAVING, bEnabled, 1, 0, 0, 0, 0))) # RxPowerSaving?
        #print(self.send_cmd(DCMD_REQUEST_RF_CHANGE_BEHAVIOR, struct.pack("<BBBBBB", RF_BEHAVIOR_RESTART_RF, 1, 0, 0, 0, 0))) # Same as 1 w/ bEnabled
        # 3 = SetLpf (7,8,9,10), not available
        # what is 4?
        #print(self.send_cmd(DCMD_REQUEST_RF_CHANGE_BEHAVIOR, struct.pack("<B", RF_BEHAVIOR_FACTORY_RESET))) # FactoryReset?
        #print(self.send_cmd(DCMD_REQUEST_RF_CHANGE_BEHAVIOR, struct.pack("<BBBBBB", RF_BEHAVIOR_6, 1, 0, 0, 0, 0))) # ClearPairingInfo?

        with open('wifi_info.json', 'r') as f:
            self.wifi_info = json.load(f)

    def parse_response(self, data):
        err_ret, cmd_id, data_len, unk2 = struct.unpack("<BBBH", data[:5])
        #print(f"unk: {hex(unk)} cmd_id: {hex(cmd_id)} data_len: {hex(data_len)} unk2: {hex(unk2)} ")

        ret = data[5:5+data_len-4]
        return err_ret, cmd_id, ret

    def parse_incoming(self, data):
        cmd_id, data_len, unk = struct.unpack("<BBH", data[:4])
        #print(f"unk: {hex(unk)} cmd_id: {hex(cmd_id)} data_len: {hex(data_len)} unk2: {hex(unk2)} ")

        ret = data[4:4+data_len-4]
        return cmd_id, ret

    def parse_tracker_status(self, data):
        unk, data_len = struct.unpack("<BB", data[:2])
        #print(f"unk: {hex(unk)} data_len: {hex(data_len)}")
        hex_dump(data[:2])
        data = data[2:2+data_len]
        hex_dump(data[0:1])
        data = data[1:]
        pair_state = [0,0,0,0,0]
        unk, pair_state[0],pair_state[1],pair_state[2],pair_state[3],pair_state[4],  = struct.unpack("<HLLLLL", data)
        print(hex(unk),hex(pair_state[0]),hex(pair_state[1]),hex(pair_state[2]),hex(pair_state[3]),hex(pair_state[4]))

        self.pair_state = pair_state

        # Fallback for disconnects
        if self.current_host_id >= 0:
            if self.pair_state[self.current_host_id] & PAIR_STATE_PAIRED == 0:
                self.handle_disconnected(self.current_host_id)

        # pair state:
        # 0x4000003 - unpaired, pairing info present?
        # 0x1000003 - unpaired, pairing info not present?
        # 0x320fc008 - paired
        # 0x320ff808 - paired
        # 0x320fa808 - paired


    def send_raw(self, data=None, pad=True):
        if data is None:
            data = []
        out = bytes(data)

        if pad:
            out += bytes([0x0] * (0x40 - len(out)))
        #print("Sending raw:")
        #hex_dump(out)

        try:
            ret = self.device_hid1.send_feature_report(out)

            resp = self.device_hid1.get_feature_report(0, 0x40)
            #hex_dump(resp)
                
            return resp
        except:
            return bytes([])

        return bytes([])

    def send_cmd(self, cmd_id, data=None):
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
            ret = self.device_hid1.send_feature_report(out)
            for i in range(0, 10):
                resp = self.device_hid1.get_feature_report(0, 0x40)
                #hex_dump(resp)
                err_ret, cmd_ret, data_ret = self.parse_response(resp)
                #hex_dump(data_ret)
                if err_ret:
                    print(f"Got error response: {hex(err_ret)}")
                if cmd_ret == cmd_id:
                    return data_ret
        except:
            return bytes([])

        return bytes([])

    def send_F4(self, trackers, subcmd, data=None):
        if data is None:
            data = []
        if len(trackers) != 5:
            return bytes([])
        checksummed_data = bytes(trackers) + bytes([subcmd]) + bytes(data)
        out_data = bytes([do_u8_checksum(checksummed_data)]) + checksummed_data
        hex_dump(out_data)
        return self.send_cmd(DCMD_F4, out_data)

    def parse_pose_data(self, mac, data):
        self.poses_recvd[mac_to_idx(mac)] += 1

        if len(data) == 0x2:
            idx, btns = struct.unpack("<BB", data)
            print(f"({mac_str(mac)})", hex(idx), "btns:", hex(btns))
            return

        if len(data) != 0x25 and len(data) != 0x27:
            print("Weird pose data.", len(data))
            hex_dump(data)
            return
        idx, btns, pos, rot, acc, rot_vel, tracking_status = struct.unpack("<BB12s8s6s8sB", data[:0x25])
        
        # tracking_status = 2 => pose + rot
        # tracking_status = 3 => rot only
        # tracking_status = 4 => pose frozen (lost tracking), rots

        pos_arr = np.frombuffer(pos, dtype=np.float32, count=3)
        rot_arr = np.frombuffer(rot, dtype=np.float16, count=4)
        acc_arr = np.frombuffer(acc, dtype=np.float16, count=3)
        rot_vel_arr = np.frombuffer(rot_vel, dtype=np.float16, count=4)
        #print(f"({mac_str(mac)})", hex(idx), pose_status_to_str(tracking_status), "btns:", hex(btns), "pos:", pos_arr, "rot:", rot_arr, "acc:", acc_arr, "rot_vel:", rot_vel_arr, "time_delta", current_milli_time() - self.pose_time[mac_to_idx(mac)])

        self.pose_quat[mac_to_idx(mac)] = rot_arr
        self.pose_pos[mac_to_idx(mac)] = pos_arr
        self.pose_time[mac_to_idx(mac)] = current_milli_time()

        if self.map_once[mac_to_idx(mac)] and self.poses_recvd[mac_to_idx(mac)] > 1000:
            self.slam_online[mac_to_idx(mac)] = True
            #if self.current_host_id == mac_to_idx(mac):
            #    self.send_ack_to(mac_to_idx(mac), ACK_END_MAP)
            #self.send_ack_to_all(ACK_END_MAP)
            self.map_once[mac_to_idx(mac)] = False
            #self.send_ack_to(mac_to_idx(mac), ACK_LAMBDA_ASK_STATUS + "0")
            if self.current_host_id != mac_to_idx(mac):
                print("asdf")
                #self.send_ack_to(mac_to_idx(mac), ACK_LAMBDA_COMMAND + "3")
                #self.send_ack_to_all(ACK_LAMBDA_COMMAND + "1")

    def get_pos(self, idx=0):
        return np.array(self.pose_pos[idx])

    def get_rot(self, idx=0):
        return np.array(self.pose_quat[idx])

    def parse_tracker_incoming(self, resp):
        cmd_id, pkt_idx, device_addr, type_maybe, data_len = struct.unpack("<BH6sHB", resp[:0xC])
        #hex_dump(resp)
        #print(hex(cmd_id), hex(pkt_idx), mac_str(device_addr), hex(type_maybe), "data_len:", hex(data_len))

        #if self.slam_online[mac_to_idx(device_addr)]:
        #    self.send_ack_to(mac_to_idx(device_addr), "P61")

        if type_maybe == 0x101:
            data_raw = resp[0xC:0xC+data_len]
            data = data_raw.decode("utf-8")
            if data[0:1] == ACK_CATEGORY_CALIB_1:
                data_real = data[1:]
                self.calib_1 += data_real
                print(f"   Got CALIB_1 ({mac_str(device_addr)}):", self.calib_1)
            elif data[0:1] == ACK_CATEGORY_CALIB_2:
                data_real = data[1:]
                self.calib_2 += data_real
                print(f"   Got CALIB_2 ({mac_str(device_addr)}):", self.calib_2)
            elif data[0:1] == ACK_CATEGORY_DEVICE_INFO:
                data_real = data[1:]
                print(f"   Got device info ACK ({mac_str(device_addr)}):", data_real[:3])
            elif data[0:1] == ACK_CATEGORY_PLAYER:
                data_real = data[1:]
                parts = data_real.split(":")
                idx = int(parts[0])
                args = parts[1]
                

                if idx == LAMBDA_PROP_GET_STATUS:
                    args = [int(s) for s in args.split(",")]
                    key_id = args[0]
                    state = args[1]
                    addendum = ""

                    if key_id == KEY_RECEIVED_HOST_ED:
                        #if state == 0:
                        #    self.send_ack_to(mac_to_idx(device_addr), ACK_LAMBDA_COMMAND + f"{ASK_ED}")
                        pass
                    elif key_id == KEY_RECEIVED_HOST_MAP:
                        if state == 0:
                            #self.send_ack_to(mac_to_idx(device_addr), ACK_LAMBDA_COMMAND + f"{ASK_MAP}")
                            # TODO: when do we ask for maps?
                            pass
                        else:
                            if self.bump_map_once[mac_to_idx(device_addr)]:
                                self.send_ack_to(mac_to_idx(device_addr), ACK_END_MAP)
                                #self.send_ack_to(mac_to_idx(device_addr), ACK_TRACKING_MODE + "-1")
                                #self.send_ack_to(mac_to_idx(device_addr), ACK_TRACKING_MODE + "1")
                                self.bump_map_once[mac_to_idx(device_addr)] = False
                            #self.send_ack_to(mac_to_idx(paired_mac), ACK_END_MAP)
                            #self.send_ack_to_all(ACK_FW + "1")
                    elif key_id == KEY_TRANSMISSION_READY:
                        #self.send_ack_to(mac_to_idx(device_addr), ACK_LAMBDA_COMMAND + f"{RESET_MAP}")
                        #self.send_ack_to(mac_to_idx(device_addr), ACK_LAMBDA_COMMAND + f"{ASK_ED}")
                        a='a'
                    elif key_id == KEY_MAP_STATE:
                        addendum = f"({map_status_to_str(state)})"
                        if state == MAP_REBUILD_WAIT_FOR_STATIC:
                            #self.send_ack_to(mac_to_idx(device_addr), ACK_LAMBDA_COMMAND + f"{RESET_MAP}")
                            if self.bump_map_once_2[mac_to_idx(device_addr)]:
                                self.send_ack_to(self.current_host_id, ACK_END_MAP)
                                self.bump_map_once_2[mac_to_idx(device_addr)] = False
                            #self.send_ack_to(mac_to_idx(device_addr), ACK_LAMBDA_SET_STATUS + f"{KEY_MAP_STATE},{MAP_REBUILT}")
                            #self.send_ack_to(mac_to_idx(device_addr), ACK_LAMBDA_SET_STATUS + f"{KEY_CURRENT_TRACKING_STATE},{MAP_REBUILD_CREATE_MAP}")
                        else:
                            self.bump_map_once_2[mac_to_idx(device_addr)] = True
                    elif key_id == KEY_CURRENT_TRACKING_STATE:
                        addendum = f"({pose_status_to_str(state)})"

                    print(f"   Status returned for SLAM key {slam_key_to_str(key_id)} ({mac_str(device_addr)}): {state} {addendum}")

                else:
                    print(f"   Got PLAYER ACK ({mac_str(device_addr)}):", f"CMD{idx}", args)
            elif data[0:2] == ACK_LAMBDA_PROPERTY:
                data_real = data[2:]
                print(f"   Got LP ACK ({mac_str(device_addr)}):", data_real)
            elif data[0:2] == ACK_LAMBDA_STATUS:
                data_real = data[2:]
                a, b, c = [int(s) for s in data_real.split(",")]
                print(f"   Got LAMBDA_STATUS ACK ({mac_str(device_addr)}): {a},{b},{c}")
                self.send_ack_to_all(ACK_FW + "0")
                if b != 2:
                    print("ask for host map.")
                    #self.send_ack_to(mac_to_idx(device_addr), ACK_LAMBDA_COMMAND + f"{ASK_ED}")
                    #self.send_ack_to(mac_to_idx(device_addr), ACK_LAMBDA_COMMAND + f"{ASK_MAP}")
                    #self.send_ack_to(mac_to_idx(device_addr), ACK_LAMBDA_COMMAND + f"{KF_SYNC}")
                    
            elif data[0:4] == ACK_ERROR_CODE:
                data_real = data[4:]
                print(f"   Got ERROR ({mac_str(device_addr)}):", data_real)
            elif data[0:2] == ACK_WIFI_HOST_SSID:
                data_real = data[2:]
                ssid, passwd, freq = data_real.split(",")
                print(f"   Got WIFI_HOST_SSID ACK ({mac_str(device_addr)}): ssid={ssid}, pass={passwd}, freq={freq}")

                self.host_ssid = ssid
                self.host_passwd = passwd
                self.host_freq = freq
            elif data[0:2] == ACK_WIFI_SSID_PASS:
                print(f"   Got WIFI_SSID ACK ({mac_str(device_addr)})")

                self.wifi_set_ssid_full(mac_to_idx(device_addr), self.host_ssid[:8])
                self.wifi_set_ssid_append(mac_to_idx(device_addr), self.host_ssid[8:])
                self.wifi_set_password(mac_to_idx(device_addr), self.host_passwd)
                #self.wifi_set_ssid_password(mac_to_idx(device_addr), self.host_ssid, self.host_passwd)
                self.wifi_set_freq(mac_to_idx(device_addr), self.host_freq)
                self.wifi_set_country(mac_to_idx(device_addr), self.wifi_info["country"])
            elif data[0:2] == ACK_WIFI_CONNECT:
                ret = int(data[2:])
                print(f"   Got WIFI_CONNECT ACK ({mac_str(device_addr)}): {ret}")
                if ret == 1:
                    #self.send_ack_to(mac_to_idx(device_addr), ACK_LAMBDA_COMMAND + f"{ASK_ED}")
                    #self.send_ack_to(mac_to_idx(device_addr), ACK_LAMBDA_ASK_STATUS + f"{KEY_RECEIVED_HOST_ED}")
                    #self.send_ack_to(mac_to_idx(device_addr), ACK_LAMBDA_COMMAND + f"{RESET_MAP}")
                    a='a'

            elif data[0:2] == ACK_MAP_STATUS:
                data_real = data[2:]
                status = [int(s) for s in data_real.split(",")]
                print(f"   Got MAP_STATUS ({mac_str(device_addr)}):", status, f"({map_status_to_str(status[1])})")
                #self.send_ack_to_all(ACK_END_MAP)

                # Initial map status:
                # Got MAP_STATUS: -1,10
                # Got MAP_STATUS: 0,10
                # Got MAP_STATUS: 0,3

                # Losing tracking?
                # Got LP ACK: 1,0,1
                # Got MAP_STATUS: -1,0
                # Got MAP_STATUS: -1,1

                # Got MAP_STATUS: 0,6 = mapped and tracking
            elif data[0:3] == ACK_POWER_OFF:
                print(f".  Got POWER_OFF. ({mac_str(device_addr)})")
                self.handle_disconnected(mac_to_idx(device_addr))
            elif data[0:3] == ACK_RESET:
                print(f".  Got RESET ({mac_str(device_addr)}).")
                self.handle_disconnected(mac_to_idx(device_addr))
            else:
                print(f"   Got ACK ({mac_str(device_addr)}):", data, "(", data_raw, ")")
            print("")
            return
        elif type_maybe == 0x110:
            data = resp[0xC:0xC+data_len]
            self.parse_pose_data(device_addr, data)
            return

        data = resp[0xC:0xC+data_len]
        data_id = data[0]
        data_real = data[1:]
        print("   data_id:", hex(data_id), "data:", data_real)

    def get_PCBID(self):
        return self.send_cmd(DCMD_GET_CR_ID, [CR_ID_PCBID]).decode("utf-8")

    def get_SKUID(self):
        return self.send_cmd(DCMD_GET_CR_ID, [CR_ID_SKUID]).decode("utf-8")

    def get_SN(self):
        return self.send_cmd(DCMD_GET_CR_ID, [CR_ID_SN]).decode("utf-8")

    def get_ShipSN(self):
        return self.send_cmd(DCMD_GET_CR_ID, [CR_ID_SHIP_SN]).decode("utf-8")

    def get_CapFPC(self):
        return self.send_cmd(DCMD_GET_CR_ID, [CR_ID_CAP_FPC]).decode("utf-8")

    def get_ROMVersion(self):
        return self.send_cmd(DCMD_QUERY_ROM_VERSION, [0x00]).decode("utf-8")

    def send_ack_to(self, idx, ack):
        mac = [0x23, 0x30, 0x42, 0xB7, 0x82, 0xD3]
        mac[1] |= idx

        # TX_ACK_TO_MAC checks all MAC bytes,
        # TX_ACK_TO_PARTIAL_MAC checks the first 2
        preamble = struct.pack("<BBBBBBBBB", TX_ACK_TO_PARTIAL_MAC, mac[0],mac[1],mac[2],mac[3],mac[4],mac[5],0, 1)
        ack = struct.pack("<B", len(ack)) + ack.encode("utf-8")

        data = preamble + ack

        return self.send_cmd(DCMD_TX, data)

    def send_ack_to_all(self, ack):
        for i in range(0, 5):
            self.send_ack_to(i, ack)

    def handle_disconnected(self, idx):
        if idx == self.current_host_id:
            self.current_host_id = -1

    def do_loop(self):
        resp = self.device_hid1.read(0x400)
        if len(resp) <= 0:
            return
        #print("dump:")
        #hex_dump(resp)
        #print("parsed:")
        # 0x18 = paired event, gives the 
        if resp[0] == DRESP_PAIR_EVENT:
            self.got_a_pair = True
            #print("dump:")
            #hex_dump(resp)
            cmd_ret, data_ret = self.parse_incoming(resp)
            #hex_dump(data_ret)
            unk = data_ret[0]
            is_unpair = data_ret[1] # 0x1, id?
            paired_mac = data_ret[2:]
            paired_mac_str = mac_str(paired_mac)
            if paired_mac not in self.device_macs:
                self.device_macs += [paired_mac]
                self.num_paired += 1
            print(("Unpaired" if is_unpair else "Paired") + f" {paired_mac_str}, {hex(unk)}")
            #print(self.device_macs)
            self.calib_1 = ""
            self.calib_2 = ""

            if is_unpair:
                self.handle_disconnected(mac_to_idx(paired_mac))
                return

            # I really wish they included the index of each tracker *somewhere*, but it seems
            # like the MACs have always been fake anyhow
            self.send_ack_to(mac_to_idx(paired_mac), ACK_ROLE_ID + "1")
            self.send_ack_to(mac_to_idx(paired_mac), ACK_TRACKING_MODE + "-1")
            #self.send_ack_to(mac_to_idx(paired_mac), ACK_TRACKING_MODE + "1")
            #self.send_ack_to(mac_to_idx(paired_mac), ACK_END_MAP)

            # TODO: detect re-pairs and force re-init
            
            #if self.num_paired <= 1:
            if self.current_host_id == -1 or self.current_host_id == mac_to_idx(paired_mac):
                test_mode = f"{TRACKING_MODE_SLAM_HOST}"
                self.current_host_id = mac_to_idx(paired_mac)
                print(f"Making {paired_mac_str} the SLAM host")
                self.wifi_set_country(mac_to_idx(paired_mac), self.wifi_info["country"])
                self.send_ack_to(mac_to_idx(paired_mac), ACK_TRACKING_HOST + "1")
                self.send_ack_to(mac_to_idx(paired_mac), ACK_WIFI_HOST + "1")
                self.send_ack_to(mac_to_idx(paired_mac), ACK_NEW_ID + "0")
            else:
                test_mode = f"{TRACKING_MODE_SLAM_CLIENT}"
                #self.wifi_connect(mac_to_idx(paired_mac))
                new_id = int(mac_to_idx(paired_mac))

                self.send_ack_to(mac_to_idx(paired_mac), ACK_TRACKING_HOST + "0")
                self.send_ack_to(mac_to_idx(paired_mac), ACK_WIFI_HOST + "0")
                self.send_ack_to(mac_to_idx(paired_mac), ACK_NEW_ID + f"{new_id}")
                #self.send_ack_to(mac_to_idx(paired_mac), ACK_NEW_ID + "0")

            self.send_ack_to(mac_to_idx(paired_mac), ACK_TRACKING_MODE + test_mode)
            #self.send_ack_to(mac_to_idx(paired_mac), ACK_NEW_ID + f"{mac_to_idx(paired_mac)}")
            #if self.current_host_id == mac_to_idx(paired_mac):
            if self.current_host_id == mac_to_idx(paired_mac):
                self.send_ack_to(mac_to_idx(paired_mac), ACK_END_MAP)
            else:
                self.send_ack_to(mac_to_idx(paired_mac), ACK_LAMBDA_COMMAND + f"{RESET_MAP}")
            #self.send_ack_to(mac_to_idx(paired_mac), ACK_ATW)
            #if self.current_host_id == mac_to_idx(paired_mac):
            #    self.send_ack_to(mac_to_idx(paired_mac), ACK_LAMBDA_SET_STATUS + f"{KEY_TRANSMISSION_READY},1")

            #self.send_ack_to_all(ACK_FW + "1")
            #self.send_ack_to_all(ACK_FW + "0")
            self.send_ack_to(mac_to_idx(paired_mac), ACK_FW + "1")
            
        elif resp[0] == DRESP_TRACKER_RF_STATUS or resp[0] == DRESP_TRACKER_NEW_RF_STATUS or resp[0] == 0x29:
            print(f"dump for {hex(resp[0])}:")
            #hex_dump(resp)
            cmd_ret, data_ret = self.parse_incoming(resp)
            if resp[0] == DRESP_TRACKER_RF_STATUS or resp[0] == DRESP_TRACKER_NEW_RF_STATUS:
                self.parse_tracker_status(data_ret)
            else:
                hex_dump(data_ret)
        elif resp[0] == DRESP_TRACKER_INCOMING:
            self.parse_tracker_incoming(resp)
            #self.send_raw(bytes([0]) + resp)

            #hex_dump(self.send_cmd(DCMD_28, struct.pack("<BBBBBBBB", DCMD_28_SUBCMD_8, 1, 0, 0, 0, 0, 0x22, 0x3) + "APF".encode("utf-8")))
            #hex_dump(self.send_cmd(DCMD_28, struct.pack("<BBBBBB", DCMD_28_SUBCMD_9, 1, 0, 0, 0, 0)))

            #hex_dump(self.send_cmd(DCMD_98, struct.pack("<BB", 0x22, 0x3) + "APF".encode("utf-8"))) 
            #hex_dump(self.send_cmd(DCMD_99, struct.pack("<BB", 0x22, 0x3) + "APF".encode("utf-8"))) 

            # These commands feel sketchy...
            #hex_dump(self.send_F4([1,1,1,1,1], 0))
            #hex_dump(self.send_F4([1,1,1,1,1], 1, struct.pack("<BL", 0, 0)))

            
            #self.send_ack_to_all(ACK_TRACKING_MODE + "1")
            #self.send_ack_to_all("ATW")
            
            #self.send_ack_to_all(ACK_LAMBDA_SET_STATUS + f"{KEY_TRANSMISSION_READY},1")
            #self.send_ack_to_all(ACK_LAMBDA_ASK_STATUS + f"{KEY_CURRENT_MAP_ID}")
            
            self.tick_periodic += 1
            if self.tick_periodic > 1000:
                print("Tick!")
                #self.send_ack_to_all(ACK_LAMBDA_MESSAGE + "1:0")
                self.send_ack_to_all(ACK_LAMBDA_ASK_STATUS + f"{KEY_TRANSMISSION_READY}")
                #self.send_ack_to_all(ACK_LAMBDA_ASK_STATUS + f"{KEY_RECEIVED_HOST_MAP}")
                self.send_ack_to_all(ACK_LAMBDA_ASK_STATUS + f"{KEY_CURRENT_MAP_ID}")
                self.send_ack_to_all(ACK_LAMBDA_ASK_STATUS + f"{KEY_MAP_STATE}")
                self.send_ack_to_all(ACK_LAMBDA_ASK_STATUS + f"{KEY_CURRENT_TRACKING_STATE}")

                #self.send_ack_to_all(ACK_LAMBDA_SET_STATUS + f"{KEY_TRANSMISSION_READY},1")
                #self.send_ack_to_all(ACK_ATW)


                for i in range(0, 5):
                    #self.send_ack_to(i, ACK_NEW_ID + f"{i}")
                    #self.wifi_connect(i)
                    #self.wifi_set_ssid_full(i, self.wifi_info["ssid"])
                    #self.wifi_set_password(i, self.wifi_info["pass"])
                    #self.wifi_set_country(i, self.wifi_info["country"])
                    
                    if i != self.current_host_id:
                        self.send_ack_to(i, ACK_LAMBDA_ASK_STATUS + f"{KEY_RECEIVED_HOST_ED}")
                        self.send_ack_to(i, ACK_LAMBDA_ASK_STATUS + f"{KEY_RECEIVED_HOST_MAP}")
                    
                    #    self.send_ack_to(i, ACK_LAMBDA_COMMAND + f"{ASK_ED}")
                    pass

                self.tick_periodic = 0
            #self.send_ack_to_all(ACK_LAMBDA_MESSAGE)
        else:
            print("dump:")
            hex_dump(resp)

    def wifi_connect(self, idx):
        self.send_ack_to(idx, ACK_WIFI_CONNECT)

    #def wifi_set_ssid_password(self, idx, ssid, passwd):
    #    self.send_ack_to(idx, f"{ACK_WIFI_SSID_PASS}{ssid},{passwd}")

    def wifi_set_ssid_full(self, idx, ssid):
        self.send_ack_to(idx, ACK_WIFI_SSID_FULL + ssid)

    def wifi_set_ssid_append(self, idx, ssid):
        self.send_ack_to(idx, ACK_WIFI_SSID_APPEND + ssid)

    def wifi_set_country(self, idx, country):
        self.send_ack_to(idx, ACK_WIFI_COUNTRY + country)

    def wifi_set_password(self, idx, passwd):
        self.send_ack_to(idx, ACK_WIFI_PW + passwd)

    def wifi_set_freq(self, idx, freq):
        self.send_ack_to(idx, f"{ACK_WIFI_FREQ}{freq}")

class TrackerHID:

    def __init__(self):
        self.watchdog_delay = 0
        self.map_once = True
        self.poses_recvd = 0
        self.slam_online = False

        self.pose_quat = [0.0, 0.0, 0.0, 1.0]
        self.pose_pos = [0.0, 0.0, 0.0]
        self.pose_time = 0

        device_list = hid.enumerate(VID_VIVE, PID_TRACKER)
        print(device_list)

        #Find the device with the particular usage you want
        device_dict_hid1 = [device for device in device_list if device['interface_number'] == HID1_INTERFACE_NUM][0]
        self.device_hid1 = hid.Device(path=device_dict_hid1['path'])

        '''
        device_dict_hid3 = [device for device in device_list if device['interface_number'] == HID3_INTERFACE_NUM][0]
        device_hid3 = hid.Device(path=device_dict_hid3['path'])
        '''

        #self.set_tracking_mode(TRACKING_MODE_SLAM_HOST)
        #self.set_tracking_mode(0xFFFFFFFF)
        #self.set_tracking_mode(TRACKING_MODE_SLAM_HOST)
        self.set_power_pcvr(TRACKING_MODE_SLAM_HOST)

        with open('wifi_info.json', 'r') as f:
            self.wifi_info = json.load(f)

    def parse_response(self, data):
        unk, cmd_id, data_len, unk2 = struct.unpack("<BHBB", data[:5])
        #print(f"unk: {hex(unk)} cmd_id: {hex(cmd_id)} data_len: {hex(data_len)} unk2: {hex(unk2)} ")

        ret = data[5:5+data_len]
        return cmd_id, ret

    def send_command(self, cmd_id, data=None):
        if data is None:
            data = []
        out = struct.pack("<HBB", cmd_id, len(data), 0)
        out += bytes(data)

        out += bytes([0x0] * (0x40 - len(out)))

        try:
            ret = self.device_hid1.send_feature_report(out)
            for i in range(0, 10):
                resp = self.device_hid1.get_feature_report(0, 0x40)
                #hex_dump(resp)
                cmd_ret, data_ret = self.parse_response(resp)
                #hex_dump(data_ret)
                if cmd_ret == cmd_id:
                    return data_ret
        except:
            return bytes([])

        return bytes([])

    def send_haptic(self, nDuration, nFrequency, nAmplitude, identify):
        self.send_command(PACKET_SET_HAPTIC, struct.pack("<HHHH", nDuration, nFrequency, nAmplitude, identify))

    def get_str_info(self, idx):
        return self.send_command(PACKET_GET_STR_INFO, [idx]).decode("utf-8")

    def set_str_info(self, idx, val):
        return self.send_command(PACKET_SET_STR_INFO, struct.pack("<BS", idx, val))

    def get_status(self):
        ret = self.send_command(PACKET_GET_STATUS)
        tracking_mode, power, batt, hmd_init, device_status_mask, btn = struct.unpack("<BBBBBL", ret)
        print(f"tracking_mode={tracking_mode}, power={power}, batt={batt}, hmd_init={hmd_init}, device_status_mask={hex(device_status_mask)}, btn={hex(btn)}")

    def set_tracking_mode(self, mode):
        self.send_command(PACKET_SET_TRACKING_MODE, [mode & 0xFF])

    # ex: bootloader, fastboot, etc. I think.
    def set_reboot(self, reason=""):
        self.send_command(PACKET_SET_REBOOT, reason.encode("utf-8"))

    def get_property(self, key):
        self.send_command(PACKET_GET_PROPERTY, key.encode("utf-8"))

    def parse_pose_data(self, data):
        self.poses_recvd += 1

        if len(data) == 0x2:
            idx, btns = struct.unpack("<BB", data)
            print(hex(idx), "btns:", hex(btns))
            return

        if len(data) != 0x25 and len(data) != 0x27:
            print("Weird pose data.", len(data))
            hex_dump(data)
            return
        idx, btns, pos, rot, acc, rot_vel, tracking_status = struct.unpack("<BB12s8s6s8sB", data[:0x25])
        
        # tracking_status = 2 => pose + rot
        # tracking_status = 3 => rot only
        # tracking_status = 4 => pose frozen (lost tracking), rots

        pos_arr = np.frombuffer(pos, dtype=np.float32, count=3)
        rot_arr = np.frombuffer(rot, dtype=np.float16, count=4)
        acc_arr = np.frombuffer(acc, dtype=np.float16, count=3)
        rot_vel_arr = np.frombuffer(rot_vel, dtype=np.float16, count=4)
        print(hex(idx), pose_status_to_str(tracking_status), "btns:", hex(btns), "pos:", pos_arr, "rot:", rot_arr, "acc:", acc_arr, "rot_vel:", rot_vel_arr, "time_delta", current_milli_time() - self.pose_time)

        self.pose_quat = rot_arr
        self.pose_pos = pos_arr
        self.pose_time = current_milli_time()

        #if self.map_once and self.poses_recvd > 1000:
        #    self.slam_online = True
        #    self.send_ack_to(mac_to_idx(mac), ACK_END_MAP)
        #    #self.send_ack_to_all(ACK_END_MAP)
        #    self.map_once[mac_to_idx(mac)] = False

    def parse_incoming(self):
        resp = self.device_hid1.read(0x400)
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
                self.parse_pose_data(pose_data)
        netsync_str = "netsync: "
        for i in range(0, 7):
            a,b = struct.unpack("<QQ", resp[0x2ce+(i*0x10):0x2ce+(i*0x10)+0x10])
            netsync_str += f"({a},{b}) "
        print(netsync_str)
        print("")
        print("")

    # 1=gyro, 2=body tracking(?), 3=body?
    def set_power_pcvr(self, mode):
        self.send_command(PACKET_SET_POWER_PCVR, [mode & 0xFF])

    def get_ack(self):
        hex_dump(self.send_command(PACKET_GET_ACK))

    def kick_watchdog(self):
        self.watchdog_delay += 1
        if self.watchdog_delay < 1000:
            return
        self.send_command(PACKET_SET_WATCHDOG_KICK)
        self.watchdog_delay = 0

    # default 3?
    def set_camera_policy(self, val):
        self.send_command(PACKET_SET_CAMERA_POLICY, [val])

    # default 3?
    def set_camera_fps(self, val):
        self.send_command(PACKET_SET_CAMERA_FPS, [val])

    def get_pos(self, idx=0):
        return np.array(self.pose_pos)

    def get_rot(self, idx=0):
        return np.array(self.pose_quat)

    def do_loop(self):
        self.parse_incoming()
        self.kick_watchdog()

if __name__ == '__main__':
    dongle = DongleHID()
    #dongle = TrackerHID()

    while True:
        dongle.do_loop()


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