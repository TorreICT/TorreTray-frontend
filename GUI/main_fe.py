import sys
if len(sys.argv) > 1:
	sys.path.append(sys.argv[1])

from GUI.window import *
runGUI()
