# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [1.14.0](https://github.com/cortexapps/cli/releases/tag/1.14.0) - 2026-04-02

<small>[Compare with 1.13.0](https://github.com/cortexapps/cli/compare/1.13.0...1.14.0)</small>

### Bug Fixes

- update GH Actions to Node 24 and fix dependabot security alerts ([7d2f482](https://github.com/cortexapps/cli/commit/7d2f4828210dedc1880a3730a0f57259fce3950f) by Jeff Schnitter).

## [1.13.0](https://github.com/cortexapps/cli/releases/tag/1.13.0) - 2026-04-02

<small>[Compare with 1.12.0](https://github.com/cortexapps/cli/compare/1.12.0...1.13.0)</small>

### Bug Fixes

- pass GH_TOKEN to checkout action for protected branch push ([7ad96e4](https://github.com/cortexapps/cli/commit/7ad96e4f3e3f9a5abd584059ca229058588c8a24) by Jeff Schnitter).

## [1.12.0](https://github.com/cortexapps/cli/releases/tag/1.12.0) - 2026-04-02

<small>[Compare with 1.11.0](https://github.com/cortexapps/cli/compare/1.11.0...1.12.0)</small>

### Bug Fixes

- use GH_TOKEN PAT for publish workflow git push to protected main branch ([ad8b16c](https://github.com/cortexapps/cli/commit/ad8b16c0ba1f6c4b7d671901e431b6fdaa4fa998) by Jeff Schnitter).

## [1.11.0](https://github.com/cortexapps/cli/releases/tag/1.11.0) - 2026-04-02

<small>[Compare with 1.10.0](https://github.com/cortexapps/cli/compare/1.10.0...1.11.0)</small>

### Features

- Add User-Agent header to CLI API requests (#195) ([8e94411](https://github.com/cortexapps/cli/commit/8e94411a9dc5b3e64d922ad148adcd234c6d187f) by Jeff Schnitter).
- add entity relationships API support with optimized backup/restore (#160) ([6fc38bb](https://github.com/cortexapps/cli/commit/6fc38bbf5a4fe994f3967b6c0aad3a379b5c20ac) by Jeff Schnitter).
- add support for Cortex Secrets API (#161) ([32c9f45](https://github.com/cortexapps/cli/commit/32c9f456e4dcde53b8df370f2e2b9ba45c9cbb8b) by Jeff Schnitter).

### Bug Fixes

- correct New Relic integration commands to match API (#192) ([a54f13a](https://github.com/cortexapps/cli/commit/a54f13aacebc54d8db3df0443da97600c8fa0eb1) by Jeff Schnitter).
- only retry on 429 rate limit errors, not 5xx server errors (#179) ([a037024](https://github.com/cortexapps/cli/commit/a037024672d7721d490c1f3cfca79e6e0399a289) by Jeff Schnitter).
- initialize results and failed_count before directory check in import functions (#178) ([b5f0c5a](https://github.com/cortexapps/cli/commit/b5f0c5a939cf15924ca46d2265513ff510c5251c) by Jeff Schnitter).
- change default logging level from INFO to WARNING (#177) ([d7e6963](https://github.com/cortexapps/cli/commit/d7e6963d6ba3157d1690b7288991502b337dd6b9) by Jeff Schnitter).
- only retry on 429 rate limit errors, not 5xx server errors ([b292e67](https://github.com/cortexapps/cli/commit/b292e67b1896c291b8bb63969ea97bf5a3d04d33) by Jeff Schnitter).
- initialize results and failed_count before directory check in import functions ([4165886](https://github.com/cortexapps/cli/commit/41658862455075d01c23be72432785d9e66c0afd) by Jeff Schnitter).
- change default logging level from INFO to WARNING ([8e58ea0](https://github.com/cortexapps/cli/commit/8e58ea0c94b4b077604d114618f21209f28a3e67) by Jeff Schnitter).
- remove rate limiter initialization log message (#168) ([5741d35](https://github.com/cortexapps/cli/commit/5741d355451a1f1ad1e658f1974cfeb6d1dfd559) by Jeff Schnitter).
- add client-side rate limiting and make tests idempotent (#165) #minor ([e54dca3](https://github.com/cortexapps/cli/commit/e54dca376e67a7dbc0059ff4f2f942014b308cf8) by Jeff Schnitter).

### Performance Improvements

- optimize test scheduling with --dist loadfile for 25% faster test runs ([0d99232](https://github.com/cortexapps/cli/commit/0d992320bdd9eecb2e0e86ebb3e7088ce81a9829) by Jeff Schnitter).

## [1.10.0](https://github.com/cortexapps/cli/releases/tag/1.10.0) - 2026-01-23

<small>[Compare with 1.9.0](https://github.com/cortexapps/cli/compare/1.9.0...1.10.0)</small>

## [1.9.0](https://github.com/cortexapps/cli/releases/tag/1.9.0) - 2026-01-12

<small>[Compare with 1.7.0](https://github.com/cortexapps/cli/compare/1.7.0...1.9.0)</small>

### Bug Fixes

- Update urllib3 to address CVE-2025-66418 and CVE-2025-66471 #patch (#188) ([4fba98b](https://github.com/cortexapps/cli/commit/4fba98bf12083faa030dfb84b2db325d55ae9afc) by Jeff Schnitter).

## [1.7.0](https://github.com/cortexapps/cli/releases/tag/1.7.0) - 2025-11-18

<small>[Compare with 1.6.0](https://github.com/cortexapps/cli/compare/1.6.0...1.7.0)</small>

## [1.6.0](https://github.com/cortexapps/cli/releases/tag/1.6.0) - 2025-11-13

<small>[Compare with 1.5.0](https://github.com/cortexapps/cli/compare/1.5.0...1.6.0)</small>

### Bug Fixes

- remove rate limiter initialization log message (#169) #patch ([015107a](https://github.com/cortexapps/cli/commit/015107aca15d5a4cf4eb746834bcbb7dac607e1d) by Jeff Schnitter).

## [1.5.0](https://github.com/cortexapps/cli/releases/tag/1.5.0) - 2025-11-13

<small>[Compare with 1.4.0](https://github.com/cortexapps/cli/compare/1.4.0...1.5.0)</small>

## [1.4.0](https://github.com/cortexapps/cli/releases/tag/1.4.0) - 2025-11-05

<small>[Compare with 1.3.0](https://github.com/cortexapps/cli/compare/1.3.0...1.4.0)</small>

### Code Refactoring

- remove unnecessary mock decorator from _get_rule helper function ([3e09a81](https://github.com/cortexapps/cli/commit/3e09a81e22ea3aed35ee780c605f108bf176b305) by Jeff Schnitter).
- separate trigger-evaluation test to avoid scorecard evaluation race conditions ([8c1ba4f](https://github.com/cortexapps/cli/commit/8c1ba4fcc0d106dacbc595ecc13a95cd6995fd8d) by Jeff Schnitter).

### Performance Improvements

- rename test_deploys.py to test_000_deploys.py for early scheduling ([f36aae2](https://github.com/cortexapps/cli/commit/f36aae22f56317cde70a6a9df56b097edb6a6117) by Jeff Schnitter).
- optimize test scheduling with --dist loadfile for 25% faster test runs (#157) ([8879fcf](https://github.com/cortexapps/cli/commit/8879fcfa7ee30a73f023e8bbef7d799808493319) by Jeff Schnitter).

## [1.3.0](https://github.com/cortexapps/cli/releases/tag/1.3.0) - 2025-11-04

<small>[Compare with 1.2.0](https://github.com/cortexapps/cli/compare/1.2.0...1.3.0)</small>

### Features

- improve backup import/export performance with parallel processing ([8a3b4d5](https://github.com/cortexapps/cli/commit/8a3b4d5308191c4d28ab78c4d8fab762a2713e95) by Jeff Schnitter).

### Bug Fixes

- add retry logic for scorecard create to handle active evaluations ([cc40b55](https://github.com/cortexapps/cli/commit/cc40b55ed9ef5af4146360b5a879afc6dc67fe06) by Jeff Schnitter).
- use json.dump instead of Rich print for file writing ([c66c2fe](https://github.com/cortexapps/cli/commit/c66c2fe438cc95f8343fbd4ba3cecae605c435ea) by Jeff Schnitter).
- ensure export/import output is in alphabetical order ([9055f78](https://github.com/cortexapps/cli/commit/9055f78cc4e1136da20e4e42883ff3c0f248825b) by Jeff Schnitter).
- ensure CORTEX_BASE_URL is available in publish workflow ([743579d](https://github.com/cortexapps/cli/commit/743579d760e900da693696df2841e7b710b08d39) by Jeff Schnitter).

### Performance Improvements

- add HTTP connection pooling to CortexClient for massive speedup ([6117eb3](https://github.com/cortexapps/cli/commit/6117eb3c2a8b3a9ced439a5953a84d06099b1c1e) by Jeff Schnitter).
- optimize backup export with increased parallelism and reduced API calls ([3bdd45a](https://github.com/cortexapps/cli/commit/3bdd45ab07a0aabc8c045d7cde63e6d9908c6e8a) by Jeff Schnitter).

## [1.2.0](https://github.com/cortexapps/cli/releases/tag/1.2.0) - 2025-11-04

<small>[Compare with 1.1.0](https://github.com/cortexapps/cli/compare/1.1.0...1.2.0)</small>

### Bug Fixes

- handle 409 Already evaluating in trigger-evaluation test ([6715ea8](https://github.com/cortexapps/cli/commit/6715ea8ace42e5e137b649daf927bf2bec225b5e) by Jeff Schnitter).
- remove entity_relationships imports from wrong branch ([3d467f6](https://github.com/cortexapps/cli/commit/3d467f699a0d4883316e039fcca571bde03d7f0a) by Jeff Schnitter).
- ensure base_url defaults correctly when not set ([cadf62e](https://github.com/cortexapps/cli/commit/cadf62e79c96fb6e89046d399d9247680e8057da) by Jeff Schnitter).

## [1.1.0](https://github.com/cortexapps/cli/releases/tag/1.1.0) - 2025-11-04

<small>[Compare with 1.0.6](https://github.com/cortexapps/cli/compare/1.0.6...1.1.0)</small>

## [1.0.6](https://github.com/cortexapps/cli/releases/tag/1.0.6) - 2025-10-31

<small>[Compare with 1.0.5](https://github.com/cortexapps/cli/compare/1.0.5...1.0.6)</small>

### Bug Fixes

- ensure base_url override is honored when parsing config file ([c9678e9](https://github.com/cortexapps/cli/commit/c9678e9e7203ba90822593688b772a57aea962dc) by Jeff Schnitter).

## [1.0.5](https://github.com/cortexapps/cli/releases/tag/1.0.5) - 2025-08-25

<small>[Compare with 1.0.4](https://github.com/cortexapps/cli/compare/1.0.4...1.0.5)</small>

### Bug Fixes

- correct end endpoint for adding multiple configurations ([8e325bb](https://github.com/cortexapps/cli/commit/8e325bbfd71a38f9d6ac4439276ad7eef8e34fff) by Jeff Schnitter).

## [1.0.4](https://github.com/cortexapps/cli/releases/tag/1.0.4) - 2025-08-01

<small>[Compare with 1.0.3](https://github.com/cortexapps/cli/compare/1.0.3...1.0.4)</small>

### Bug Fixes

- add sub-command needs to include tenant and password parameters ([6ea99a4](https://github.com/cortexapps/cli/commit/6ea99a426abb8a746cd8316c75a7eaa01c911c1c) by Jeff Schnitter).

## [1.0.3](https://github.com/cortexapps/cli/releases/tag/1.0.3) - 2025-06-19

<small>[Compare with 1.0.2](https://github.com/cortexapps/cli/compare/1.0.2...1.0.3)</small>

### Bug Fixes

- add get-personal sub-command ([e117047](https://github.com/cortexapps/cli/commit/e1170478ddc8185d081a2fb6e1ec186be4ee7747) by Jeff Schnitter).

## [1.0.2](https://github.com/cortexapps/cli/releases/tag/1.0.2) - 2025-06-16

<small>[Compare with 1.0.1](https://github.com/cortexapps/cli/compare/1.0.1...1.0.2)</small>

## [1.0.1](https://github.com/cortexapps/cli/releases/tag/1.0.1) - 2025-06-16

<small>[Compare with 1.0.0](https://github.com/cortexapps/cli/compare/1.0.0...1.0.1)</small>

## [1.0.0](https://github.com/cortexapps/cli/releases/tag/1.0.0) - 2025-06-13

<small>[Compare with 0.27.0](https://github.com/cortexapps/cli/compare/0.27.0...1.0.0)</small>

## [0.27.0](https://github.com/cortexapps/cli/releases/tag/0.27.0) - 2025-01-04

<small>[Compare with 0.26.7](https://github.com/cortexapps/cli/compare/0.26.7...0.27.0)</small>

## [0.26.7](https://github.com/cortexapps/cli/releases/tag/0.26.7) - 2024-11-18

<small>[Compare with 0.26.6](https://github.com/cortexapps/cli/compare/0.26.6...0.26.7)</small>

### Bug Fixes

- docker/Dockerfile to reduce vulnerabilities ([4c0ab3e](https://github.com/cortexapps/cli/commit/4c0ab3ea208ad4d07d87bc45c12bb08dab6cf3a3) by snyk-bot).

## [0.26.6](https://github.com/cortexapps/cli/releases/tag/0.26.6) - 2024-07-30

<small>[Compare with 0.26.5](https://github.com/cortexapps/cli/compare/0.26.5...0.26.6)</small>

### Bug Fixes

- docker/Dockerfile to reduce vulnerabilities ([778ec0f](https://github.com/cortexapps/cli/commit/778ec0f25bf19c35cca2d3e811c0fcba63c83685) by snyk-bot).

## [0.26.5](https://github.com/cortexapps/cli/releases/tag/0.26.5) - 2024-06-27

<small>[Compare with 0.26.4](https://github.com/cortexapps/cli/compare/0.26.4...0.26.5)</small>

## [0.26.4](https://github.com/cortexapps/cli/releases/tag/0.26.4) - 2024-06-26

<small>[Compare with 0.26.3](https://github.com/cortexapps/cli/compare/0.26.3...0.26.4)</small>

## [0.26.3](https://github.com/cortexapps/cli/releases/tag/0.26.3) - 2024-05-20

<small>[Compare with 0.26.2](https://github.com/cortexapps/cli/compare/0.26.2...0.26.3)</small>

## [0.26.2](https://github.com/cortexapps/cli/releases/tag/0.26.2) - 2024-05-08

<small>[Compare with 0.26.1](https://github.com/cortexapps/cli/compare/0.26.1...0.26.2)</small>

## [0.26.1](https://github.com/cortexapps/cli/releases/tag/0.26.1) - 2024-05-06

<small>[Compare with 0.26.0](https://github.com/cortexapps/cli/compare/0.26.0...0.26.1)</small>

## [0.26.0](https://github.com/cortexapps/cli/releases/tag/0.26.0) - 2024-05-06

<small>[Compare with 0.25.0](https://github.com/cortexapps/cli/compare/0.25.0...0.26.0)</small>

## [0.25.0](https://github.com/cortexapps/cli/releases/tag/0.25.0) - 2024-05-05

<small>[Compare with 0.24.3](https://github.com/cortexapps/cli/compare/0.24.3...0.25.0)</small>

## [0.24.3](https://github.com/cortexapps/cli/releases/tag/0.24.3) - 2024-04-26

<small>[Compare with 0.24.2](https://github.com/cortexapps/cli/compare/0.24.2...0.24.3)</small>

## [0.24.2](https://github.com/cortexapps/cli/releases/tag/0.24.2) - 2024-02-28

<small>[Compare with 0.24.1](https://github.com/cortexapps/cli/compare/0.24.1...0.24.2)</small>

## [0.24.1](https://github.com/cortexapps/cli/releases/tag/0.24.1) - 2024-02-14

<small>[Compare with 0.24.0](https://github.com/cortexapps/cli/compare/0.24.0...0.24.1)</small>

## [0.24.0](https://github.com/cortexapps/cli/releases/tag/0.24.0) - 2024-02-13

<small>[Compare with 0.23.0](https://github.com/cortexapps/cli/compare/0.23.0...0.24.0)</small>

## [0.23.0](https://github.com/cortexapps/cli/releases/tag/0.23.0) - 2024-02-05

<small>[Compare with 0.22.0](https://github.com/cortexapps/cli/compare/0.22.0...0.23.0)</small>

## [0.22.0](https://github.com/cortexapps/cli/releases/tag/0.22.0) - 2024-02-05

<small>[Compare with 0.21.0](https://github.com/cortexapps/cli/compare/0.21.0...0.22.0)</small>

## [0.21.0](https://github.com/cortexapps/cli/releases/tag/0.21.0) - 2024-01-25

<small>[Compare with 0.20.0](https://github.com/cortexapps/cli/compare/0.20.0...0.21.0)</small>

## [0.20.0](https://github.com/cortexapps/cli/releases/tag/0.20.0) - 2024-01-22

<small>[Compare with 0.19.0](https://github.com/cortexapps/cli/compare/0.19.0...0.20.0)</small>

## [0.19.0](https://github.com/cortexapps/cli/releases/tag/0.19.0) - 2023-12-21

<small>[Compare with 0.18.0](https://github.com/cortexapps/cli/compare/0.18.0...0.19.0)</small>

## [0.18.0](https://github.com/cortexapps/cli/releases/tag/0.18.0) - 2023-12-19

<small>[Compare with 0.17.0](https://github.com/cortexapps/cli/compare/0.17.0...0.18.0)</small>

## [0.17.0](https://github.com/cortexapps/cli/releases/tag/0.17.0) - 2023-12-06

<small>[Compare with 0.16.0](https://github.com/cortexapps/cli/compare/0.16.0...0.17.0)</small>

## [0.16.0](https://github.com/cortexapps/cli/releases/tag/0.16.0) - 2023-12-06

<small>[Compare with 0.15.0](https://github.com/cortexapps/cli/compare/0.15.0...0.16.0)</small>

## [0.15.0](https://github.com/cortexapps/cli/releases/tag/0.15.0) - 2023-12-05

<small>[Compare with 0.14.0](https://github.com/cortexapps/cli/compare/0.14.0...0.15.0)</small>

## [0.14.0](https://github.com/cortexapps/cli/releases/tag/0.14.0) - 2023-12-04

<small>[Compare with 0.13.0](https://github.com/cortexapps/cli/compare/0.13.0...0.14.0)</small>

## [0.13.0](https://github.com/cortexapps/cli/releases/tag/0.13.0) - 2023-11-30

<small>[Compare with 0.12.0](https://github.com/cortexapps/cli/compare/0.12.0...0.13.0)</small>

## [0.12.0](https://github.com/cortexapps/cli/releases/tag/0.12.0) - 2023-11-30

<small>[Compare with 0.11.0](https://github.com/cortexapps/cli/compare/0.11.0...0.12.0)</small>

## [0.11.0](https://github.com/cortexapps/cli/releases/tag/0.11.0) - 2023-11-27

<small>[Compare with 0.10.0](https://github.com/cortexapps/cli/compare/0.10.0...0.11.0)</small>

## [0.10.0](https://github.com/cortexapps/cli/releases/tag/0.10.0) - 2023-11-21

<small>[Compare with 0.9.0](https://github.com/cortexapps/cli/compare/0.9.0...0.10.0)</small>

## [0.9.0](https://github.com/cortexapps/cli/releases/tag/0.9.0) - 2023-11-21

<small>[Compare with 0.8.0](https://github.com/cortexapps/cli/compare/0.8.0...0.9.0)</small>

## [0.8.0](https://github.com/cortexapps/cli/releases/tag/0.8.0) - 2023-11-19

<small>[Compare with 0.7.0](https://github.com/cortexapps/cli/compare/0.7.0...0.8.0)</small>

## [0.7.0](https://github.com/cortexapps/cli/releases/tag/0.7.0) - 2023-11-17

<small>[Compare with 0.6.0](https://github.com/cortexapps/cli/compare/0.6.0...0.7.0)</small>

## [0.6.0](https://github.com/cortexapps/cli/releases/tag/0.6.0) - 2023-11-16

<small>[Compare with 0.5.0](https://github.com/cortexapps/cli/compare/0.5.0...0.6.0)</small>

## [0.5.0](https://github.com/cortexapps/cli/releases/tag/0.5.0) - 2023-11-13

<small>[Compare with 0.4.0](https://github.com/cortexapps/cli/compare/0.4.0...0.5.0)</small>

## [0.4.0](https://github.com/cortexapps/cli/releases/tag/0.4.0) - 2023-11-13

<small>[Compare with 0.3.0](https://github.com/cortexapps/cli/compare/0.3.0...0.4.0)</small>

## [0.3.0](https://github.com/cortexapps/cli/releases/tag/0.3.0) - 2023-11-07

<small>[Compare with 0.2.0](https://github.com/cortexapps/cli/compare/0.2.0...0.3.0)</small>

## [0.2.0](https://github.com/cortexapps/cli/releases/tag/0.2.0) - 2023-11-07

<small>[Compare with 0.1.0](https://github.com/cortexapps/cli/compare/0.1.0...0.2.0)</small>

## [0.1.0](https://github.com/cortexapps/cli/releases/tag/0.1.0) - 2023-11-05

<small>[Compare with 0.0.5](https://github.com/cortexapps/cli/compare/0.0.5...0.1.0)</small>

## [0.0.5](https://github.com/cortexapps/cli/releases/tag/0.0.5) - 2023-11-04

<small>[Compare with first commit](https://github.com/cortexapps/cli/compare/c1de1ad2bf64e156246c6806e2d57ee3b03b3d1b...0.0.5)</small>

