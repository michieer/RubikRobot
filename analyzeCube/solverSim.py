def SolveCube (solution: str):
    list = (solution.split(' '))[:-1]
    steps = len(list)
    print("Kociemba: " + solution)
    print("Steps:" + str(steps))

    # Sent moves to robot
    front = "front"
    for i in range(0,steps):
        Finished = False
        move = list[i]

    # Sent moves to robot
    front = "front"
    for i in range(0,steps):
        Finished = False
        move = list[i]
        side = move[0].upper()

        print("Move " + str(i + 1) + ": " + move)
        print("Side: " + side)

        if ((front == "front") and ((side == "F") or (side == "B"))):
            front = "right"
            print("Turning right to right")
        elif ((front == "right") and ((side == "R") or (side == "L"))):
            front = "front"
            print("Turning front to right")
        else:
            turn = "none"
