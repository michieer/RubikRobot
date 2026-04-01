from moveCube.moves import rotate, twist
from moveCube.handles import park
from moveCube.logger import *

def SolveCube (self, solution: str):
    list = (solution.split(' '))[:-1]
    steps = len(list)
    
    # Sent moves to robot
    front = "front"
    for i in range(0,steps):
        Finished = False
        move = list[i]
        side = move[0].upper()
        
        log("Move " + str(i + 1) + " " + move)
        
        if ((front == "front") and ((side == "F") or (side == "B"))):
            log("Turning front - right")
            front = "right"
            twist("right")
        elif ((front == "right") and ((side == "R") or (side == "L"))):
            log("Turning front - front")
            front = "front"
            twist("front")

        rotate(list[i])

    park()
