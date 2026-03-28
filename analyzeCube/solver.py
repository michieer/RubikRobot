from moveCube.moves import rotate
from moveCube.handles import park

def SolveCube (solution: str):
    list = (solution.split(' '))[:-1]
    steps = len(list)
    
    # Sent moves to robot
    front = "front"
    for i in range(0,steps):
        Finished = False
        move = list[i]
        print("Move " + str(i + 1) + ": " + move + "\n")

        side = move[0].upper()
        if ((front == "front") and ((side == "F") or (side == "B"))):
            front = "right"
            turn = "right"
        elif ((front == "right") and ((side == "R") or (side == "L"))):
            front = "front"
            turn = "front"
        else:
            turn = "none"

        rotate(list[i], turn)

        while True:
            if (Finished == True):
                break

    park()
