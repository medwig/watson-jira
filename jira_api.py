from pprint import pprint
from datetime import datetime
from jira import JIRA


jira = JIRA({'server':'https://skywatch.atlassian.net'})
uname = 'jon@skywatch.co'
password = 'WJmIkdCTHsQhq61BOjEl5102'
server = 'https://skywatch.atlassian.net'
issue = 'OO-762'
time_spent = '1.5m'
comment = 'comment_test_test'
started = datetime(2006, 11, 21, 16, 30)

#jira = JIRA(basic_auth=(uname, password), options={'server': server})

issue = jira.issue(issue)
for worklog in issue.fields.worklog.worklogs:
    pprint(vars(worklog))
# pprint(dir(jira))
#wl = jira.add_worklog(
#    issue,
#    timeSpent=time_spent,
#    comment=comment,
#    started=started
#)
#print(wl)
