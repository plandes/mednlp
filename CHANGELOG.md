# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).


## [Unreleased]

### Removed
- Deprecated feature document parser `mednlp_combine_medfirst_doc_parser` from
  resource library.

### Changed
- Renamed `MeddicalFeatureDocumentParser` to `MedCatFeatureDocumentParser`
  since the parser only adds MedCAT CUIs.
- Fixed the configured parser that adds both ScispaCy biomed entities and
  MedCAT CUIs in `mednlp_combine_biomed_doc_parser`.
- Separated combiner with non-combiner models in configuration space.  The
  non-combiners (biomed ScispaCy and MedCAT) are parses that are used in their
  respective combiners.  These are then used by a new composite parser that
  uses both (`mednlp_combine_biomed_doc_parser`).  Unit test case added for
  all configured parsers.


## [1.6.0] - 2024-02-27
### Added
- Added a ScispaCy biomedical document parser, which is enabled by setting
  `mednlp_default:doc_parser = mednlp_combine_biomed_doc_parser`.  This uses
  better linguistic features and detects more entity span(s).

### Changed
- Fixed normalize token and sentence/token indexes from being clobbered by
  combined medical parsers.
- Fixed numeric entity feature from the combined medical parser is non-zero
  for medical entities.
- Combined medical parser defines linguistic and medical features in the
  document parser object instance.


## [1.5.0] - 2023-12-05
### Changed
- Upgrade libraries: `numpy`, `lxml`, `scikitlearn`, `scipy`, `medcat`.
- Added `scispacy` dependency.

### Added
- Support for Python 3.11.

### Removed
- Support for Python 3.9.


## [1.4.1] - 2023-09-08
### Changed
- Fix unit tests using the model provided for the MedCAT tutorials.
- Re-enable GitHub workflow unit tests CI.


## [1.4.0] - 2023-08-16
Downstream moderate risk update release.

### Changed
- Switch order of medical specific and general spaCy language parsing and
  chunking.  Now the medical parser is the source parser and the default spaCy
  parser is the target in `MappingCombinerFeatureDocumentParser`.  This was
  done to get better sentence chunking as MedCAT (used in the medical parser)
  does not sentence chunk well as it was not designed for it.
- Upgrade to [zensols.util] 1.13.0
- Fix `cui2vec` weight archive re-download on each access.
- Mapping combiner default is to use token's character absolute index.


## [1.3.2] - 2023-06-29
### Added
- Feature document parser shortcut from application factory.

### Changed
- Resource library configuration to clean up model resources after download.


## [1.3.1] - 2023-06-27
### Changed
- Updated to [zensols.nlp] to 1.7.2 and use its new feature to auto load any
  missing spaCy base model(s).
- Remove configuration file requirement from the CLI.
- Fix spaCy dependency requirement to align with `scipy` and  [zensols.nlp].


## [1.3.0] - 2023-06-20
### Changed
- Fix contraction tokenization.  This was done by swapping the target and
  source parser in the `lang.conf:mednlp_combine_doc_parser` resource library
  configuration.


## [1.2.0] - 2023-06-09
### Changed
- Upgrade to [medcat] 1.7.0.
- Better UTS error handling with raised exceptions and messages.


## [1.1.0] - 2023-04-05
### Changed
- Install missing models and packages on start up.
- Updated [zensols.install] to 0.2.1
- Updated [zensols.nlp] to 1.6.0.


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
[Unreleased]: https://github.com/Paul Landes/mednlp/compare/v1.6.0...HEAD
[1.6.0]: https://github.com/Paul Landes/mednlp/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/Paul Landes/mednlp/compare/v1.4.1...v1.5.0
[1.4.1]: https://github.com/Paul Landes/mednlp/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/Paul Landes/mednlp/compare/v1.3.2...v1.4.0
[1.3.2]: https://github.com/Paul Landes/mednlp/compare/v1.3.1...v1.3.2
[1.3.1]: https://github.com/Paul Landes/mednlp/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/Paul Landes/mednlp/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/Paul Landes/mednlp/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Paul Landes/mednlp/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Paul Landes/mednlp/compare/v0.1.1...v1.0.0
[0.1.1]: https://github.com/Paul Landes/mednlp/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/Paul Landes/mednlp/compare/v0.0.2...v0.1.0
[0.0.2]: https://github.com/Paul Landes/mednlp/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/Paul Landes/mednlp/compare/v0.0.0...v0.0.1

[zensols.util]: https://github.com/plandes/util
[zensols.nlp]: https://github.com/plandes/nlparse
[zensols.install]: https://github.com/plandes/install
[medcat]: https://github.com/CogStack/MedCAT
