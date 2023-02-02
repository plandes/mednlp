# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).


## [Unreleased]


## [1.0.0] - 2023-02-02
### Changed
- Updated [zensols.util] to 1.12.1.
- Updated [zensols.nlp] to 1.5.0.


## [0.1.1] - 2022-10-02
### Removed
- Make scispacy optional and remove the dependency.  See the test cases in
  [test](test/entlink).


## [0.1.0] - 2022-10-01
### Added
- Unit test in GitHub CI.

### Changed
- Upgrade to spaCy 2.2, MedCAT 3.0, `zensols.nlp` 1.4.0.
- Make `cui2vec` a standard word embedding with vectorizer and layer.
- Replace entity splitter by not embedding named entities as default
  configuration.

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
[Unreleased]: https://github.com/Paul Landes/mednlp/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Paul Landes/mednlp/compare/v0.1.1...v1.0.0
[0.1.1]: https://github.com/Paul Landes/mednlp/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/Paul Landes/mednlp/compare/v0.0.2...v0.1.0
[0.0.2]: https://github.com/Paul Landes/mednlp/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/Paul Landes/mednlp/compare/v0.0.0...v0.0.1

[zensols.util]: https://github.com/plandes/util
[zensols.nlp]: https://github.com/plandes/nlparse
