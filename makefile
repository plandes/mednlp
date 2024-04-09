## makefile automates the build and deployment for python projects


## Build system
#
PROJ_TYPE =		python
PROJ_MODULES =		git python-resources python-cli python-doc python-doc-deploy markdown
PY_DEP_POST_DEPS +=	modeldeps
PY_CLI_ARGS +=		--config test-resources/config/default.conf
ADD_CLEAN +=		medcat.log
CLEAN_DEPS +=		pycleancache cleanexample

## Project
#
ENTRY_BIN =		./mednlp
TEST_SENT =		"John Smith was diagnosed with liver disease while in Chicago."


## Includes
#
include ./zenbuild/main.mk


## Targets
#
# install models and their dependencies instead of letting the app do it
.PHONY:			modeldeps
modeldeps:
			$(PIP_BIN) install $(PIP_ARGS) -r \
				resources/requirements/model.txt --no-deps

# try to reinstall the `nmslib` python package
.PHONY:			reinstallnmslib
reinstallnmslib:
			@echo "reinstall no binary nmslib for speed and warnings"
			pip uninstall -y nmslib || true
			pip install --no-binary :all: nmslib

# test scispacy entity link db
.PHONY:			testentlink
testentlink:
			make PY_SRC_TEST=test/entlink test

# test parsing
.PHONY:			testparse
testparse:
			@$(ENTRY_BIN) show $(PY_CLI_ARGS) $(TEST_SENT) | \
				diff - test-resources/integration/parse.txt || \
				exit 1

# not CUIs/results are after defaulting to notebook only MedCAT model
.PHONY:			testfeatures
testfeatures:
			@$(ENTRY_BIN) features $(PY_CLI_ARGS) \
				--ids pref_name_,loc --medonly $(TEST_SENT) | \
				diff - test-resources/integration/features.csv || \
				exit 1

# test CTS (UMLS terminology service)
.PHONY:			testclinicaltuis
testclinicaltuis:
			@$(ENTRY_BIN) group byname $(PY_CLI_ARGS) -q \
				Anatomy,Devices,Disorders,Drugs,Genes,Living,Objects,Occupations,Phenomena,Physiology,Procedures | \
				diff - test-resources/integration/tuis.txt || \
				exit 1

# run unit tests and examples as integration tests
.PHONY:			testall
testall:		test testentlink testparse testfeatures testclinicaltuis
			@example/features/features.py show | \
				diff - test-resources/integration/ex-features.txt || \
				exit 1
			@example/cui2vec/cui2vec.py similarity -t heart 2>&1 | \
				grep -v RuntimeWarning | \
				grep -v 'dists = dot' | \
				diff - test-resources/integration/cui2vec.txt || \
				exit 1
			@example/uts/uts.py | \
				diff - test-resources/integration/uts.txt || \
				exit 1

# remove cached files created by the examples
.PHONY:			cleanexample
cleanexample:
			rm -fr example/cache
