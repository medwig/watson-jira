[![CircleCI](https://circleci.com/gh/medwig/watson-jira.svg?style=shield)](https://circleci.com/gh/medwig/watson-jira)

# Watson-Jira

Upload watson time logs to Jira from the CLI! Selects Watson time logs whose project name matches
a Jira naming regex, formats those logs to Tempo format, and uploads to the appropriate Jira tickets.
Will not double-write logs, and makes no local edits.

## Install

`$ pip install watson-jira`


## Setup

API access to Jira needs to be enabled, this can be done one of 2 ways:

##### Guided:

`$ watson-jira init`

##### Manual:

1. Generate a Jira token: https://id.atlassian.com/manage/api-tokens#
2. Add this to `~/.netrc`:
```
	machine yoururl.atlassian.net
	login yourjiraemail@company.com
	password <<Jira Token>>
```
Replacing `<<Jira Token>>` with the token you copied from step 1.

The library will read `~/.netrc`, no further config needed!


## Usage

#### Show Jira-specific logs from today

`$ watson-jira logs --jira-only --tempo-format`


#### Show exixting worklogs for a Jira issue

`$ watson-jira logs tempo --issue JI-101`


#### Upload logs from the last 3 days

`$ watson-jira sync --from 3`


#### Help

`$ watson-jira --help`


Will install TD-Watson https://github.com/TailorDev/Watson as one of it's dependencies, not surprisingly.
