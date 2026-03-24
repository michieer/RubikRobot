from time import sleep
from moveCube.maestro import *

def home ():
    allMove('In')
    sleep(1)
    allMove('Home')

def mount ():
    singleMove('dOut')
    sleep(2)
    dualMove('rOut')
    sleep(2)
    singleMove('uOut')

def park ():
    allMove('Park')
    sleep(2)
    allMove('Home')

def move (pos: str):
    singleMove(pos)
