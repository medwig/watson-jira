[![CircleCI](https://circleci.com/gh/medwig/watson-jira.svg?style=shield)](https://circleci.com/gh/medwig/watson-jira)

# Watson-Jira

Upload watson time logs to Jira from the CLI! Selects Watson time logs based on the configurable mapping rules, formats those logs to Tempo format, and uploads to the appropriate Jira tickets.
Will not double-write logs, and makes no local edits.

## Install

`$ pip install watson-jira`


## Setup

### JIRA Connection

Connection to JIRA can be configured in `~/.config/watson-jira/config.yaml`.

```
jira:
  server: XXX
  login: XXX
  # personalAccessToken: XXX
  # cookie: XXX
```

#### Auth with API token

1. Generate a Jira token: https://id.atlassian.com/manage/api-tokens#
2. Add this to config file :
```
  apitToken <<Jira Token>>
```
Replacing `<<Jira Token>>` with the token you copied from step 1.

#### Auth with Personal Access Token

TODO:

#### Auth with Cookie

TODO:


### Mapping rules

Mapping rules can be configured in `~/.config/watson-jira/mapping-rules.yaml`.
The precedence equal the order of listing.

#### Single issue

```
  - name: vacation
    description: 'Vacation'
    type: single_issue
    issue: JIRA-1
```

Logs containing tag matching the name of the mapping rule will be always synced to one specified JIRA ticket.

#### Issue per project

```
  - name: other
    description: 'Generic activities not related to any task in the current sprint.'
    type: issue_per_project
    projects:
      project1: JIRA-2
      project2: JIRA-3
```

Logs containing tag matching the name of the mapping rule will be synced to JIRA ticket resolved by project name.

#### Issue specified in the tag

```
  - name: sprint
    description: 'Activities performed in scope of sprint related to planned issues.'
    type: issue_specified_in_tag
```

Logs containing tag matching the name of the mapping rule will be synced to JIRA ticket which is specified also as a tag.

#### Issue specified in the project name

Logs of the project with name containing a JIRA ticket will be synced to the respective JIRA ticket.

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
