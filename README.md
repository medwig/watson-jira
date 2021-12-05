[![CircleCI](https://circleci.com/gh/PrimaMateria/watson-jira-next/tree/master.svg?style=svg)](https://circleci.com/gh/PrimaMateria/watson-jira-next/tree/master)

# Watson-Jira

Upload Watson time logs to Jira from the CLI! Selects Watson time logs based on the configurable mapping rules, formats those logs to Tempo format, and uploads to the appropriate Jira issues.
Will not double-write logs, and makes no local edits.

## Install

`$ pip install watson-jira`


## Config

Config is stored in `$XDG_CONFIG_HOME/.config/watson-jira/config.yaml`.

### JIRA

`jira` section should contain JIRA base URL and one of the authentication methods.

```
server: <<JIRA base URL>>
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

1. login to JIRA in the browser
1. open Network tab in the developer tools
1. copy the cookie from the request header 
1. add the following to the config file:

```
cookie: <<cookie>>
```

### Mappings 

`mappings` section contains list of mapping rules.

Mapping rule has name and type. For each Watson log, **Watson-Jira** tries to find the name in the tags. If found, then the JIRA issue number is resolved according to the type definition.

Mapping precedence is of the following order:

#### Single issue

```
name: vacation
type: single_issue
issue: JIRA-1
```

This type always returns the one specified JIRA issue number.

**Watson example:** `watson add -f 10:00 -t 18:00 none +vacation`

#### Issue per project

```
name: maintenance
type: issue_per_project
projects:
  project1: JIRA-2
  project2: JIRA-3
```

This type returns JIRA issue number based on the project name.

**Watson example:** `watson add -f 10:00 -t 11:00 project2 +maintenance +dependencies-upgrade`

#### Issue specified in the tag

```
name: sprint
type: issue_specified_in_tag
```

This type resolves the JIRA issue number from the first tag which matches the issue number regex.

**Example:** `watson add -f 10:00 -t 11:00 project1 +sprint +JIRA-123 +code`

#### Issue specified in the project name

For any Watson log, which doesn't match any of the mappings, the JIRA issue number will be tried to be resolved from the project name.

**Watson example:** `watson add -f 10:00 -t 11:00 JIRA-123 +investigation`

### Full config example

```
jira:
  server: http://localhost:8080
  cookie: atlassian.xsrf.token=BEHZ-5GE9-RXNS-7J78_bfa98881ae96448d36fdaa94f2b3ac6b8f205885_lout; JSESSIONID=51D8547A4C356A8355F8FDAF7CC97D51
mappings:
  - name: sprint
    type: issue_specified_in_tag
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

#### Show Jira-specific logs from today

`$ watson-jira logs --jira-only --tempo-format`

#### Show existing work logs for a Jira issue

`$ watson-jira logs tempo --issue JIRA-1`

#### Upload logs from today interactively

`$ watson-jira sync --from 3 --interactive`

#### Upload logs from the last 3 days

`$ watson-jira sync --from 3`

#### Help

`$ watson-jira --help`

Will install TD-Watson https://github.com/TailorDev/Watson as one of its dependencies, not surprisingly.
