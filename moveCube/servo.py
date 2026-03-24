import serial
import os

#def moveServo(
#    mode,
#    device,
#    channel,
#    target1=None,
#    target2=None,
#    target3=None,
#    target4=None
#):

#def encode_7bit(value):
#    return [value & 0x7F, (value >> 7) & 0x7F]

def encode_7bit(value):
    lsb = value & 0x7F
    msb = (value >> 7) & 0x7F
    return [lsb, msb]

def moveServo(mode, device, channel, target1=None, target2=None, target3=None, target4=None):
    with serial.Serial(device, 115200, timeout=1) as ser:
        ser.write(bytearray([0xAA, 12]))

        if mode == "single":
            data = bytearray([0x84, channel])
            data.extend(encode_7bit(target1))

        elif mode == "dual":
            data = bytearray([0x9F, 2, channel])
            data.extend(encode_7bit(target1))
            data.extend(encode_7bit(target2))

        elif mode == "all":
            data = bytearray([0x9F, 4, channel])
            data.extend(encode_7bit(target1))
            data.extend(encode_7bit(target2))
            data.extend(encode_7bit(target3))
            data.extend(encode_7bit(target4))

        elif mode == "get":
            data = bytearray([0x90, channel])
            ser.write(data)
            response = ser.read(2)  # Adjust size depending on expected response
            print(f"Response: {list(response)}")
            return response

        else:
            raise ValueError(f"Unknown mode: {mode}")

        # Send the constructed byte command
        ser.write(data)