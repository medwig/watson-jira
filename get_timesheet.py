# > Authorization: Basic am9uQHNreXdhdGNoLmNvOldKbUlrZENUSHNRaHE2MUJPakVsNTEwMg==

# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
import json

url = "https://skywatch.atlassian.net/rest/api/2/issue/OO-760/worklog"

headers = {
   "Accept": "application/json",
   "Content-Type": "application/json",
   "Bearer": "jon@skywatch.co:WJmIkdCTHsQhq61BOjEl5102"
}

payload = json.dumps({
  "comment": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "Rest api test log."
          }
        ]
      }
    ]
  },
  "visibility": {
    "type": "group",
    "value": "jira-developers"
  },
  "started": "2018.11.20 10:01:14-0500",
  "timeSpentSeconds": 10
})

uname = 'jon@skywatch.co'
password = 'WJmIkdCTHsQhq61BOjEl5102' 

response = requests.request(
   "GET",
   url,
   data=payload,
   auth=(uname, password)
)

print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
