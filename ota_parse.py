import struct
import os

# Not what HTC used lmao
def crc128(buf, crc=0xffffffffffffffffffffffffffffffff):
    for val in buf:
        crc ^= val << 120
        for _ in range(8):
            crc <<= 1
            if crc & 2**128:
                crc ^= 0x14caa61b0d7fe5fa54189d46709eaba2d
    return crc

# "CRC128" as used in HTC's nRF52 OTA files
def htc_crc128(buf):
    def mask64(v):
        return v  & 0xFFFFFFFFFFFFFFFF
    def mask32(v):
        return v  & 0xFFFFFFFF

    calcLower = 0
    calcUpper = 0
    for buffer_idx in range(0, len(buf), 0x10):
        calcLower_masked = mask32(calcLower)

        val_lower = struct.unpack("<Q", buf[buffer_idx:buffer_idx+8])[0]
        val_upper = struct.unpack("<Q", buf[buffer_idx+8:buffer_idx+16])[0]

        calcLower_iter = (calcLower >> 1 | calcUpper << 63) ^ val_lower
        calcUpper_iter = (val_upper & 0x8000000000000000)
        
        calcUpper_iter_intermediate = calcLower_masked
        calcUpper_iter_intermediate ^= (calcLower_masked >> 2)
        calcUpper_iter_intermediate ^= (calcLower_masked >> 27)
        calcUpper_iter_intermediate ^= (calcLower_masked >> 29)
        
        calcUpper_iter ^= calcUpper_iter_intermediate << 63
        calcUpper_iter |= (val_upper & 0x7fffffffffffffff) ^ calcUpper >> 1

        calcLower = mask64(calcLower_iter)
        calcUpper = mask64(calcUpper_iter)

    return calcLower | (calcUpper << 64)

# bytes -> bigint
def to_int128(b):
    upper,lower = struct.unpack("<QQ", b)
    return lower | (upper << 64)

f = open("trackers/firmware/TX_FW.ota", "rb")
contents = f.read()

header = contents[:0x70]
number_of_segments = struct.unpack("<L", header[0x10:0x14])[0]

partitions = header[0x40:]
# Usually 2 segments, APP/UPDATER? or maybe the other way around, second is larger.
for i in range(0, number_of_segments):
    offs = 0x40 + (i*0x20)
    partition = contents[offs:offs+0x20]
    file_offs,flash_addr,mem_addr,file_sz,crc128_val = struct.unpack("<LLLL16s", partition)
    crc128_val = to_int128(crc128_val)
    print(f"file_offs: {hex(file_offs)}, flash_addr: {hex(flash_addr)}, mem_addr: {hex(mem_addr)}, file_sz: {hex(file_sz)}")
    
    partition_data = contents[file_offs:file_offs+file_sz]
    crc128_calc = htc_crc128(bytes(partition_data))
    print("CRC128 is", "valid!" if crc128_val == crc128_calc else "BAD!")
    print("calc:", hex(crc128_calc), "stored:", hex(crc128_val))
    print("")

    f_w = open(f"seg_{i}_{hex(mem_addr)[2:]}.bin", "wb")
    f_w.write(partition_data)
    f_w.close()

f.close()
