# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [1.0.5](https://github.com/cortexapps/cli/releases/tag/1.0.5) - 2025-08-25

<small>[Compare with 1.0.4](https://github.com/cortexapps/cli/compare/1.0.4...1.0.5)</small>

### Fixed

- fix: correct end endpoint for adding multiple configurations ([8e325bb](https://github.com/cortexapps/cli/commit/8e325bbfd71a38f9d6ac4439276ad7eef8e34fff) by Jeff Schnitter).

## [1.0.4](https://github.com/cortexapps/cli/releases/tag/1.0.4) - 2025-08-01

<small>[Compare with 1.0.3](https://github.com/cortexapps/cli/compare/1.0.3...1.0.4)</small>

### Added

- Add "Export all workflows" ([05aa7b1](https://github.com/cortexapps/cli/commit/05aa7b161b4d5e42070332c0456ea92cc2ed6b79) by Jeff Schnitter).

### Fixed

- fix(integrations prometheus): add sub-command needs to include tenant and password parameters ([6ea99a4](https://github.com/cortexapps/cli/commit/6ea99a426abb8a746cd8316c75a7eaa01c911c1c) by Jeff Schnitter).

## [1.0.3](https://github.com/cortexapps/cli/releases/tag/1.0.3) - 2025-06-19

<small>[Compare with 1.0.2](https://github.com/cortexapps/cli/compare/1.0.2...1.0.3)</small>

### Fixed

- fix(integrations github): add get-personal sub-command ([e117047](https://github.com/cortexapps/cli/commit/e1170478ddc8185d081a2fb6e1ec186be4ee7747) by Jeff Schnitter).
- fix(integrations github) add get-personal sub-command ([ca30efc](https://github.com/cortexapps/cli/commit/ca30efcacdf1d52cb32d2bb7351e5976b12216c8) by Jeff Schnitter).

## [1.0.2](https://github.com/cortexapps/cli/releases/tag/1.0.2) - 2025-06-16

<small>[Compare with 1.0.1](https://github.com/cortexapps/cli/compare/1.0.1...1.0.2)</small>

### Added

- Add github personal sub-commands ([09fb345](https://github.com/cortexapps/cli/commit/09fb34514e755989f1b90de9de3f04795a82aff1) by Jeff Schnitter).

## [1.0.1](https://github.com/cortexapps/cli/releases/tag/1.0.1) - 2025-06-16

<small>[Compare with 1.0.0](https://github.com/cortexapps/cli/compare/1.0.0...1.0.1)</small>

## [1.0.0](https://github.com/cortexapps/cli/releases/tag/1.0.0) - 2025-06-13

<small>[Compare with 0.27.0](https://github.com/cortexapps/cli/compare/0.27.0...1.0.0)</small>

### Added

- Add workflows ([aa4eec7](https://github.com/cortexapps/cli/commit/aa4eec7a22a03c47d08a107bc2273da7c0fff40c) by Jeff Schnitter).
- Add AWS integration ([5bfd05c](https://github.com/cortexapps/cli/commit/5bfd05c8df39924346349d2519e381cfa27722fc) by Jeff Schnitter).
- Add partial SCIM commands ([4ce1f2a](https://github.com/cortexapps/cli/commit/4ce1f2a3552d9831479f18a2255cc84a44f2bf5d) by Jeff Schnitter).
- Add queries ([47a6405](https://github.com/cortexapps/cli/commit/47a6405c67589eef6803bdb5a022d1f3327666c1) by Jeff Schnitter).
- Add plugins ([1bcb3e7](https://github.com/cortexapps/cli/commit/1bcb3e73f52d83ad3079d86c852a74778e7f550b) by Jeff Schnitter).
- Add packages ([512ab55](https://github.com/cortexapps/cli/commit/512ab55523869b1aa16941ccd93ba59583bcdb84) by Jeff Schnitter).
- Add oncall.  No tests for now because we cannot ensure test environment has on-call configured ([b718bef](https://github.com/cortexapps/cli/commit/b718befd67d295e5131d05f35ea29b50c9716cc3) by Jeff Schnitter).
- Add IP allowlist ([9a30031](https://github.com/cortexapps/cli/commit/9a30031ea43b09259264dea81ac7686721f40c5c) by Jeff Schnitter).
- Add groups ([32607f3](https://github.com/cortexapps/cli/commit/32607f3deb80a167a6e776960b58452136147500) by Jeff Schnitter).
- Add GitOps Logs.  Could use some additional test coverage. ([6e762f6](https://github.com/cortexapps/cli/commit/6e762f6b9b75dc91d55db59fb73bac9bb56c475b) by Jeff Schnitter).
- add table sorting, default to show usage when no command given ([fd991aa](https://github.com/cortexapps/cli/commit/fd991aadb9f031340a9ce2a31d41f35c644d17a7) by Martin Stone).
- Add docs API commands ([685991d](https://github.com/cortexapps/cli/commit/685991d58c54bfbddd0032de32f5966d89a3ac0d) by Jeff Schnitter).
- Add discovery audit ([acec276](https://github.com/cortexapps/cli/commit/acec2763443822b06af1696b58409b4f47bf5497) by Jeff Schnitter).
- Add test utils; clean up tests ([6223ad4](https://github.com/cortexapps/cli/commit/6223ad401b9a11f06c32a5930457f3b7fa690826) by Jeff Schnitter).
- Add tests ([d165686](https://github.com/cortexapps/cli/commit/d16568645377422d4a7eded1b71fbfbb13b00bb8) by Jeff Schnitter).
- Add deploys command ([ca41f9c](https://github.com/cortexapps/cli/commit/ca41f9cabb66ad8ab5c31aac0b7f535ecbaf3565) by Jeff Schnitter).
- Add custom-metrics ([2d2886d](https://github.com/cortexapps/cli/commit/2d2886d3b4474e1b2b6e3a4adda7e196e2834567) by Jeff Schnitter).
- Add dependencies commands ([7e474ea](https://github.com/cortexapps/cli/commit/7e474ea4a2e2a5d1fcfb68405bca66530b4d9b67) by Jeff Schnitter).
- add a blank line to raw post/put when reading from interactive terminal stdin ([4a4c9da](https://github.com/cortexapps/cli/commit/4a4c9da0bca375c2c11a5c673ab36ae75cad7146) by Martin Stone).
- add raw request commands ([703110c](https://github.com/cortexapps/cli/commit/703110c388d96e6989ee159772c75628a127530c) by Martin Stone).
- Add custom-events; minor clean up ([7bc72b1](https://github.com/cortexapps/cli/commit/7bc72b15a6582c16f19b4ef7e82f58c6150d2119) by Jeff Schnitter).
- Add simple descriptions for each command. ([765a2fd](https://github.com/cortexapps/cli/commit/765a2fd4f5f6667159dfc271ef8b7c42677a1339) by Jeff Schnitter).
- Add custom-data commands ([915c9ab](https://github.com/cortexapps/cli/commit/915c9ab699afdc82f80563c3390fe3bd2cdc3b39) by Jeff Schnitter).
- add paginated fetch to client, start on catalog commands ([2624db2](https://github.com/cortexapps/cli/commit/2624db29d32b6009a08a215144bca72eca02f609) by Martin Stone).

### Fixed

- Fix paths ([871ce6a](https://github.com/cortexapps/cli/commit/871ce6a602422941fb4dcdcfcbbc67afa515e6f2) by Jeff Schnitter).
- Fix catalog patch test ([3fbbc05](https://github.com/cortexapps/cli/commit/3fbbc05dee137e41dca01c1f6f7be8254fff3d45) by Jeff Schnitter).
- Fix vuln in requests library ([cdac2d7](https://github.com/cortexapps/cli/commit/cdac2d7ce7fbcb8bd3abb0ff3b28baa1951d7187) by Jeff Schnitter).
- Fix syntax error ([c9d1b39](https://github.com/cortexapps/cli/commit/c9d1b39e063b3a72fc4006a414d37ac5ddb37846) by Jeff Schnitter).
- Fix merge conflicts ([04adc78](https://github.com/cortexapps/cli/commit/04adc78753917c3ef53dd05a537671f0f48f801a) by Jeff Schnitter).

### Removed

- Remove need to load data before tests. ([082b059](https://github.com/cortexapps/cli/commit/082b0591f123c235ce6c20e4e1d1b3057fd818fa) by Jeff Schnitter).
- remove validate-pr.yml action ([edeeaf4](https://github.com/cortexapps/cli/commit/edeeaf46e00dd180a952fd8dff7b5ef8ff20b807) by Mike Mellenthin).

## [0.27.0](https://github.com/cortexapps/cli/releases/tag/0.27.0) - 2025-01-05

<small>[Compare with 0.26.7](https://github.com/cortexapps/cli/compare/0.26.7...0.27.0)</small>

### Added

- Add empty __init__.py ([8a56a10](https://github.com/cortexapps/cli/commit/8a56a10e54d1c0a78d10c94c3e487b5e298c848b) by Jeff Schnitter).
- Add History update ([d71c7e5](https://github.com/cortexapps/cli/commit/d71c7e59bd45ad7ce6d07e015d68739266c3babd) by Jeff Schnitter).
- Add catalog patch ([aeff656](https://github.com/cortexapps/cli/commit/aeff656196212399fd5e6d98d29bb87abafca4e2) by Jeff Schnitter).

## [0.26.7](https://github.com/cortexapps/cli/releases/tag/0.26.7) - 2024-11-18

<small>[Compare with 0.26.6](https://github.com/cortexapps/cli/compare/0.26.6...0.26.7)</small>

### Added

- Add history update ([83f87a0](https://github.com/cortexapps/cli/commit/83f87a0e5bac30b47543e5d539d39177bf0ff1e6) by Jeff Schnitter).
- Add slack notification ([ffef9f8](https://github.com/cortexapps/cli/commit/ffef9f8e05808ed47c7abb7babb044f032913ba0) by Jeff Schnitter).
- Add slack notifications ([7e12934](https://github.com/cortexapps/cli/commit/7e12934f75995a069ec729266d6e84ea69b33f0f) by Jeff Schnitter).

### Fixed

- Fix flag for catalog dryRun ([d596e7c](https://github.com/cortexapps/cli/commit/d596e7c93a0624dfc958376286ec18405b9d4c98) by Jeff Schnitter).
- fix: docker/Dockerfile to reduce vulnerabilities ([4c0ab3e](https://github.com/cortexapps/cli/commit/4c0ab3ea208ad4d07d87bc45c12bb08dab6cf3a3) by snyk-bot).

### Removed

- Remove schedule now that test is triggered on each push to staging ([a33b60d](https://github.com/cortexapps/cli/commit/a33b60d944ce4b5cc247645148c4f7f1e1169aa6) by Jeff Schnitter).

## [0.26.6](https://github.com/cortexapps/cli/releases/tag/0.26.6) - 2024-07-30

<small>[Compare with 0.26.5](https://github.com/cortexapps/cli/compare/0.26.5...0.26.6)</small>

### Added

- Add test to ensure all deploys aren't deleted by deploys delete-by-uuid ([33966a3](https://github.com/cortexapps/cli/commit/33966a332872108ba944e88638dadd45a367d557) by Jeff Schnitter).
- Add workflow dispatch events ([8000ba0](https://github.com/cortexapps/cli/commit/8000ba01b0df4985b76ce1d3f83cf166b757b1bc) by Jeff Schnitter).

### Fixed

- Fix make target that ensure pre-requisite tools are installed ([bacbe45](https://github.com/cortexapps/cli/commit/bacbe45b20b50bb46ae089ac8a214731f4cdeebb) by Jeff Schnitter).
- fix: docker/Dockerfile to reduce vulnerabilities ([778ec0f](https://github.com/cortexapps/cli/commit/778ec0f25bf19c35cca2d3e811c0fcba63c83685) by snyk-bot).

## [0.26.5](https://github.com/cortexapps/cli/releases/tag/0.26.5) - 2024-06-27

<small>[Compare with 0.26.4](https://github.com/cortexapps/cli/compare/0.26.4...0.26.5)</small>

### Added

- add history update ([3c4cded](https://github.com/cortexapps/cli/commit/3c4cded1a2b5f7437b9785aaf9a1eded24bfa1f6) by Jeff Schnitter).

## [0.26.4](https://github.com/cortexapps/cli/releases/tag/0.26.4) - 2024-06-27

<small>[Compare with 0.26.3](https://github.com/cortexapps/cli/compare/0.26.3...0.26.4)</small>

### Added

- Add history file ([3587614](https://github.com/cortexapps/cli/commit/3587614eb5b3e934a50dc352262e9d77fe200ac7) by Jeff Schnitter).
- Add obfuscation script ([ac595ca](https://github.com/cortexapps/cli/commit/ac595caa32dfd6ea5863183918cbcbedabadab22) by Jeff Schnitter).
- Add provider for all group type owners where provider is not listed ([d8319b0](https://github.com/cortexapps/cli/commit/d8319b0369d084ff00f35ad49b812690c7d2afb8) by Jeff Schnitter).

### Fixed

- Fix var definition ([7632aca](https://github.com/cortexapps/cli/commit/7632aca1fa5459e0b729178e371005d657e7effd) by Jeff Schnitter).
- Fix PYTHONPATH for setting up github ([b4715f6](https://github.com/cortexapps/cli/commit/b4715f636f34c74683de64f0e89dc300757644cc) by Jeff Schnitter).
- Fix python path; upgrade dependent versions ([0f2e44d](https://github.com/cortexapps/cli/commit/0f2e44dd597d0d04d9f775dcfc3b58a3e69c3390) by Jeff Schnitter).

### Removed

- Remove debugging; solved - bad CORTEX_API_KEY but no exception was thrown ([3331d0a](https://github.com/cortexapps/cli/commit/3331d0adcdc76e1d38aa2a25456725c395af90cc) by Jeff Schnitter).

## [0.26.3](https://github.com/cortexapps/cli/releases/tag/0.26.3) - 2024-05-20

<small>[Compare with 0.26.2](https://github.com/cortexapps/cli/compare/0.26.2...0.26.3)</small>

### Fixed

- Fix JSON payload formatting for docs update ([f1f4f27](https://github.com/cortexapps/cli/commit/f1f4f272fcede8894b486458ff9716e04a62c619) by Jeff Schnitter).

## [0.26.2](https://github.com/cortexapps/cli/releases/tag/0.26.2) - 2024-05-08

<small>[Compare with 0.26.1](https://github.com/cortexapps/cli/compare/0.26.1...0.26.2)</small>

## [0.26.1](https://github.com/cortexapps/cli/releases/tag/0.26.1) - 2024-05-06

<small>[Compare with 0.26.0](https://github.com/cortexapps/cli/compare/0.26.0...0.26.1)</small>

## [0.26.0](https://github.com/cortexapps/cli/releases/tag/0.26.0) - 2024-05-06

<small>[Compare with 0.25.0](https://github.com/cortexapps/cli/compare/0.25.0...0.26.0)</small>

## [0.25.0](https://github.com/cortexapps/cli/releases/tag/0.25.0) - 2024-05-05

<small>[Compare with 0.24.3](https://github.com/cortexapps/cli/compare/0.24.3...0.25.0)</small>

### Added

- Add pagination parmeters ([3bf5534](https://github.com/cortexapps/cli/commit/3bf5534fa9a25ea6a5189d69dc3dfc99116a1dad) by Jeff Schnitter).

## [0.24.3](https://github.com/cortexapps/cli/releases/tag/0.24.3) - 2024-04-27

<small>[Compare with 0.24.2](https://github.com/cortexapps/cli/compare/0.24.2...0.24.3)</small>

### Added

- Add backup of Workday teams. ([a258eab](https://github.com/cortexapps/cli/commit/a258eab35104c2f2c80b134b6595186365f46935) by Jeff Schnitter).

### Fixed

- Fix IP allowlist validate; add -q option ([e31e16b](https://github.com/cortexapps/cli/commit/e31e16bc85fe0d3305f27dff4685adbf356b3e0f) by Jeff Schnitter).

## [0.24.2](https://github.com/cortexapps/cli/releases/tag/0.24.2) - 2024-02-28

<small>[Compare with 0.24.1](https://github.com/cortexapps/cli/compare/0.24.1...0.24.2)</small>

### Added

- Add recipe for deleting all Workday teams ([b5cd084](https://github.com/cortexapps/cli/commit/b5cd0841b6fea4bad7f30c12bdfaadcab8d96046) by Jeff Schnitter).

## [0.24.1](https://github.com/cortexapps/cli/releases/tag/0.24.1) - 2024-02-15

<small>[Compare with 0.24.0](https://github.com/cortexapps/cli/compare/0.24.0...0.24.1)</small>

## [0.24.0](https://github.com/cortexapps/cli/releases/tag/0.24.0) - 2024-02-14

<small>[Compare with 0.23.0](https://github.com/cortexapps/cli/compare/0.23.0...0.24.0)</small>

### Removed

- Remove extra workflow ([34d3ca1](https://github.com/cortexapps/cli/commit/34d3ca1731b79da4e1e07459e02c077aaf71f16a) by Jeff Schnitter).
- Remove aliases from default cortex config file ([8926291](https://github.com/cortexapps/cli/commit/892629163eb232c017c2de140f21a38c1a821955) by Jeff Schnitter).

## [0.23.0](https://github.com/cortexapps/cli/releases/tag/0.23.0) - 2024-02-06

<small>[Compare with 0.22.0](https://github.com/cortexapps/cli/compare/0.22.0...0.23.0)</small>

### Added

- Add dependency on pypi ([10f9f27](https://github.com/cortexapps/cli/commit/10f9f27bb902e309374fc73192f80a03c9ebaddc) by Jeff Schnitter).

### Fixed

- Fix homebrew publishing ([fefe24b](https://github.com/cortexapps/cli/commit/fefe24bfc17ab82d1fee4203e170bd3b9b3a1da7) by Jeff Schnitter).

## [0.22.0](https://github.com/cortexapps/cli/releases/tag/0.22.0) - 2024-02-06

<small>[Compare with 0.21.0](https://github.com/cortexapps/cli/compare/0.21.0...0.22.0)</small>

## [0.21.0](https://github.com/cortexapps/cli/releases/tag/0.21.0) - 2024-01-26

<small>[Compare with 0.20.0](https://github.com/cortexapps/cli/compare/0.20.0...0.21.0)</small>

### Added

- Add showDrafts query parameter for scorecards list ([bcc5c79](https://github.com/cortexapps/cli/commit/bcc5c791626d135a5bef350682197c81449a2e03) by Jeff Schnitter).

## [0.20.0](https://github.com/cortexapps/cli/releases/tag/0.20.0) - 2024-01-23

<small>[Compare with 0.19.0](https://github.com/cortexapps/cli/compare/0.19.0...0.20.0)</small>

### Fixed

- Fix vulnerabilities found by dependabot ([d339b79](https://github.com/cortexapps/cli/commit/d339b7947ef392069a9064f8531d2f3ebb86037d) by Jeff Schnitter).
- Fix scorecards scores, entity tag is an optional parameter ([4b1a81f](https://github.com/cortexapps/cli/commit/4b1a81f5f450be2a2c019b1e06837070bda5d0e7) by Jeff Schnitter).

## [0.19.0](https://github.com/cortexapps/cli/releases/tag/0.19.0) - 2023-12-22

<small>[Compare with 0.18.0](https://github.com/cortexapps/cli/compare/0.18.0...0.19.0)</small>

## [0.18.0](https://github.com/cortexapps/cli/releases/tag/0.18.0) - 2023-12-19

<small>[Compare with 0.17.0](https://github.com/cortexapps/cli/compare/0.17.0...0.18.0)</small>

### Added

- Add improvement for version 0.18.0 ([76069ac](https://github.com/cortexapps/cli/commit/76069ac7e0b2f88791f31a187946196a793cc2af) by Jeff Schnitter).
- Add gitops-logs command ([f03f7d5](https://github.com/cortexapps/cli/commit/f03f7d5c872f18e3cfd554e9a25188b0a43692e5) by Jeff Schnitter).
- Add example for updating deploys ([148b973](https://github.com/cortexapps/cli/commit/148b97368d23998622632b7f0dc8a876f59b7df2) by Jeff Schnitter).

### Fixed

- Fix typos ([891b231](https://github.com/cortexapps/cli/commit/891b231f3640cb3fbdb479ae7796ee1dfbb9f047) by Jeff Schnitter).
- Fix doc for backup to include tenant flag. ([549a53c](https://github.com/cortexapps/cli/commit/549a53c03bc7dbb1cf28d6ee74207d97b71501d2) by Jeff Schnitter).

## [0.17.0](https://github.com/cortexapps/cli/releases/tag/0.17.0) - 2023-12-06

<small>[Compare with 0.16.0](https://github.com/cortexapps/cli/compare/0.16.0...0.17.0)</small>

## [0.16.0](https://github.com/cortexapps/cli/releases/tag/0.16.0) - 2023-12-06

<small>[Compare with 0.15.0](https://github.com/cortexapps/cli/compare/0.15.0...0.16.0)</small>

### Added

- Add history update ([d589dcf](https://github.com/cortexapps/cli/commit/d589dcf381ff826606b3016477940125963d86fb) by Jeff Schnitter).
- Add azure-resources integration ([8b07757](https://github.com/cortexapps/cli/commit/8b077576b0d3f146faec2d3d8df46f737cdc4e16) by Jeff Schnitter).

### Fixed

- Fix bug in export; re-order tests ([886f92f](https://github.com/cortexapps/cli/commit/886f92fc1b4007e414587154f757261d5a1d0feb) by Jeff Schnitter).
- Fix outputs in workflow ([fdf28a9](https://github.com/cortexapps/cli/commit/fdf28a9ad1ba525e4899f86b2145888cad2f3fb8) by Jeff Schnitter).

## [0.15.0](https://github.com/cortexapps/cli/releases/tag/0.15.0) - 2023-12-05

<small>[Compare with 0.14.0](https://github.com/cortexapps/cli/compare/0.14.0...0.15.0)</small>

### Added

- add example for changing git basepath ([f415036](https://github.com/cortexapps/cli/commit/f41503617b0825e19f2d6a4c3807fef6783dc53b) by Jeff Schnitter).

## [0.14.0](https://github.com/cortexapps/cli/releases/tag/0.14.0) - 2023-12-04

<small>[Compare with 0.13.0](https://github.com/cortexapps/cli/compare/0.13.0...0.14.0)</small>

### Added

- Add support for CORTEX environment variables; remove alias support ([2a331a1](https://github.com/cortexapps/cli/commit/2a331a137b1da8f079710c4bd85a4f7a6c9fbb70) by Jeff Schnitter).

## [0.13.0](https://github.com/cortexapps/cli/releases/tag/0.13.0) - 2023-12-01

<small>[Compare with 0.12.0](https://github.com/cortexapps/cli/compare/0.12.0...0.13.0)</small>

### Added

- Add incident.io integration; fix GH workflows ([00b7f60](https://github.com/cortexapps/cli/commit/00b7f60a0fcfc716d207a6862420636045399ed4) by Jeff Schnitter).

## [0.12.0](https://github.com/cortexapps/cli/releases/tag/0.12.0) - 2023-11-30

<small>[Compare with 0.11.0](https://github.com/cortexapps/cli/compare/0.11.0...0.12.0)</small>

### Added

- Add support for updating deploys by uuid; change newrelic tests to use mocks ([29e5400](https://github.com/cortexapps/cli/commit/29e54002b0c27936dc49a8501c4328743368ff53) by Jeff Schnitter).
- Add badges ([4073cae](https://github.com/cortexapps/cli/commit/4073cae15547ecc13736af9917ddf3eba0d5c51d) by jeff-schnitter).

### Fixed

- Fix test data ([0ac90a0](https://github.com/cortexapps/cli/commit/0ac90a09af96fd478d96f7c33a2ddd4fdb9563ed) by Jeff Schnitter).

## [0.11.0](https://github.com/cortexapps/cli/releases/tag/0.11.0) - 2023-11-27

<small>[Compare with 0.10.0](https://github.com/cortexapps/cli/compare/0.10.0...0.11.0)</small>

### Added

- Add README back to fix merge conflict ([f359c15](https://github.com/cortexapps/cli/commit/f359c15eda28056735109ebdcf072adeebcaa6d1) by Jeff Schnitter).
- Add support for docker builds ([aace4cb](https://github.com/cortexapps/cli/commit/aace4cbca8d14cb6d07da7734f26fb45b0f6dce6) by Jeff Schnitter).
- Add examples ([efe75c6](https://github.com/cortexapps/cli/commit/efe75c68a892dfbe8a764c2897c9706bdbf4365b) by jeff-schnitter).
- Add GH Actions badge. ([84a6fa6](https://github.com/cortexapps/cli/commit/84a6fa649b95a0785837ef02ab49f21a28be4e5b) by jeff-schnitter).

### Fixed

- Fix build errors ([38f3987](https://github.com/cortexapps/cli/commit/38f398746dee8c033e1a3622d7bc79d1321bee3d) by Jeff Schnitter).

## [0.10.0](https://github.com/cortexapps/cli/releases/tag/0.10.0) - 2023-11-22

<small>[Compare with 0.9.0](https://github.com/cortexapps/cli/compare/0.9.0...0.10.0)</small>

### Added

- Add suffix for export directory ([57bb9b3](https://github.com/cortexapps/cli/commit/57bb9b316db06bfc8fe6e914e74ff62bd5a71e52) by Jeff Schnitter).

## [0.9.0](https://github.com/cortexapps/cli/releases/tag/0.9.0) - 2023-11-21

<small>[Compare with 0.8.0](https://github.com/cortexapps/cli/compare/0.8.0...0.9.0)</small>

### Added

- Add error handling for bad API keys ([b894ca2](https://github.com/cortexapps/cli/commit/b894ca2c5df53befa8d45ca6eb3f6ae98fca9826) by Jeff Schnitter).

## [0.8.0](https://github.com/cortexapps/cli/releases/tag/0.8.0) - 2023-11-19

<small>[Compare with 0.7.0](https://github.com/cortexapps/cli/compare/0.7.0...0.8.0)</small>

### Added

- Add coralogix, launchdarkly integrations ([80cc095](https://github.com/cortexapps/cli/commit/80cc09536127d684a1d9d1f1f614aa5714a7e8c3) by Jeff Schnitter).

## [0.7.0](https://github.com/cortexapps/cli/releases/tag/0.7.0) - 2023-11-18

<small>[Compare with 0.6.0](https://github.com/cortexapps/cli/compare/0.6.0...0.7.0)</small>

### Added

- Add pagerduty integration ([63c8eba](https://github.com/cortexapps/cli/commit/63c8eba7aab2ce9a0465b849bc48f83d43bfde42) by Jeff Schnitter).

## [0.6.0](https://github.com/cortexapps/cli/releases/tag/0.6.0) - 2023-11-16

<small>[Compare with 0.5.0](https://github.com/cortexapps/cli/compare/0.5.0...0.6.0)</small>

### Added

- Add dependencies; increase timeout for query tests ([88cfdb2](https://github.com/cortexapps/cli/commit/88cfdb24b00a3bfcee467c90cf610fd3d3aa40e9) by Jeff Schnitter).

### Fixed

- Fix test names to reflect consolidated tests ([c9d948f](https://github.com/cortexapps/cli/commit/c9d948f781f9813bdcd7fabb6bd8124627693ab8) by Jeff Schnitter).
- Fix timeout flag for queries ([220d4cc](https://github.com/cortexapps/cli/commit/220d4ccea7ad2aab81a5828e1062614b70ec9e5f) by Jeff Schnitter).
- Fix github action, the branch is the target branch, not the source branch ([024b894](https://github.com/cortexapps/cli/commit/024b8945fd7cbe176c8bf2d1feacb7700f02d7c6) by Jeff Schnitter).

## [0.5.0](https://github.com/cortexapps/cli/releases/tag/0.5.0) - 2023-11-14

<small>[Compare with 0.4.0](https://github.com/cortexapps/cli/compare/0.4.0...0.5.0)</small>

### Fixed

- Fix syntax error in cortex deploy API call for prod publish ([8334b25](https://github.com/cortexapps/cli/commit/8334b25aa235039664ac97bb6c0f9503da2e5f67) by Jeff Schnitter).

## [0.4.0](https://github.com/cortexapps/cli/releases/tag/0.4.0) - 2023-11-14

<small>[Compare with 0.3.0](https://github.com/cortexapps/cli/compare/0.3.0...0.4.0)</small>

### Added

- Add fix for backups to export catalog entries as YAML ([1a28817](https://github.com/cortexapps/cli/commit/1a2881775815bdc12c54262da7e28b0b91e49941) by Jeff Schnitter).
- Add --wait, --timeout for queries and support for queries as text ([198c8e1](https://github.com/cortexapps/cli/commit/198c8e198504c8044493a2186c0c740406d82a25) by Jeff Schnitter).
- Add composite action for deploys ([c3b838d](https://github.com/cortexapps/cli/commit/c3b838de70b98b29b765895eb51a1ee273924028) by Jeff Schnitter).

## [0.3.0](https://github.com/cortexapps/cli/releases/tag/0.3.0) - 2023-11-07

<small>[Compare with 0.2.0](https://github.com/cortexapps/cli/compare/0.2.0...0.3.0)</small>

### Fixed

- Fix backup ([10220e0](https://github.com/cortexapps/cli/commit/10220e06ab69e5736f6f98b2202ee0808315bfa9) by Jeff Schnitter).

## [0.2.0](https://github.com/cortexapps/cli/releases/tag/0.2.0) - 2023-11-07

<small>[Compare with 0.1.0](https://github.com/cortexapps/cli/compare/0.1.0...0.2.0)</small>

### Added

- Add documentation for local homebrew install ([337525f](https://github.com/cortexapps/cli/commit/337525f2670057cf81d87c3d7313500ff27531b9) by Jeff Schnitter).

### Fixed

- Fix configuration of cortex config file ([44119a5](https://github.com/cortexapps/cli/commit/44119a5b81d471bc949122d2650ce68c8faa6a85) by Jeff Schnitter).
- Fix path to homebrew formula ([adf83f8](https://github.com/cortexapps/cli/commit/adf83f89a40c7d751356d8173a5cb7ebd9aae588) by Jeff Schnitter).

## [0.1.0](https://github.com/cortexapps/cli/releases/tag/0.1.0) - 2023-11-05

<small>[Compare with 0.0.5](https://github.com/cortexapps/cli/compare/0.0.5...0.1.0)</small>

### Added

- add debugging ([2549b23](https://github.com/cortexapps/cli/commit/2549b237b636bb28de7925728300870d61b50899) by Jeff Schnitter).
- add pytest-cov ([e0ba740](https://github.com/cortexapps/cli/commit/e0ba740176c5dd71014ca87308491d07b1af20d7) by Jeff Schnitter).

### Removed

- remove poetry self add pytest-cov ([7a661f1](https://github.com/cortexapps/cli/commit/7a661f1692e952c4893e8d67802674f856b15dd4) by Jeff Schnitter).

## [0.0.5](https://github.com/cortexapps/cli/releases/tag/0.0.5) - 2023-11-04

<small>[Compare with first commit](https://github.com/cortexapps/cli/compare/c1de1ad2bf64e156246c6806e2d57ee3b03b3d1b...0.0.5)</small>

### Added

- add build in the right spot ([7b9d266](https://github.com/cortexapps/cli/commit/7b9d266273beec6670e64bb562a4acaddb0e03d5) by Jeff Schnitter).
- add needs ([9946e60](https://github.com/cortexapps/cli/commit/9946e60259688fec231c6b37af1270da1b02e379) by Jeff Schnitter).
- Add a pr workflow ([9a0989d](https://github.com/cortexapps/cli/commit/9a0989d3cc33d9b92be8053a28e46925e867f2cc) by Jeff Schnitter).
- Add voln scan, artifact upload ([1728617](https://github.com/cortexapps/cli/commit/1728617a12f6b4bb967f3ee765e980e485169ab7) by Jeff Schnitter).
- add pip-audit ([5854f9b](https://github.com/cortexapps/cli/commit/5854f9b47e2ef6edcf0d0c9dcc92d88ac0ab8425) by Jeff Schnitter).
- Add debugging ([072de28](https://github.com/cortexapps/cli/commit/072de28b31026dcbe1b2b3f097aa72ff141a2f8c) by jeff-schnitter).
- Add requests and pyyaml dependencies ([c1de1ad](https://github.com/cortexapps/cli/commit/c1de1ad2bf64e156246c6806e2d57ee3b03b3d1b) by Jeff Schnitter).

### Fixed

- fix syntax ([70bd98f](https://github.com/cortexapps/cli/commit/70bd98f52565bc5542631ed04709e8f536c914fb) by Jeff Schnitter).
- Fix syntax errors ([f1a96ed](https://github.com/cortexapps/cli/commit/f1a96ed068d3ffdafdff325bb19487f5b616781b) by Jeff Schnitter).
- fix branch rules ([5637b9e](https://github.com/cortexapps/cli/commit/5637b9e362915724f50f09c14b3350b0dc052af8) by Jeff Schnitter).
- Fix title of step ([b3f2fee](https://github.com/cortexapps/cli/commit/b3f2feec85e8a9c0abd9a60b30f7224ef4895f8d) by Jeff Schnitter).
- Fix creation of cortex config file ([7d97964](https://github.com/cortexapps/cli/commit/7d979642b3dc02b30bff1bdd8d3dc46fb186fc9b) by Jeff Schnitter).
- fix yaml error ([e9e82b2](https://github.com/cortexapps/cli/commit/e9e82b2d1755de31de8f83a46d912097f98f526d) by Jeff Schnitter).

### Changed

- Change version logic ([fc0ac06](https://github.com/cortexapps/cli/commit/fc0ac06d04b3bcf6ea875b84924324bb789ef921) by Jeff Schnitter).

### Removed

- remove pycache ([84f8dde](https://github.com/cortexapps/cli/commit/84f8dde2438dca0d72dc81fb9fc49fe919594110) by Jeff Schnitter).

