## makefile automates the build and deployment for python projects


## Build system
#
PROJ_TYPE =		python
PROJ_MODULES =		python/doc python/test python/package python/deploy
PY_TEST_TARGETS =	testcur
PY_TEST_ALL_TARGETS +=	testentlink testparse testfeatures testclinicaltuis testint
CLEAN_DEPS +=		cleanexample


## Project
#
MODEL_DIR ?=		$(HOME)/.cache/zensols/mednlp
MODEL_RESAVE_BIN ?=	src/bin/resave.py
PY_CLI_ARGS +=		--config test-resources/config/default.conf
TEST_SENT ?=		'John Smith was diagnosed with liver disease while in Chicago.'


## Includes
#
include ./zenbuild/main.mk


## Targets
#
# test scispacy entity link db
.PHONY:			testentlink
testentlink:
			@echo "testing entity linking..."
			@make PY_TEST_GLOB=noghci_test_*.py testcur

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
			@echo "integration test: features (harness)"
			@make $(PY_MAKE_ARGS) ARG="show" \
				PY_HARNESS_BIN=example/features/features.py run | \
				diff - test-resources/integration/ex-features.txt || \
				exit 1
			@echo "integration test: features (harness)...ok"

.PHONY:			testintcui2vec
testintcui2vec:
			@echo "integration test: cui2vec"
			@make $(PY_MAKE_ARGS) ARG="similarity -t heart" \
				PY_INVOKE_ARG="-e testint" \
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

# fix warning: "This is an old format. Please re-save the mode..."
.PHONY:			resavemodels
resavemodels:
			@echo "installing deps..."
			@$(PY_PX_BIN) run python -m pip install plac
			@for i in $(MODEL_DIR)/medcat-* ; do \
				echo "resaving models in $$i" ; \
				$(PY_PX_BIN) run python $(MODEL_RESAVE_BIN) $$i ; \
			done


# remove cached files created by the examples
.PHONY:			cleanexample
cleanexample:
			@echo "removing example cache"
			@rm -fr example/cache
