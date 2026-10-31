# Changelog

## [3.1.4](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v3.1.3...v3.1.4) (2026-10-31)


### Bug Fixes

* **core:** time-limit opening the SSH shell ([16332a6](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/16332a6781843912d207ecf60e5b3e6babe5b78d))
* **core:** time-limit opening the SSH shell ([4b33987](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/4b339879c73843404b48df484d0c1cdb21aab3bf))

## [3.1.3](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v3.1.2...v3.1.3) (2026-10-31)


### Bug Fixes

* validate command inputs and harden reply parsing ([01da1ac](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/01da1ac85cf4642eb9881ab8fa8069730262f297))
* validate command inputs and harden reply parsing ([4e96b7d](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/4e96b7dd0dfa408806b5ae421285a475aaca7d97))

## [3.1.2](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v3.1.1...v3.1.2) (2026-10-30)


### Bug Fixes

* **core:** drop other API sessions' echoed commands and replies from responses ([aa6f559](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/aa6f559841d7c49483bba96f73aaa49805341b28))
* **core:** keep possessive scene replies and drop repeats of our own command ([27b2aaf](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/27b2aafa9be8560cb3936b4c6a9557d236e98270))
* ignore other API sessions' traffic in command responses ([8880bbf](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/8880bbf59ccb938dbdf23409818d468eebc4e182))


### Documentation

* note that the controller echoes other sessions' traffic ([61a86d0](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/61a86d01ff50e9bff5e6dd41615234e12484eb94))

## [3.1.1](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v3.1.0...v3.1.1) (2026-10-30)


### Bug Fixes

* 3.1.1 — final audit fixes ([84da79e](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/84da79e67dab2ad68c1aed8b527527839b94c410))
* **core:** check the link under the command lock and sanity-check hex serialinfo ([ac4c6db](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/ac4c6db34a02e25ef21830d35a7313afbf4d1c30))
* declare the MIT license and Typing :: Typed in package metadata ([42ed4f1](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/42ed4f18ad085d1b40772e0036da5faf2fd639ce))
* keep the vendor PDF and repo tooling out of the sdist; empty device name means all devices ([2066fe9](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/2066fe919e620483fe8927684985aee98e7dc5ed))
* **models:** decide single-device queries by the request, not the entry count ([2bd7ef5](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/2bd7ef5e33c8ab711a30b0c845f9bd5284178df6))
* **models:** parse matrix audio3 pairs on one line and accept an empty scene list ([e402d84](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/e402d8479a8e9798bf23c253a7933e807c70d39e))
* stop make clean deleting the tracked .claude directory ([1219db7](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/1219db770fea6dc97a4889f2201516cb2c3fa9fb))


### Documentation

* fix drift in docstrings, contributor docs and agent skills ([f99d8dc](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/f99d8dce48fa6cb72a940e70c84fd400386cf07e))
* link the security policy by URL so the strict docs build passes ([963bc75](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/963bc75ff65e6ed4aa85f305eab028668566eb95))
* report vulnerabilities through GitHub private vulnerability reporting ([4072d4c](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/4072d4cdbd25c0e5a0ce6894acb01980fe50547e))

## [3.1.0](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v3.0.1...v3.1.0) (2026-10-30)


### Features

* **core:** optional SSH host key pinning ([a8aaae6](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/a8aaae62d77d12656fb4d6a094bc5d67753e7e00))
* optional SSH host key pinning; bound serialinfo framing ([e338451](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/e33845140fd793103dd43806e45a5ac943210a48))


### Bug Fixes

* **core:** cap serialinfo length and bound the reader buffer ([dd95508](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/dd95508f14eaaf7990d52a96954a843a34018c11))
* **core:** dispatch serialinfo as soon as its data is in ([c41f5ad](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/c41f5ad450daf446111f762569aaf5cc7176bede))
* **core:** record host key fingerprint only once the shell is open ([9c89533](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/9c8953389eb05f43e88d2c10f7e263cfccfb3556))


### Documentation

* describe pinning an existing SSH client after trust on first use ([536e5d0](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/536e5d049703fd6475ba3d99e87678127af7f635))
* document SSH host key pinning and trust on first use ([1285276](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/12852762e0faaf97d027b019df4e1920ca1af622))

## [3.0.1](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v3.0.0...v3.0.1) (2026-10-30)


### Bug Fixes

* 3.0.1 — echo handling, truncated replies and connection lifecycle ([68d5b21](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/68d5b21d550a04ff59435cd4233bc3496958a767))
* **commands:** drop the command echo before parsing replies ([6b620dc](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/6b620dcd2561c5eaef925a88bfe3a0b77f3e6795))
* **core:** harden the reader, timeouts and connection lifecycle ([576ab4e](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/576ab4e766d19edf1629d7cd2d00c9adcf986cde))
* **models:** skip unparseable devices in multi-device lists ([2ba6b8e](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/2ba6b8edb27bef437132ead75679776f9d464814))


### Documentation

* correct NHDAPI registration and document 3.0.1 behaviour changes ([51f14b3](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/51f14b3fd61ee9881b09bc59d336ac0c77c8b637))

## [3.0.0](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/compare/v2.2.1...v3.0.0) (2026-10-30)


### ⚠ BREAKING CHANGES

* **core:** send_command raises TimeoutError instead of returning "" and UnknownCommandError for "unknown command"; responses start at the command echo; response_line_timeout defaults to 0.3 s instead of 1 s; reconnect() raises ReconnectionError and no longer returns silently while connecting; heartbeat_interval and circuit_breaker_timeout are ignored with a DeprecationWarning (removed in 4.0); notification_handler.handle_notification is now synchronous.
* **core:** ConnectionLostError/ReconnectionError/UnknownCommandError have new base classes, and parse_json_response raises ResponseError (a ValueError subclass once ResponseError gains that base).
* **models:** DeviceInfo.parse and DeviceStatus.parse no longer raise DeviceQueryError when one of several devices is an error entry; that device is left out of the returned list. Unknown JSON keys are ignored instead of raising TypeError, invalid values raise ResponseError, and a required DeviceInfo "aliasname" of "null" stays the string "null".

### Features

* **core:** make library exceptions subclass the matching builtins ([0887aaa](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/0887aaa76001733120dfb3740e86e24ea34bff91))
* **core:** rework transport, framing and reconnect ([2e8b8ba](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/2e8b8ba41ad9f1dc188ffec1f69d6439e23a1559))


### Bug Fixes

* **core:** annotate RS232 serial_kwargs so the docs build passes --strict ([0976d82](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/0976d821d31a8109c650137710f21cd0491fc009))
* **core:** stop configuring logging on import ([edb3d3f](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/edb3d3fa0829b54484197042354fc67aa9e5bf92))
* **models:** handle short video and multi-line serial/IR notifications ([edd87fb](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/edd87fb8c6d536589f60bd6dd4aceae984116e26))
* **models:** parse device JSON robustly and raise ResponseError from parsers ([c73167f](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/c73167ff3bd75b00da8220d52803658b4fb3a8ce))


### Documentation

* correct CONTRIBUTING for 3.0 ([86a629b](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/86a629bd656d29991e5771320d8361c9193586f9))
* update README and docs for 3.0 and add a migration guide ([97969e7](https://github.com/Matt-Hadley/wyrestorm-networkhd-py/commit/97969e7c6c2bad185093ae9dc4a7fbb8edc5ba7d))

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
