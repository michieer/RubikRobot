#!/usr/bin/env python3

import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from moveCube.handles import home

home()
