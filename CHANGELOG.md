# Changelog

## [2.2.1](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v2.2.0...v2.2.1) (2025-09-01)


### Bug Fixes

* include Python version in PR artifact name ([aa7e599](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/aa7e599aefb6f5d4889f7c07fd0b125913a13c8e))

## [2.2.0](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v2.1.0...v2.2.0) (2025-08-31)


### Features

* add Python 3.11 support and update to production status ([82abb77](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/82abb775e721d31a44512d6ed24896c863b6b613))

## [2.1.0](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v2.0.1...v2.1.0) (2025-08-29)


### Features

* add configurable response_line_timeout parameter ([e654961](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/e65496150aca26472d82ecb8a55b06f8b412ed0e))

## [2.0.1](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v2.0.0...v2.0.1) (2025-08-29)


### Bug Fixes

* apply response parsing to strip welcome banner consistently ([6e39896](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/6e39896827eb87083e0c58116c434ab31293bfcc))

## [2.0.0](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v1.1.1...v2.0.0) (2025-08-28)


### ⚠ BREAKING CHANGES

* Device query methods now return typed dataclass objects instead of raw dictionaries

### Features

* replace device query dict returns with typed dataclasses ([3db36e9](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/3db36e986434304d2931a619bd5912a8d5a81ecd))


### Documentation

* add comprehensive troubleshooting documentation ([a3785b3](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/a3785b397e0e53ed4224a7e00bf581484e16a488))
* update examples for typed device query methods ([bf02bdb](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/bf02bdbca0c07a0dc5c6ded8fcc203c2934e482c))

## [1.1.1](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v1.1.0...v1.1.1) (2025-08-24)


### Bug Fixes

* correct coverage badge output parsing in release workflow ([ec174af](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/ec174af075b86eebf307cb7d9601f5d7fe6175d2))
* restore release.yml name for PyPI trusted publisher compatibility ([d3acb76](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/d3acb76dbc805c3328aee696f31a18c1e50a33cc))
* update project structure validation for temporary workflow ([ecd6f0a](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/ecd6f0a6db85e25b72e82b8aa95f22b27ee0a696))
* use virtual environment mkdocs path for reliable documentation building ([c801cc6](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/c801cc6c27abb5c30525451cb76cbe4bcc9cd8fe))

## [1.1.0](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v1.0.0...v1.1.0) (2025-08-24)


### Features

* optimize release workflow to avoid duplicate health-checks ([3897014](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/3897014843d28db16a56bf6fae40b38305746c0d))


### Bug Fixes

* use runtime mkdocs resolution instead of parse-time variable ([bea3cc2](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/bea3cc2f732f309c8d69cfc3dda7a70e9702bed3))

## [1.0.0](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v0.1.3...v1.0.0) (2025-08-24)


### ⚠ BREAKING CHANGES

* Test file organization restructured with new naming conventions
* Notification class names have been updated to align with the actual API reference command names:
* NetworkHDClientSSH constructor now requires explicit port, username, password, and ssh_host_key_policy parameters with no defaults except timeout (10s). Users must now provide all connection parameters explicitly for better security. The NotificationObject type alias is now dynamically generated from notification parser mappings.
* NetworkHDClient replaced with NetworkHDClientSSH, ssh_host_key_policy now required
* add core directory

### Features

* add comprehensive integration and performance test suite ([3a007ce](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/3a007ce402295d6a94adf5c116021bab537b1473))
* add comprehensive sink power notification support ([fcd320f](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/fcd320f525e9476b67c987f3bb3b5f5f46354e07))
* add core directory ([d34f81b](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/d34f81b724970bb52e13af4fffc56b3b3ac18a21))
* add dynamic client support to NHDAPI ([b1e7974](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/b1e797411c36b22832cddfe3674ff85d9925d9a4))
* add dynamic command group discovery to NHDAPI ([e3948e3](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/e3948e3b006824485618465fc629b73dd3491242))
* add RS232 client as optional extension ([d20e990](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/d20e99080b032afa82d2c25fda4ecd409fd51170))
* Comprehensive test suite reorganization and improvementsFix/unit test core ([7e0f188](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/7e0f18887b232393441ff10c66bc3c1ab695f9e4))
* enhance core module with robust connection management and improve code organization ([f39abba](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/f39abbadfb7fbfb62be569d2359a8ce6a3b25f44))
* fix rs232 client ([62f3178](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/62f3178ccdd7a00f019939824386cf556d883684))
* improve type safety in core module with dynamic notification types ([73b7c21](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/73b7c21420f91cee1fb15e0c31fd36c4f74cab12))
* include documentation building in health-check target ([d6ad051](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/d6ad051c614e7cf70a902339b3ae7913e3a91811))
* restructure client architecture and add real-time notifications ([055f4e6](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/055f4e63246227d3d0bb238d11bed66dc9071208))


### Bug Fixes

* Add unit tests for RS232 and SSH clients, including connection, command sending, and message dispatching ([18fc382](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/18fc3823082f63d7f92d6d5f116dfdca0ee96152))
* clarify response_timeout argument description in client classes ([73ee14c](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/73ee14cc642c4818da96fdf6db72caaad3f2db66))
* Correct enum comparison in connection state checks ([927d00f](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/927d00fbe674a4883fc6d84039e154fbeaf7585d))
* Correct import paths for exceptions in test files ([cd7b407](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/cd7b407fea03b7dbf1b41b9e612117ddbfb71f7a))
* improve SSH command response handling and connection state management ([14e4653](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/14e4653b0291509a3de60ab2cb2f147c8f09c02e))
* resolve all linting and test issues ([c66163d](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/c66163d43d158e075cfbe5a082e11a67276d6f7a))
* resolve all mypy type checking errors across core and models ([f8f69a7](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/f8f69a74a23fb6be10586db4d6218ea86611b4a1))
* rs232 client ([5862d1c](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/5862d1c0435c88d9c75ac54d7726eb2cffe9ca13))
* store connection state consistently ([ed85f3b](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/ed85f3bcb22753bd0ac7a7e2fe77c4f2d85495a5))
* update docstring ([8dadc4e](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/8dadc4ead4445200106290aa8b8843055668cab8))


### Documentation

* comprehensive documentation system and GitHub Pages integration ([adb46bf](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/adb46bf774ecb0927ac5d4858d04a4c9d9dc647b))
* update notification type references in examples ([ae59dea](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/ae59dead9ed6f5756c6a4c9264b410525280b632))
* update notification type references in examples ([0ee2612](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/0ee2612bd8c8e610f696083bae73f77e1988d2aa))


### Code Refactoring

* rename notification classes to match API reference names ([fae6a82](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/fae6a829ebac7711301aee84174cd42e255d73e7))

## [0.1.3](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v0.1.2...v0.1.3) (2025-08-22)


### Bug Fixes

* update cobertura-action version to v14 in workflows for improved functionality ([b5218ed](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/b5218ed86cea9bf7c6990fcb9704b61a9f219864))

## [0.1.2](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v0.1.1...v0.1.2) (2025-08-22)


### Bug Fixes

* update permissions in workflow files to include checks for improved CI/CD functionality ([237a9d6](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/237a9d6881c5745bbbe88b9251d6a66b64c3dbdf))

## [0.1.1](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v0.1.0...v0.1.1) (2025-08-22)

### Bug Fixes

- update CI/CD workflows and documentation for improved health checks and coverage reporting
  ([94a9db7](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/94a9db7a442a052687c3c5b6a1bdf9151e0c8663))

## 0.1.0 (2025-08-22)

### Features

- initial release
  ([3e4e4fe](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/3e4e4fee67b32e0c1336924505fe8b5dc5999fce))
