
"""Test harness for  run.py  that traps all Python errors before quitting:"""

# to run an external program from within Python code do this:
# import subprocess
# subprocess.call(["path/program-name", "param1", "param2", ...])
# e.g.,   subprocess.call(["C:/Python26/Python.exe", "p.py"])

#progname = raw_input("Type name of Python program: ")
#subprocess.call(["Python.exe", progname + ".py"])
 
import subprocess         # imports Python utility module 
subprocess.call(["Python.exe", "run.py"])

raw_input("\nPress Enter key to finish")

