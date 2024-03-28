import os
import sys
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))

from utils.function import analyze

analyze()