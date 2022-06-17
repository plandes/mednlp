# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).


## [Unreleased]

### Removed
- Support for Python 3.7, 3.8 from dropped support in `zensols.util`.


## [0.0.2] - 2022-05-04
### Added
- A CSV features dump example.

### Changed
- Use token instead of sentence level mapping in cases where MedCAT creates
  unaligned sentence boundaries.
- Make medical parser stand-alone and use delegate mapping combiner instead of
  using a class hierarchy.
- Entity linker is now a token decorator.
- Protect against `unk` (unknown) keys in TUIs.


## [0.0.1] - 2022-01-30
### Added
- Initial version.


<!-- links -->
[Unreleased]: https://github.com/Paul Landes/mednlp/compare/v0.0.2...HEAD
[0.0.2]: https://github.com/Paul Landes/mednlp/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/Paul Landes/mednlp/compare/v0.0.0...v0.0.1
