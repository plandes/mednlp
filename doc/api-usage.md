# Medical NLP and Utility API

This API primarily wraps others with the [Zensols Framework] to provide easy
way and reproducible method of utilization and experimentation with medical and
clinical natural language text.  It provides the following functionality:

* [UMLS Access via UTS]
* [Medical Concept and Entity Linking]
* [Using CUI as Word Embeddings](#using-cui-as-word-embeddings)
* [Entity Linking with cTAKES](#entity-linking-with-ctakes)

The rest of this document is structured as a cookbook style tutorial.  Each
sub-section describes the examples in the [examples] directory.

**Important**: many of the examples use [UMLS] UTS service, which requires a
key that is provided by NIH.  If you do not have a key, request one and add it
to the [UTS key file].


## Medical Concept and Entity Linking

Concept linking with [CUIs] is provided using the same interface as the
[Zensols NLP parsing API].  The resource library provided with this package
creates a `mednlp_doc_parser` as shown in the [entity-example].  First we start
with the configuration with file name `features.conf`, which starts with
telling the [CLI] to import the [Zensols NLP package] and this
(`zensols.mednlp`) package:
```ini
[import]
sections = list: imp_conf

[imp_conf]
type = importini
config_files = list:
    resource(zensols.nlp): resources/obj.conf,
    resource(zensols.nlp): resources/mapper.conf,
    resource(zensols.mednlp): resources/lang.conf
```

Next configure the parser with specific features, since otherwise, the parser
will retain all medical and non-medical features:
```ini
[mednlp_doc_parser]
token_feature_ids = set: norm, is_ent, cui, cui_, pref_name_, detected_name_, is_concept, ent_, ent
```

Finally, declare the application, which is needed by the [CLI] glue code to
invoke the class we will write afterward:
```ini
[app]
class_name = ${program:name}.Application
doc_parser = instance: mednlp_doc_parser
```

Next comes the application class:
```python
@dataclass
class Application(object):
    doc_parser: FeatureDocumentParser = field()

    def show(self, sent: str = None):
        if sent is None:
            sent = 'He was diagnosed with kidney failure in the United States.'
        doc: FeatureDocument = self.doc_parser(sent)
        print('first three tokens:')
        for tok in it.islice(doc.token_iter(), 3):
            print(tok.norm)
            tok.write_attributes(1, include_type=False)
```
This uses the document parser to create the feature document, which has both
the medical and linguistic features in tokens (provided by `token_iter()`) of the document.

Use the [CLI] API in the entry point to use the configuration and application
class:
```python
if (__name__ == '__main__'):
    CliHarness(
        app_config_resource='uts.conf',
        app_config_context=ProgramNameConfigurator(
            None, default='uts').create_section(),
        proto_args='',
    ).run()
```

Running the program produces one such token data:
```
...
diagnosed
    cui=11900
    cui_=C0011900
    detected_name_=diagnosed
    ent=13188083023294932426
    ent_=concept
    i=2
    i_sent=2
    idx=7
    is_concept=True
    is_ent=True
    norm=diagnosed
    pref_name_=Diagnosis
...
```
See the full [entity example] for the full example code, which will also output
both linguistic and medical features as a [Pandas] data frame.


## UMLS Access via UTS

NIH provides a very rough REST client using the `requests` library given as an
example.  This API takes that example, adds some "rigor" and structure in a
an easy to use class called `UTSClient`.  This is configured by first defining
paths for where fetched entities are cached:
```ini
[default]
# root directory given by the application, which is the parent directory
root_dir = ${appenv:root_dir}/..
# the directory to hold the cached UMLS data
cache_dir = ${root_dir}/cache
```

Next, import the this package's resource library (`zensols.mednlp`).  Note we
have to refer to sections that substitute the `default` section's data:
```ini
[import]
references = list: uts, default
sections = list: imp_uts_key, imp_conf

[imp_conf]
type = importini
config_file = resource(zensols.mednlp): resources/uts.conf

[imp_uts_key]
type = json
default_section = uts
config_file = ${default:root_dir}/uts-key.json
```
The `imp_uts_key` points to a file where you put add your UTS key, which is
given by NIH.

Now indicate where to cache the [UMLS] data and define our application we'll
write afterward:
```ini
# UTS (UMLS access)
[uts]
cache_file = ${default:cache_dir}/uts-request.dat
```

For brevity the [CLI] application code and configuration is omitted (see [UMLS
Access via UTS] for more detail).

To use the API to first search a term, then print entity information, we can
use the `search_term` method with `get_atoms`:
```python
@dataclass
class Application(object):
    ...
    def lookup(self, term: str = 'heart'):
        # terms are returned as a list of pages with dictionaries of data
        pages: List[Dict[str, str]] = self.uts_client.search_term(term)
        # get all term dictionaries from the first page
        terms: Dict[str, str] = pages[0]
        # get the concept unique identifier
        cui: str = terms['ui']

        # print atoms of this concept
        print('atoms:')
        pprint(self.uts_client.get_atoms(cui))
```
This yields the following output:
```
atoms:
{'ancestors': None,
 'classType': 'Atom',
 'code': 'https://uts-ws.nlm.nih.gov/rest/content/2020AA/source/MTH/NOCODE',
 'concept': 'https://uts-ws.nlm.nih.gov/rest/content/2020AA/CUI/C0018787',
 'contentViewMemberships': [{'memberUri': 'https://uts-ws.nlm.nih.gov/rest/content-views/2020AA/CUI/C1700357/member/A0066369',
                             'name': 'MetaMap NLP View',
                             'uri': 'https://uts-ws.nlm.nih.gov/rest/content-views/2020AA/CUI/C1700357'}],
 'name': 'Heart',
 'obsolete': 'false',
 'rootSource': 'MTH',
...
}
```

See the full [uts example] for the full example code.


## Using CUI as Word Embeddings

[cui2vec] was trained and can be in the same way as [word2vec].  Such examples
is computing a similarity between [UMLS] [CUIs].  This API provides access to
the vectors directly along with all the functionality using [cui2vec] with the
[gensim] package.  This example computes the similarity between two medical
concepts.  For brevity the [CLI] application code and configuration is omitted
(see [UMLS Access via UTS] for more detail).

Let's jump right to how we import everything we need for the [cui2vec] example,
which the `uts` and `cui2vec` resource libraries:
```ini
[imp_conf]
type = importini
config_files = list:
    resource(zensols.mednlp): resources/uts.conf,
    resource(zensols.mednlp): resources/cui2vec.conf
```
The UTS configuration is given as in the [UMLS Access via UTS] section and the
parser is configured as in the [Medical Concept and Entity Linking] section.

With the high level classes given the configuration is class looks similar to
what we've seen before, this time we define a `similarity` method/[CLI] action:
```python
@dataclass
class Application(object):
    def similarity(self, term: str = 'heart disease', topn: int = 5):
```

Next, get the [gensim] `KeyedVectors` instance, which provides (among *many*
other useful methods) one to compute the similarity between two words, or in
our case, two medical [CUIs]:
```python
        embedding: Cui2VecEmbedModel = self.cui2vec_embedding
        kv: KeyedVectors = embedding.keyed_vectors
```

Next we use UTS to get the term we're searching on, use [gensim] to find
similarities, and output them:
```python
        res: List[Dict[str, str]] = self.uts_client.search_term(term)
        cui: str = res[0]['ui']
        sims_by_word: List[Tuple[str, float]] = kv.similar_by_word(cui, topn)
        for rel_cui, proba in sims_by_word:
            rel_atom: Dict[str, str] = self.uts_client.get_atoms(rel_cui)
            rel_name = rel_atom.get('name', 'Unknown')
            print(f'{rel_name} ({rel_cui}): {proba * 100:.2f}%')
```

The output contains the top (`topn`) 5 matches and their similarity to the
search term in the example `heart`:
```
Heart failure (C0018801): 72.03%
Atrial Premature Complexes (C0033036): 71.53%
Chronic myocardial ischemia (C0264694): 69.68%
Right bundle branch block (C0085615): 69.34%
First degree atrioventricular block (C0085614): 69.09%
```

See the full [cui2vec example] for the full example code.


## Entity Linking with cTAKES

This package provides an interface to [cTAKES], which primarily manages the
file system and invokes the Java program to produce results.  It then uses the
[ctakes-parser] to create a data frame of features and linked entities from
tokens of the source text.

The configuration is a bit more involved since you have to indicate where the
[cTAKES] program is installed, and provide your NIH key as detailed in the
[UMLS Access via UTS] section:
```ini
[import]
# refer to sections for which we need substitution in this file
references = list: default, ctakes, uts
sections = list: imp_env, imp_uts_key, imp_conf

# expose the user HOME environment variable
[imp_env]
type = environment
section_name = env
includes = set: HOME

# import the Zensols NLP UTS resource library
[imp_conf]
type = importini
config_files = list:
    resource(zensols.mednlp): resources/uts.conf,
    resource(zensols.mednlp): resources/ctakes.conf

# indicate where Apache cTAKES is installed
[ctakes]
home = ${env:home}/opt/app/ctakes-4.0.0.1
source_dir = ${default:cache_dir}/ctakes/source
```
For brevity the [CLI] application code and configuration is omitted, and other
configuration given in previous sections (see [UMLS Access via UTS] for more
detail). See the full [ctakes example] for the full example code.

The pertinent snippet to get the [Pandas] data frame from the medical text is
very simple:
```python
@dataclass
class Application(object):
    def entities(self, sent: str = None, output: Path = None):
        if sent is None:
            sent = 'He was diagnosed with kidney failure in the United States.'
        self.ctakes_stash.set_documents([sent])
        df: pd.DataFrame = self.ctakes_stash['0']
        print(df)
        if output is not None:
            df.to_csv(output)
            print(f'wrote: {output}')
```
The `set_documents` expects a list of text, which is saved to disk.  When
[cTAKES] is run, the directory where this list of text is saved (one file per
element in the list).  The access to the [Stash] accesses the first document by
element ID.  **Note**: the element ID has to be a string to follow the [Stash]
API.


<!-- links -->
[UMLS Access via UTS]: #umls-access-via-uts
[Medical Concept and Entity Linking]: #medical-concept-and-entity-linking

[UMLS]: https://www.nlm.nih.gov/research/umls/
[CUIs]: https://www.nlm.nih.gov/research/umls/new_users/online_learning/Meta_005.html
[cui2vec]: https://arxiv.org/abs/1804.01486
[word2vec]: https://arxiv.org/abs/1301.3781

[Pandas]: https://pandas.pydata.org
[gensim]: https://radimrehurek.com/gensim/
[cTAKES]: https://ctakes.apache.org
[ctakes-parser]: https://pypi.org/project/ctakes-parser

[Zensols Framework]: https://arxiv.org/abs/2109.03383
[CLI]: https://plandes.github.io/util/doc/command-line.html
[Stash]: https://plandes.github.io/util/api/zensols.persist.html#zensols.persist.domain.Stash
[Zensols NLP package]: https://github.com/plandes/nlparse
[Zensols NLP parsing API]: https://plandes.github.io/nlparse/doc/feature-doc.html

[examples]: https://github.com/plandes/mednlp/tree/master/example
[entity example]: https://github.com/plandes/mednlp/tree/master/example/features
[ctakes example]: https://github.com/plandes/mednlp/tree/master/example/ctakes
[cui2vec example]: https://github.com/plandes/mednlp/tree/master/example/cui2vec
[uts example]: https://github.com/plandes/mednlp/tree/master/example/uts
[UTS key file]: https://github.com/plandes/mednlp/tree/master/example/uts-key.json
