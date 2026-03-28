import json
import os
import sys
from time import sleep
from moveCube.maestro import *

with open('config/config.json', mode='r', encoding='utf-8') as jsonFile:
    config = json.load(jsonFile)

serialDevice = config['serial'][os.name]

delay90 = int(config['delay']['90']) / 1000
delay180 = int(config['delay']['180']) / 1000
delayMove = int(config['delay']['move']) / 1000
delayPhoto = int(config['delay']['photo']) / 1000

def photo (side: str):
    match side:
        case 'F':
            dualMove('rIn')
            sleep(delayMove)
            dualMove('rRight')
            sleep(delay90)
            dualMove('rOut')
            sleep(delayMove)
            dualMove('uIn')
        case 'R':
            dualMove('uOut')
            sleep(delayMove)
            dualMove('rIn')
            sleep(delayMove)
            dualMove('uRight')
        case 'B':
            dualMove('u180')
            sleep(delay180)
            dualMove('rOut')
            sleep(delayMove)
            dualMove('uIn')
        case 'L':
            dualMove('uOut')
            sleep(delayMove)
            dualMove('rIn')
            sleep(delayMove)
            dualMove('uLeft')
        case 'U':
            dualMove('uHome')
            sleep(delay90)
            dualMove('rHome')
            sleep(delay90)
            dualMove('rOut')
            sleep(2 * delayMove)
            dualMove('uIn')
            sleep(2 * delayMove)
            dualMove('rLeft')
        case 'D':
            dualMove('rRight')
        case 'finish':
            dualMove('rHome')
            sleep(delay90)
            dualMove('uIn')
            sleep(delayMove)
            dualMove('uHome')
            sleep(delay90)
            dualMove('uOut')

def rotate (action: str, cube: str):
    side = action[0].lower()
    turn = action[-1]
    
    match cube:
        case 'front':
            dualMove('rIn')
            sleep(delay90)
            dualMove('uRight')
            sleep(delay90)
            dualMove('rOut')
            sleep(delay90)
            dualMove('uIn')
            sleep(delay90)
            dualMove('uHome')
            sleep(delay90)
            dualMove('uOut')
            sleep(delay90)
        case 'right':
            dualMove('rIn')
            sleep(delay90)
            dualMove('uLeft')
            sleep(delay90)
            dualMove('rOut')
            sleep(delay90)
            dualMove('uIn')
            sleep(delay90)
            dualMove('uHome')
            sleep(delay90)
            dualMove('uOut')
            sleep(delay90)
        case _:
            raise ValueError("Invalid side")
    
    if side == "f":
        dSide = "r"
    elif side == "b":
        dSide = "l"
    else:
        dSide = side

    match turn:
        case '1':
            dest = dSide + 'Right'
            delay = delay90
        case '2':
            dest = dSide + '180'
            delay = delay180
        case '3':
            dest = dSide + 'Left'
            delay = delay90
        case _:
            raise ValueError("Invalid turn")

    match side:
        case 'R':
            singleMove(dest)
            sleep(delay)
            singleMove('rIn')
            sleep(delayMove)
            singleMove('rHome')
            sleep(delay)
            singleMove('rOut')
            sleep(delayMove)
        case 'L':
            singleMove(dest)
            sleep(delay)
            singleMove('lIn')
            sleep(delayMove)
            singleMove('lHome')
            sleep(delay)
            singleMove('lOut')
            sleep(delayMove)
        case 'U':
            singleMove(dest)
            sleep(delay)
            singleMove('uIn')
            sleep(delayMove)
            singleMove('uHome')
            sleep(delay)
            singleMove('uOut')
            sleep(delayMove)
        case 'D':
            singleMove(('dOut') + 100)
            sleep(0.2)
            singleMove(dest)
            sleep(delay)
            singleMove('dIn')
            sleep(delayMove)
            singleMove('dHome')
            sleep(delay)
            singleMove('dOut')
            sleep(delayMove)
        case 'F':
            singleMove(dest)
            sleep(delay)
            singleMove('rIn')
            sleep(delayMove)
            singleMove('rHome')
            sleep(delay)
            singleMove('rOut')
            sleep(delayMove)
        case 'B':
            singleMove(dest)
            sleep(delay)
            singleMove('lIn')
            sleep(delayMove)
            singleMove('lHome')
            sleep(delay)
            singleMove('lOut')
            sleep(delayMove)
