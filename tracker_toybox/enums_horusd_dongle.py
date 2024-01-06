#
# DONGLE COMMANDS (DCMD = dongle command)
#
DCMD_TX = 0x18 #  -> RF_REPORT_RF_VERSION, [0]->[0,0,0], [1]->[0,0], [2]->[2,0,0,0,...], [3]->[3], [4]->[4]

DCMD_RESET_DFU = 0x1C # -> Enters DFU bootloader? accepts 2 bytes, first byte is seemingly not used, second must be 2 or 3?
DCMD_REQUEST_RF_CHANGE_BEHAVIOR = 0x1D # -> RF_REPORT_CHANGE_BEHAVIOR. Crafts some pkt if given >2 bytes (sent to specific device). First byte must be <7, !=3, !=4, second byte must be 0 or 1
DCMD_1E = 0x1E # -> gets RF_REPORT_CHANGE_BEHAVIOR w/o changing anything, checks if length is 2?

DCMD_21 = 0x21 # -> RF_REPORT_RF_MODE_OP? BRICKED MY DONGLE :( Accepts only 1 byte

DCMD_26 = 0x26 # -> Echoes back the USB buffer, 0x40 bytes
DCMD_27 = 0x27 # -> RF_REPORT_RF_IDS, "Proprietary" in string. Checks if data is [7] and size is < 4, but does nothing with it.
DCMD_28 = 0x28 # -> , takes [6/7/8/9, ...]

DCMD_FLASH_WRITE_1 = 0x98 # -> flashing related! accepts 5 bytes: <BL, second arg must not be > 0x14000, first arg must not be 1 or 2
DCMD_FLASH_WRITE_2 = 0x99 # -> flashing related! does a crc32. data length must not exceed 0x3c
DCMD_FLASH_WRITE_3 = 0x9A # -> flashing related! accepts <BBBBBL, last u32 is the crc32 of the data. finalizes flashing?

DCMD_9E = 0x9E # -> accepts 1 byte.
DCMD_9F = 0x9F # -> always returns 0x10 00s if data[0] is not 0x2, otherwise, resets into cmd98..cmd9A data? maybe?
DCMD_EB = 0xEB # -> Reboot

DCMD_WRITE_CR_ID = 0xEF # -> writes to ID stuff, accepts a byte idx and data. data must not exceed 0x3d
DCMD_GET_CR_ID = 0xF0 # -> a lot of ID stuff
DCMD_F3 = 0xF3 # -> wrapper for cmd 0x1D?
DCMD_F4 = 0xF4 # -> accepts <BBBBBBB, a checksum, 5 bytes (presumably trackers), and a subcmd minimum
DCMD_QUERY_ROM_VERSION = 0xFF # -> ROM version, does not check input

# Everything that's showed up in tracker-side binaries, but not in the dongle firmware
#DCMD_1A = 0x1A # -> GetFusionMode, GetRoleId?
#DCMD_9C = 0x9C # -> "RequestData"?
#DCMD_9D = 0x9D # -> "RequestData"?
#DCMD_A4 = 0xA4 # RequestCap1/RequestCap2?
#DCMD_FA = 0xFA # -> used in DisableCharging?

#
# SUB COMMANDS
#
TX_SUBCMD_0 = 0x00 # returns const
TX_SUBCMD_1 = 0x01 # returns const
TX_SUBCMD_2 = 0x02 # returns const
TX_ACK_TO_MAC = 0x03 # data len must be <=0x2C data[8] must be 10, data[9] must be < 0x10
TX_ACK_TO_PARTIAL_MAC = 0x04
TX_SUBCMD_5 = 0x05 # Takes 5 bytes in, sends ACK P:%d to each tracker where %d is the value in the input

DCMD_21_SUBCMD_0 = 0x00 # BRICKED MY DONGLE :(
DCMD_21_SUBCMD_1 = 0x01 # would have unbricked my dongle if I could actually send USB commands
DCMD_21_SUBCMD_2 = 0x02 # flashes some different byte?
DCMD_21_SUBCMD_5 = 0x05 # flashes some different byte?
DCMD_21_SUBCMD_6 = 0x06 # flashes some different byte?
DCMD_21_SUBCMD_7 = 0x07 # restarts?
DCMD_21_SUBCMD_8 = 0x08 # restarts?

# DCMD_REQUEST_RF_CHANGE_BEHAVIOR
RF_BEHAVIOR_PAIR_DEVICE = 0x00 # pair
RF_BEHAVIOR_RX_POWER_SAVING = 0x01 # RxPowerSaving
RF_BEHAVIOR_RESTART_RF = 0x02 # RestartRf
RF_BEHAVIOR_FACTORY_RESET = 0x05 # Factory Reset
RF_BEHAVIOR_6 = 0x06 # ? clears pairing info maybe

DCMD_28_SUBCMD_6 = 0x06 # -> accepts 1 byte, might restart?
DCMD_28_SUBCMD_7 = 0x07 # -> returns some bytes from RAM, does the same weird check as 0x27
DCMD_28_SUBCMD_8 = 0x08 # -> takes 5 bytes, one per tracker presumably, as well as some extra bytes?
DCMD_28_SUBCMD_9 = 0x09 # -> takes 5 bytes, one per tracker presumably

DCMD_F4_SUBCMD_0 = 0x00 # -> 00 00 00 00 00 00 2c hex_dump(send_rf_command(0xF4, [0,0,0,0,0,0,0])) -> 01 03 03 03 03 00 2c hex_dump(send_rf_command(0xF4, [1,  1,1,1,1,1,0])) tracker related
DCMD_F4_SUBCMD_1 = 0x01 # also accepts <BL
DCMD_F4_SUBCMD_2 = 0x02
DCMD_F4_SUBCMD_3 = 0x03

# DCMD_GET_CR_ID
CR_ID_PCBID = 0x06
CR_ID_SKUID = 0x07
CR_ID_SN = 0x08
CR_ID_SHIP_SN = 0x09
CR_ID_CAP_FPC = 0x11

# Safety-oriented lists
DCMDS_THAT_RESTART = [DCMD_RESET_DFU, DCMD_21, DCMD_9F, DCMD_EB]
DCMDS_THAT_WRITE_FLASH = [DCMD_21, DCMD_FLASH_WRITE_1, DCMD_FLASH_WRITE_2, DCMD_FLASH_WRITE_3, DCMD_WRITE_CR_ID]
DCMD_FUZZ_BLACKLIST = DCMDS_THAT_RESTART + DCMDS_THAT_WRITE_FLASH

#
# RESPONSE IDs
#
DRESP_PAIR_EVENT = 0x18
DRESP_TRACKER_NEW_RF_STATUS = 0x1D
DRESP_TRACKER_RF_STATUS = 0x1E
DRESP_TRACKER_INCOMING = 0x28