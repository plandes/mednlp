## makefile automates the build and deployment for python projects


## Build system
#
PROJ_TYPE =		python
PROJ_MODULES =		python/doc python/deploy
PY_CLI_ARGS +=		--config test-resources/config/default.conf
ADD_CLEAN +=		medcat.log
CLEAN_DEPS +=		cleanexample



PY_TEST_GLOB ?=		test_combined.py


## Project
#
ENTRY_BIN =		./mednlp
TEST_SENT =		'John Smith was diagnosed with liver disease while in Chicago.'


## Includes
#
include ./zenbuild/main.mk


## Targets
#
# test scispacy entity link db
.PHONY:			testentlink
testentlink:
			make PY_SRC_TEST=test/entlink test

# test parsing
.PHONY:			testparse
testparse:
			@echo "integration test: parse"
			@make $(PY_MAKE_ARGS) run \
				ARG="show $(PY_CLI_ARGS) $(TEST_SENT)" | \
				diff - test-resources/integration/parse.txt || \
				exit 1
			@echo "integration test: parse...ok"

# not CUIs/results are after defaulting to notebook only MedCAT model
.PHONY:			testfeatures
testfeatures:
			@echo "integration test: features"
			@make $(PY_MAKE_ARGS) run \
				ARG="features $(PY_CLI_ARGS) --ids pref_name_,loc --medonly $(TEST_SENT)" | \
				diff - test-resources/integration/features.csv || \
				exit 1
			@echo "integration test: features...ok"

# test CTS (UMLS terminology service)
.PHONY:			testclinicaltuis
testclinicaltuis:
			@echo "integration test: tuis"
			@make $(PY_MAKE_ARGS) run \
				ARG="$(PY_CLI_ARGS) group byname -q Anatomy,Devices,Disorders,Drugs,Genes,Living,Objects,Occupations,Phenomena,Physiology,Procedures" | \
				diff - test-resources/integration/tuis.txt || \
				exit 1
			@echo "integration test: tuis...ok"

# integration tests
.PHONY:			testintfeat
testintfeat:
			@echo "integration test: features"
			@make $(PY_MAKE_ARGS) ARG="show" \
				PY_HARNESS_BIN=example/features/features.py run | \
				diff - test-resources/integration/ex-features.txt || \
				exit 1
			@echo "integration test: features...ok"

.PHONY:			testintcui2vec
testintcui2vec:
			@echo "integration test: cui2vec"
			@make $(PY_MAKE_ARGS) ARG="show similarity -t heart" \
				PY_HARNESS_BIN=example/cui2vec/cui2vec.py run 2>&1 | \
				grep -v RuntimeWarning | \
				grep -v 'dists = dot' | \
				diff - test-resources/integration/cui2vec.txt || \
				exit 1
			@echo "integration test: cui2vec...ok"

.PHONY:			testintuts
testintuts:
			@echo "integration test: uts"
			@make $(PY_MAKE_ARGS) \
				PY_HARNESS_BIN=example/uts/uts.py run | \
				diff - test-resources/integration/uts.txt || \
				exit 1
			@echo "integration test: uts...ok"

.PHONY:			testint
testint:		testintfeat testintcui2vec testintuts



# unit and integration tests
.PHONY:			testall
testall:		test testentlink testparse testfeatures testclinicaltuis testint

# remove cached files created by the examples
.PHONY:			cleanexample
cleanexample:
			@echo "removing example cache"
			@rm -fr example/cache
