import analyzeCube.twophase.solver as sv
import analyzeCube.twophase.cubie as cubie


def test(n, t):
    """
    Generate n random cubes and solve them with the two-phase solver.
    
    :param n: Number of random cubes
    :param t: Maximum time in seconds for each cube to find an optimal solution
    :return: Tuple with average move count and dict of move counts
    """
    cc = cubie.CubieCube()
    cnt = [0] * 31  # counts for 0..30 moves

    total_moves = 0
    for i in range(n):
        cc.randomize()
        fc = cc.to_facelet_cube()
        s = fc.to_string()
        print("Cube string:", s)

        # Solve with maxDepth=31 for optimal search
        q = sv.solve(s, 31, t)
        print("Solution:", q)

        # Count moves robustly
        moves = len(q.split())  # split by spaces
        total_moves += moves

        # Cap moves at 30 for statistics
        index = min(moves, 30)
        cnt[index] += 1

        print(f"Moves counted: {moves}\n")

    avr = total_moves / n
    return f'average {avr:.2f} moves', dict(zip(range(31), cnt))

# test results on AMD Ryzen 7 3700X 3.59 GHz:

# Standard CPython
# test(1000,30): {14: 0, 15: 2, 16: 12, 17: 74, 18: 279, 19: 534, 20: 99, 21: 0}, average 18.63 moves
# test(1000,10): {14: 0, 15: 1, 16: 8, 17: 51, 18: 242, 19: 532, 20: 166, 21: 0}, average 18.79 moves
# test(1000,1): {14: 0, 15: 2, 16: 4, 17: 28, 18: 127, 19: 401, 20: 405, 21: 33, 22: 0}, average 19.27 moves
# test(10000,1): {13: 0, 14: 1, 15: 2, 16: 54, 17: 251, 18: 1295, 19: 4047, 20: 4004, 21: 346, 22: 0}, avrg 19.27 moves
# test(1000,0.1): {15: 0, 16: 2, 17: 6, 18: 46, 19: 186, 20: 451, 21: 293, 22: 16, 23: 0}, average 20.02 moves

# PyPy (pypy3) with Just-in-Time compiler
# test(1000,10): {14: 0, 15: 1, 16: 11, 17: 100, 18: 423, 19: 433, 20: 32, 21: 0}, average 18.37 moves
# test(1000,1): {14: 0, 15: 1, 16: 10, 17: 49, 18: 259, 19: 535, 20: 145, 21: 1, 22: 0}, average 18.76 moves
# test(1000,0.1): {15: 0, 16: 4, 17: 23, 18: 100, 19: 429, 20: 401, 21: 43, 22: 0}, average 19.33 moves
# test(1000,0.01): {16: 0, 17: 1, 18: 25, 19: 95, 20: 349, 21: 461, 22: 69, 23: 0}, average 20.45 moves


# For comparison: Tomas Rokicki 2010 solved 1.000.000 random cubes *optimally* on a machine with 256 GB of RAM
# {11: 0, 12: 1, 13: 14, 14: 172, 15: 2063, 16: 26448, 17: 267027, 18: 670407, 19: 33868, 20: 0}, average 17.71 moves

def getCubeString():
    cc = cubie.CubieCube()
    cc.randomize()
    fc = cc.to_facelet_cube()
    s = fc.to_string()
    return s