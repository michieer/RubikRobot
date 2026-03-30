import os
import json
import serial
import moveCube.servo as servo
import serial.tools.list_ports

with open('config/config.json', mode='r', encoding='utf-8') as jsonFile:
    config = json.load(jsonFile)

# Assign serial portname
match os.name:
    case 'nt':
        for port in serial.tools.list_ports.comports():
            if "Pololu" in port.description and "Command" in port.description:
                serialDevice = port.device
    case 'posix':
        serialDevice = '/dev/ttyACM0'

rTurn = config['right']['turnId']
rHome = config['right']['90']
rLeft = config['right']['0']
rRight = config['right']['180']
r180 = config['right']['270']
rMove = config['right']['moveId']
rIn = config['right']['in']
rOut = config['right']['out']
rPark = config['right']['park']

lTurn = config['left']['turnId']
lHome = config['left']['180']
lLeft = config['left']['90']
lRight = config['left']['270']
l180 = config['left']['0']
lMove = config['left']['moveId']
lIn = config['left']['in']
lOut = config['left']['out']
lPark = config['left']['park']

uTurn = config['up']['turnId']
uHome = config['up']['90']
uLeft = config['up']['0']
uRight = config['up']['180']
u180 = config['up']['270']
uMove = config['up']['moveId']
uIn = config['up']['in']
uOut = config['up']['out']

dTurn = config['down']['turnId']
dHome = config['down']['180']
dLeft = config['down']['90']
dRight = config['down']['270']
d180 = config['down']['0']
dMove = config['down']['moveId']
dIn = config['down']['in']
dOut = config['down']['out']
dPark = config['down']['park']

def singleMove (action: str):
    side = action[0].lower()
    move = action[1:]

    match side:
        case 'r':
            if ((move == 'In') or (move == 'Out')):
                port = 8
            else:
                port = 0
        case 'l':
            if ((move == 'In') or (move == 'Out')):
                port = 9
            else:
                port = 1
        case 'u':
            if ((move == 'In') or (move == 'Out')):
                port = 10
            else:
                port = 2
        case 'd':
            if ((move == 'In') or (move == 'Out')):
                port = 11
            else:
                port = 3
        case _:
            raise ValueError("Invalid side")


    action1 = globals()[action]
    servo.moveServo('single', serialDevice, port, action1)
servo.moveServo
def dualMove (action: str):
    side = action[0].lower()
    move = action[1:]

    match side:
        case 'r':
            match move:
                case 'Out':
                    port = 8
                    action1 = rOut
                    action2 = lOut
                case 'In':
                    port = 8
                    action1 = rIn
                    action2 = lIn
                case 'Home':
                    port = 0
                    action1 = rHome
                    action2 = lHome
                case 'Left':
                    port = 0
                    action1 = rLeft
                    action2 = lRight
                case 'Right':
                    port = 0
                    action1 = rRight
                    action2 = lLeft
                case '180':
                    port = 0
                    action1 = r180
                    action2 = l180
                case _:
                    raise ValueError("Invalid move")
        case 'u':
            match move:
                case 'Out':
                    port = 10
                    action1 = uOut
                    action2 = dOut
                case 'In':
                    port = 10
                    action1 = uIn
                    action2 = dIn
                case 'Home':
                    port = 2
                    action1 = uHome
                    action2 = dHome
                case 'Left':
                    port = 2
                    action1 = uLeft
                    action2 = dRight
                case 'Right':
                    port = 2
                    action1 = uRight
                    action2 = dLeft
                case '180':
                    port = 2
                    action1 = u180
                    action2 = d180
                case _:
                    raise ValueError("Invalid move")
        case _:
            raise ValueError("Invalid side")


    servo.moveServo('dual', serialDevice, port, action1, action2) 
def allMove (move: str):
    match move:
        case 'Home':
            port = 0
            action1 = rHome
            action2 = lHome
            action3 = uHome
            action4 = dHome
        case 'In':
            port = 8
            action1 = rIn
            action2 = lIn
            action3 = uIn
            action4 = dIn
        case 'Park':
            port = 8
            action1 = rPark
            action2 = lPark
            action3 = uIn
            action4 = dPark
        case _:
            raise ValueError("Invalid move")

    servo.moveServo('all', serialDevice, port, action1, action2, action3, action4)


