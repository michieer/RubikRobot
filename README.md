# RubikRobot
Python code to solve a 3x3x3 rubik's cube

I build a robot from https://www.rcr3d.com/ 
This project is my attempt to create a python gui application to scan and solve the cube.

I used two projects from dwalton76
https://github.com/dwalton76/rubiks-cube-tracker
https://github.com/dwalton76/rubiks-color-resolver

And the solution from hkociemba to solve every cube in max 19 moves
https://github.com/hkociemba/RubiksCube-TwophaseSolver

I want to optimise the code to only solve 3x3x3 cubes but it needs to do that in different lighting conditions. Now the colors don't match when light is a bit dim.

Code from rubiks-cube-tracker is modified to not identify 9 squares. As the camear is in the robot with the cube the image is trimmed to the cube by default. Then the cube is divided in 9 surfaces with a border to only use clean colored surfaces.

The UI consists of two pages. The initial page will take pictures of all sides and analyze them to find the solution.
The second page is to calibrate the servos for the right position.

I updated the grippers and the camera holder from the rcr3d model to better fit.