[![CircleCI](https://circleci.com/gh/medwig/watson-jira/tree/master.svg?style=svg)](https://circleci.com/gh/medwig/watson-jira/tree/master)

# Watson-Jira

Upload Watson time logs to Jira from the CLI! Selects Watson time logs based on the configurable mapping rules, formats those logs to Tempo format, and uploads to the appropriate Jira issues.
Will not double-write logs, and makes no local edits.

## Install

`$ pip install watson-jira`

## Quickstart

1. Set up Jira authentication:
   `watson-jira init`
2. Create a watson log with a Jira issue number in the tags:
   `watson add -f 10:00 -t 11:00 project1 +sprint +JIRA-123 +code`
3. Sync the logs to Jira:
   `watson-jira sync`

## Config

Config is stored in `$XDG_CONFIG_HOME/.config/watson-jira/config.yaml`.

### Jira

`jira` section should contain Jira base URL and one of the authentication methods.

```
server: <<Jira base URL>>
```

#### Auth: API token

See [Atlassian docs](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/). Add the following to the config file:

```
email: <<email>>
apiToken: <<API token>>
```

#### Auth: Personal Access Token

See [Atlassian docs](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html). Add the following to the config file:

```
personalAccessToken: <<PAT>>
```

#### Auth: Cookie

1. login to Jira in the browser
2. open Network tab in the developer tools
3. copy the cookie from the request header
4. add the following to the config file:

```
cookie: <<cookie>>
```

### Mappings

`mappings` section contains list of mapping rules.

Mapping rule has name and type. For each Watson log, **Watson-Jira** tries to find the name in the tags. If found, then the Jira issue number is resolved according to the type definition.

Mapping precedence is of the following order:

#### Single issue

```
name: vacation
type: single_issue
issue: JIRA-1
```

This type always returns the one specified Jira issue number.

**Watson example:** `watson add -f 10:00 -t 18:00 none +vacation`

#### Issue per project

```
name: maintenance
type: issue_per_project
projects:
  project1: JIRA-2
  project2: JIRA-3
```

This type returns Jira issue number based on the project name.

**Watson example:** `watson add -f 10:00 -t 11:00 project2 +maintenance +dependencies-upgrade`

#### Issue specified in the tag

If no mapping is set then it will default to resolving the Jira issue number from the first tag which matches the issue number regex.

**Watson example:** `watson add -f 10:00 -t 11:00 project1 +sprint +JIRA-123 +code`

#### Issue specified in the project name

For any Watson log, which doesn't match any of the mappings, the Jira issue number will be tried to be resolved from the project name.
If the Jira issue number is set in both the project name _and_ in a tag then the project name will be used.
Jira issue numbers are intended to be set in the tags, this behaviour is here for backwards compatibility.

**Watson example:** `watson add -f 10:00 -t 11:00 JIRA-123 +investigation`
**Watson example:** `watson add -f 10:00 -t 11:00 JIRA-123 +investigation +JIRA-2`
--> JIRA-123 will be used, not JIRA-2, since the project name takes precedence.

### Full config example

```
jira:
  server: http://localhost:8080
  cookie: atlassian.xsrf.token=<redacted>; JSESSIONID=<redacted>
mappings:
  - name: vacation
    type: single_issue
    issue: HR-123
  - name: maintenance
    type: issue_per_project
    projects:
      project1: JIRA-1
      project2: JIRA-2
```

## Usage

#### Show Watson logs from today

`$ watson-jira logs`

#### Show Watson logs in Jira Tempo format

`$ watson-jira logs --tempo-format`

#### Upload logs from today to Jira

`$ watson-jira sync`

#### Upload logs from last 3 days interactively

`$ watson-jira sync --from 3 --interactive`

#### Delete Jira tempo logs for an issue

`$ watson-jira delete --issue FOO-1`

Note that this will delete all Jira worklogs for the issue, not just the ones synced by Watson-Jira. It will _not_ delete any Watson logs, Watson-Jira is readonly for Watson logs.

#### Help

`$ watson-jira --help`

Will install TD-Watson https://github.com/TailorDev/Watson as one of its dependencies, not surprisingly.
