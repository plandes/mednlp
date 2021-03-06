# Medical natural language parsing and utility library

[![PyPI][pypi-badge]][pypi-link]
[![Python 3.9][python39-badge]][python39-link]
[![Build Status][build-badge]][build-link]

A natural language medical domain parsing library.  This library:

- Provides an interface to the [UTS] ([UMLS] Terminology Services) RESTful
  service with data caching (NIH login needed).
- Wraps the [MedCAT] library by parsing medical and clinical text into first
  class Python objects reflecting the structure of the natural language
  complete with [UMLS] entity linking with [CUIs] and other domain specific
  features.
- Combines non-medical (such as POS and NER tags) and medical features (such as
  [CUIs]) in one API and resulting data structure and/or as a [Pandas] data
  frame.
- Provides [cui2vec] as a [word embedding model] for either fast indexing and
  access or to use directly as features in a [Zensols Deep NLP embedding layer]
  model.
- Provides access to [cTAKES] using as a dictionary like [Stash] abstraction.
- Includes a command line program to access all of these features without
  having to write any code.


## Documentation

See the [full documentation](https://plandes.github.io/mednlp/index.html).
The [API reference](https://plandes.github.io/mednlp/api.html) is also
available.


## Obtaining

The easiest way to install the command line program is via the `pip` installer:
```bash
pip3 install zensols.mednlp
```

Binaries are also available on [pypi].

If the [cui2vec] functionality is used, the [Zensols Deep NLP library]
is also needed, which is stalled with `pip install zensols.deepnlp`.


## Attribution

This API utilizes the following frameworks:

* [MedCAT]: used to extract information from Electronic Health Records (EHRs)
  and link it to biomedical ontologies like SNOMED-CT and UMLS.
* [cTAKES]: a natural language processing system for extraction of information
  from electronic medical record clinical free-text.
* [cui2vec]: a new set of (like word) embeddings for medical concepts learned
  using an extremely large collection of multimodal medical data.
* [Zensols Deep NLP library]: a deep learning utility library for natural
  language processing that aids in feature engineering and embedding layers.
* [ctakes-parser]: parses [cTAKES] output in to a [Pandas] data frame.


## Citation

If you use this project in your research please use the following BibTeX entry:
```
@article{Landes_DiEugenio_Caragea_2021,
  title={DeepZensols: Deep Natural Language Processing Framework},
  url={http://arxiv.org/abs/2109.03383},
  note={arXiv: 2109.03383},
  journal={arXiv:2109.03383 [cs]},
  author={Landes, Paul and Di Eugenio, Barbara and Caragea, Cornelia},
  year={2021},
  month={Sep}
}
```

## Community

Please star the project and let me know how and where you use this API.
Contributions as pull requests, feedback and any input is welcome.


## Changelog

An extensive changelog is available [here](CHANGELOG.md).


## License

[MIT License](LICENSE.md)

Copyright (c) 2021 - 2022 Paul Landes


<!-- links -->
[pypi]: https://pypi.org/project/zensols.mednlp/
[pypi-link]: https://pypi.python.org/pypi/zensols.mednlp
[pypi-badge]: https://img.shields.io/pypi/v/zensols.mednlp.svg
[python39-badge]: https://img.shields.io/badge/python-3.9-blue.svg
[python39-link]: https://www.python.org/downloads/release/python-390
[build-badge]: https://github.com/plandes/mednlp/workflows/CI/badge.svg
[build-link]: https://github.com/plandes/mednlp/actions

[MedCAT]: https://github.com/CogStack/MedCAT
[Pandas]: https://pandas.pydata.org
[ctakes-parser]: https://pypi.org/project/ctakes-parser

[UTS]: https://uts.nlm.nih.gov/uts/
[UMLS]: https://www.nlm.nih.gov/research/umls/
[CUIs]: https://www.nlm.nih.gov/research/umls/new_users/online_learning/Meta_005.html
[cui2vec]: https://arxiv.org/abs/1804.01486
[cTAKES]: https://ctakes.apache.org
[word embedding model]: https://plandes.github.io/deepnlp/api/zensols.deepnlp.embed.html#zensols.deepnlp.embed.domain.WordEmbedModel
[Zensols NLP parsing API]: https://plandes.github.io/nlparse/doc/feature-doc.html
[Zensols Deep NLP library]: https://github.com/plandes/deepnlp
[Zensols Deep NLP embedding layer]: https://plandes.github.io/deepnlp/api/zensols.deepnlp.layer.html#zensols.deepnlp.layer.embed.EmbeddingNetworkModule
[Stash]: https://plandes.github.io/util/api/zensols.persist.html#zensols.persist.domain.Stash
