import sys
import subprocess
import pprint

import frame_parser
import jira_api

"""
Captures all arguments and passes them along to `Watson log --json`.
"""
args = ' '.join(sys.argv[1:])  # remove the name of the cli command itself
bash_cmd = "watson log --json {0}".format(args)
process = subprocess.Popen(bash_cmd.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
frames = output.decode('ascii')

print(bash_cmd)

local_worklogs = frame_parser.report_to_worklogs(frames)
# print(local_worklogs)

wl = local_worklogs[0]
jira_worklogs = jira_api.get_worklogs(wl['issue'])
pprint.pprint(wl)
print('='*100)
pprint.pprint(jira_worklogs)
