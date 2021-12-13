import asyncio
import bleak
import random
import time
from crccheck.crc import Crc8Maxim

address = "3DA22873-FFC2-4DED-9249-E4FE53F060FF"
WRITE_CHAR = "6e400002-e6ac-a7e7-b1b3-e699bae80060"
NOTIFY_CHAR = "6e400003-e6ac-a7e7-b1b3-e699bae80060"
stx = b"\xA3\xA4"


async def main(new_device):

    client = None

    async def _handle(sender, data):
        print("%s -> %s" % (sender, data))
        rand_1 = data[3] - 50
        if bytes([data[5] ^ rand_1]) == b"\x01":
            communication_key = data[0:3]
            for b in data[3:]:
                communication_key += bytes([b ^ rand_1])
            print("key:", communication_key)
            rand_2 = random.randint(0, 200)
            rand_3 = bytes([rand_2 + 50])
            user_id = (1).to_bytes(4, byteorder="big")
            x = time.time()
            timestamp = int(x).to_bytes(4, byteorder="big")
            packet_open = stx + b"\x0A" + rand_3
            for b in (
                communication_key[7:8] + b"\x05\x01" + user_id + timestamp + b"\x00"
            ):
                packet_open += bytes([b ^ rand_2])
            crc_8 = bytes([Crc8Maxim.calc(packet_open)])
            await client.write_gatt_char(WRITE_CHAR, packet_open + crc_8)
            """
        elif bytes([data[5] ^ rand_1]) == b"\x05":
            communication_key = data[0:3] + bytes([rand_1])
            for b in data[4:11]:
                communication_key += bytes([b ^ rand_1])
            print("open information:", communication_key + data[11:12])
            """
            rand_4 = random.randint(0, 200)
            rand_5 = bytes([rand_4 + 50])
            packet_lock_information = stx + b"\x01" + rand_5
            for b in communication_key[7:8] + b"\x31\x01":
                packet_lock_information += bytes([b ^ rand_4])
            crc_8 = bytes([Crc8Maxim.calc(packet_lock_information)])
            await client.write_gatt_char(WRITE_CHAR, packet_lock_information + crc_8)
        elif bytes([data[5] ^ rand_1]) == b"\x31":
            communication_key = data[0:3] + bytes([rand_1])
            for b in data[4:13]:
                communication_key += bytes([b ^ rand_1])
            print("lock information:", communication_key + data[13:14])
            print("Version %d" % int.from_bytes(data[12:13], byteorder="big"))

    async with bleak.BleakClient(new_device) as client:
        if client.is_connected:
            print("jaga jaga")
            rand_0 = random.randint(0, 200)
            rand = bytes([rand_0 + 50])
            packet = stx + b"\x08" + rand
            for b in b"\x00\x01\x4F\x6D\x6E\x69\x57\x34\x47\x58":
                packet += bytes([b ^ rand_0])
            crc_8 = bytes([Crc8Maxim.calc(packet)])
            await client.start_notify(NOTIFY_CHAR, _handle)
            await client.write_gatt_char(WRITE_CHAR, packet + crc_8)
            await asyncio.sleep(2)
            await client.stop_notify(NOTIFY_CHAR)
            await client.disconnect()
        else:
            print("ne jaga jaga")


asyncio.run(main(address))
