# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [1.22.0](https://github.com/cortexapps/cli/releases/tag/1.22.0) - 2026-07-14

<small>[Compare with 1.21.1](https://github.com/cortexapps/cli/compare/1.21.1...1.22.0)</small>

### Features

- show README after install by default (--no-info to suppress); update github-starter README with install instructions ([4b996c2](https://github.com/cortexapps/cli/commit/4b996c271127cbb4217df9aab7f420492963cb6b) by Jeff Schnitter).
- add solutions install command ([a6a21a7](https://github.com/cortexapps/cli/commit/a6a21a7362506ae744e8fce28d356eac9fb7c651) by Jeff Schnitter).
- add solutions info command ([de17360](https://github.com/cortexapps/cli/commit/de173603d9f459052e1cff9e714db027d2f7ada6) by Jeff Schnitter).
- add solutions list command ([02655a1](https://github.com/cortexapps/cli/commit/02655a1c984771a7de099a3a83c5c6a79bfe0e6f) by Jeff Schnitter).
- add solutions command skeleton, cli wiring, and auth bypass ([0018115](https://github.com/cortexapps/cli/commit/001811573fda9702276d631fc67aa681766ef1b4) by Jeff Schnitter).
- add solutions package scaffold with github-starter bundle ([8c010d7](https://github.com/cortexapps/cli/commit/8c010d7a005a5dbe1041ea2663794060d5900d61) by Jeff Schnitter).

### Bug Fixes

- render code blocks as cyan text instead of Rich dark panels in solutions info ([ef8c766](https://github.com/cortexapps/cli/commit/ef8c766c2325753fd439a16f426cf192ac6a07d4) by Jeff Schnitter).
- strip frontmatter and left-justify headings in solutions info ([485a061](https://github.com/cortexapps/cli/commit/485a061623aa0749f06c7e0970a2c58a6efca9c3) by Jeff Schnitter).
- handle missing api_key in config section in _build_client ([9b140a7](https://github.com/cortexapps/cli/commit/9b140a71d355ba6dd486507a37d06508d24d0230) by Jeff Schnitter).

## [1.21.1](https://github.com/cortexapps/cli/releases/tag/1.21.1) - 2026-07-14

<small>[Compare with 1.21.0](https://github.com/cortexapps/cli/compare/1.21.0...1.21.1)</small>

### Bug Fixes

- convert deploy timestamps to UTC before sending #patch ([685811e](https://github.com/cortexapps/cli/commit/685811e3dacdd6c7f20f71efce3778edc7cec569) by Hanna Vigil).

## [1.21.0](https://github.com/cortexapps/cli/releases/tag/1.21.0) - 2026-07-07

<small>[Compare with 1.20.1](https://github.com/cortexapps/cli/compare/1.20.1...1.21.0)</small>

### Features

- add login command, alphabetize help, remove workflows Beta label ([a89c6c7](https://github.com/cortexapps/cli/commit/a89c6c7e85479bb116eda3bfb6f657b888f186db) by Jeff Schnitter).

## [1.20.1](https://github.com/cortexapps/cli/releases/tag/1.20.1) - 2026-07-06

<small>[Compare with 1.20.0](https://github.com/cortexapps/cli/compare/1.20.0...1.20.1)</small>

### Bug Fixes

- two-pass re-import for catalog entities with x-cortex-relationships #patch ([1d75640](https://github.com/cortexapps/cli/commit/1d75640f3ac6314f9723c12d9434747aa8c93d4b) by Jeff Schnitter).

## [1.20.0](https://github.com/cortexapps/cli/releases/tag/1.20.0) - 2026-06-11

<small>[Compare with 1.19.2](https://github.com/cortexapps/cli/compare/1.19.2...1.20.0)</small>

### Features

- add integration tests for users roles list ([ef639c6](https://github.com/cortexapps/cli/commit/ef639c6c49a6de44e38c9c72e4d84754af4c5e8a) by Jeff Schnitter).
- add users roles list command ([52013c9](https://github.com/cortexapps/cli/commit/52013c981a38236e8a381b7c069b5f067cbdadba) by Jeff Schnitter).

### Bug Fixes

- add explicit pytest import to test_users.py ([517b60a](https://github.com/cortexapps/cli/commit/517b60a48ee1977c575c840a81e90faf92c1f793) by Jeff Schnitter).

## [1.19.2](https://github.com/cortexapps/cli/releases/tag/1.19.2) - 2026-06-10

<small>[Compare with 1.19.1](https://github.com/cortexapps/cli/compare/1.19.1...1.19.2)</small>

### Bug Fixes

- update Docker base image for CVE-2026-45447 and add docker/ to publish triggers #patch ([1bcef87](https://github.com/cortexapps/cli/commit/1bcef8718845cad9b15094a764392c5dcaa8804e) by Jeff Schnitter).

## [1.19.1](https://github.com/cortexapps/cli/releases/tag/1.19.1) - 2026-06-09

<small>[Compare with 1.19.0](https://github.com/cortexapps/cli/compare/1.19.0...1.19.1)</small>

### Bug Fixes

- remove invalid RST transition that breaks PyPI rendering #patch ([00e2d96](https://github.com/cortexapps/cli/commit/00e2d96500ddfb9325d8db8075612af4a0489d58) by Jeff Schnitter).

## [1.19.0](https://github.com/cortexapps/cli/releases/tag/1.19.0) - 2026-06-01

<small>[Compare with 1.18.0](https://github.com/cortexapps/cli/compare/1.18.0...1.19.0)</small>

### Bug Fixes

- resolve Python 3.14 crash from builtin list shadowing in custom_events ([95e3f79](https://github.com/cortexapps/cli/commit/95e3f7960fc02ab6299cd765bafe39946f8fa847) by Jeff Schnitter).

## [1.18.0](https://github.com/cortexapps/cli/releases/tag/1.18.0) - 2026-06-01

<small>[Compare with 1.17.0](https://github.com/cortexapps/cli/compare/1.17.0...1.18.0)</small>

### Features

- add Python 3.14 support and update CI to test on 3.14 by default ([90c5654](https://github.com/cortexapps/cli/commit/90c56540c3034cb29212cbd1c06eb7a8eb4073b0) by Jeff Schnitter).

### Bug Fixes

- pin safety<3.8.0 to fix broken poetry audit in CI ([f706a6c](https://github.com/cortexapps/cli/commit/f706a6c0bb384f689eab7dbc14d1b0602cc62db2) by Jeff Schnitter).
- update idna to 3.17 to address CVE bypass (Dependabot #22) ([cb60c3c](https://github.com/cortexapps/cli/commit/cb60c3cbaf281b4b80e25e0d328209d300366d50) by Jeff Schnitter).

## [1.17.0](https://github.com/cortexapps/cli/releases/tag/1.17.0) - 2026-05-20

<small>[Compare with 1.16.0](https://github.com/cortexapps/cli/compare/1.16.0...1.17.0)</small>

### Features

- add CLI support for 32 new integrations ([58c8960](https://github.com/cortexapps/cli/commit/58c8960c0359b25c49084a399f49dbb210a78507) by Jeff Schnitter).

## [1.16.0](https://github.com/cortexapps/cli/releases/tag/1.16.0) - 2026-05-14

<small>[Compare with 1.15.0](https://github.com/cortexapps/cli/compare/1.15.0...1.16.0)</small>

### Features

- shared minikube cluster, env prompting, cortex deploy recipes ([ff7c67d](https://github.com/cortexapps/cli/commit/ff7c67db11b47c32be7018b1f8660d9e7e148ed7) by Jeff Schnitter).
- add Cortex Helm values and env vars for minikube deploy ([23a8994](https://github.com/cortexapps/cli/commit/23a89943e20164c73630fdaee0071cd88cc553f9) by Jeff Schnitter).
- consolidate internal tooling — axon, k8s, prometheus, ui, functional tests ([1fd70fe](https://github.com/cortexapps/cli/commit/1fd70fe5b212516704e91e0022c10e6c6c3aed3c) by Jeff Schnitter).
- add ske-setup, ske-test, and ske-stop Justfile recipes ([6f56dca](https://github.com/cortexapps/cli/commit/6f56dca1afcd48ebc23fe3cf5a70bc2760b60257) by Jeff Schnitter).
- add SKE Helm values and ArgoCD Application manifest ([3d83ca5](https://github.com/cortexapps/cli/commit/3d83ca567861c64cea08d2dedee545fee0aff278) by Jeff Schnitter).
- add ConfigMap Promise for SKE Cortex integration test ([7942967](https://github.com/cortexapps/cli/commit/7942967b83eb121fbd2ec606a14dfd86c5a73036) by Jeff Schnitter).
- add SKE directory structure and env config ([dc0cd54](https://github.com/cortexapps/cli/commit/dc0cd54e6126bc4e5f3498db85f7cf862ea261c2) by Jeff Schnitter).

### Bug Fixes

- add __init__.py to trigger publish workflow for urllib3 update ([854dcb0](https://github.com/cortexapps/cli/commit/854dcb00b534df21b6a1976c7a4e79fca613f246) by Jeff Schnitter).
- update urllib3 to 2.7.0 to resolve high-severity CVEs ([904a144](https://github.com/cortexapps/cli/commit/904a144e02e65067f2029d85baa5efdf83c535f6) by Jeff Schnitter).
- prompt for env vars before starting minikube ([3da7a87](https://github.com/cortexapps/cli/commit/3da7a870853591f48f0eb3e80013e0d6573f9f62) by Jeff Schnitter).
- review fixes — quote .env values, fix pod selector, remove dead PID files ([4931dae](https://github.com/cortexapps/cli/commit/4931daed4e8a10ab6b9842d6aa70e6b4ce81c94b) by Jeff Schnitter).
- use external script for env prompting to fix just quoting bug ([5816d65](https://github.com/cortexapps/cli/commit/5816d65c7ca55834b7eb0a1e819b5192d2463853) by Jeff Schnitter).
- use correct Cortex API endpoint for Entity Type check in ske-test ([94f774e](https://github.com/cortexapps/cli/commit/94f774e43d7849175224794cfd8c8d7744b6c925) by Jeff Schnitter).
- wait for cert-manager webhook CA, let SKE auto-create Destination ([a4983fe](https://github.com/cortexapps/cli/commit/a4983fe75946c37e2eb582098a21754a10c498c8) by Jeff Schnitter).
- update SKE recipes with GitStateStore, Destination, and git-based resource requests ([8dad6be](https://github.com/cortexapps/cli/commit/8dad6bea12ff52011a2cbe1f15898d2eb91f9ad7) by Jeff Schnitter).
- correct SKE setup — add cert-manager, use latest version, fix integrationAlias ([4e1d2d7](https://github.com/cortexapps/cli/commit/4e1d2d74a096da9d6ff28e4cbedb7c6c50b4d8d6) by Jeff Schnitter).
- indent inline Python in ske-test recipe for just compatibility ([8a57c3c](https://github.com/cortexapps/cli/commit/8a57c3c21a10795baa1a59ca290af14f018ff813) by Jeff Schnitter).

## [1.15.0](https://github.com/cortexapps/cli/releases/tag/1.15.0) - 2026-04-15

<small>[Compare with 1.14.0](https://github.com/cortexapps/cli/compare/1.14.0...1.15.0)</small>

### Features

- pytest CVE fix, beta label updates, test improvements ([9cbe2a0](https://github.com/cortexapps/cli/commit/9cbe2a0335a55eb098ab7fb243340d4de69a07cb) by Jeff Schnitter).
- add env var checks for functional tests in Justfile ([ea3036c](https://github.com/cortexapps/cli/commit/ea3036c1ac3073845e0d8d97b0dc3f85a4c4b7a0) by Jeff Schnitter).
- add list-branches functional test ([3d9b9b6](https://github.com/cortexapps/cli/commit/3d9b9b6d27416ef61d26f91bbfd04dec87a61816) by Jeff Schnitter).
- add functional test data import test ([efddc65](https://github.com/cortexapps/cli/commit/efddc65e0d4a43e17fefe65be37c42e299cc3a1f) by Jeff Schnitter).
- add session fixtures for functional tests ([ea6b2c0](https://github.com/cortexapps/cli/commit/ea6b2c0fb77d51ce07eb2c13d64978938046e6bf) by Jeff Schnitter).
- add GitHub helper functions for functional tests ([8874ac0](https://github.com/cortexapps/cli/commit/8874ac0c6b839ee679fd5f01e83d3c1aef6c77e1) by Jeff Schnitter).
- add list-branches workflow YAML for functional tests ([f0310ac](https://github.com/cortexapps/cli/commit/f0310ac16a7e0db6d1013731ff8f86337913eae0) by Jeff Schnitter).
- add cortex workflows get-run command ([88d92cc](https://github.com/cortexapps/cli/commit/88d92cc774dcc143bbd3b4ae4edd0ca8ea258426) by Jeff Schnitter).
- add cortex workflows run command ([c1519dc](https://github.com/cortexapps/cli/commit/c1519dca44dec00159f5efb1127e0acb1dc8ea46) by Jeff Schnitter).
- add functional test infrastructure for GitHub workflow action blocks ([d0c0ecc](https://github.com/cortexapps/cli/commit/d0c0ecce027d171e45b096970451ebfed4f28c65) by Jeff Schnitter).

### Bug Fixes

- use configurable GITHUB_INTEGRATION_ALIAS and assert import success ([24851a7](https://github.com/cortexapps/cli/commit/24851a7114d270ca32c48f83a9ee8058989928d6) by Jeff Schnitter).
- remove publish.yml from paths trigger to prevent accidental releases ([4b8a71e](https://github.com/cortexapps/cli/commit/4b8a71ecaf7492dcbb37d5fd568a1024d8778fa1) by Jeff Schnitter).

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

