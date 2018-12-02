import sys
import subprocess

"""
Captures all arguments and passes them along to `Watson log --json`.
"""
args = ' '.join(sys.argv[1:])  # remove the name of the cli command itself
bash_cmd = "watson log --json {0}".format(args)
process = subprocess.Popen(bash_cmd.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
output = output.decode('ascii')


