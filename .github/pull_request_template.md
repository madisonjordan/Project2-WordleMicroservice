## PR Checklist

#### Tests

- [ ] tested services
  - [ ] functions working for this feature
  - [ ] autodocumentation works
- [ ] tested configuration
  - [ ] launches services
  - [ ] reverse proxy
  - [ ] load balancing

#### Design Requirements

- [ ] input/output representations in json format

- [ ] maintains statelessness (independent services)
  - [ ] separate python files for each service
  - [ ] doesn't store current day's answer on the server side
  - [ ] doesn't track number of guesses made by a client

#### Readability / Maintainability

- [ ] commented code
- [ ] follows PEP8 style / passes linting checks

## Description

Closes #...

#### Changes

-
