## makefile automates the build and deployment for python projects


## Build system
#
PROJ_TYPE =		python
PROJ_MODULES =		git python-resources python-cli python-doc python-doc-deploy markdown
PY_DEP_POST_DEPS +=	modeldeps
INFO_TARGETS +=		appinfo
ADD_CLEAN +=		medcat.log
CLEAN_DEPS +=		pycleancache cleanexample
# add app configuration to command line arguments
PY_CLI_ARGS +=		-c test-resources/mednlp.conf


## Project
#
ENTRY_BIN =		./mednlp


## Includes
#
include ./zenbuild/main.mk


## Targets
#
.PHONY:			appinfo
appinfo:
			@echo "app-resources-dir: $(RESOURCES_DIR)"
			@echo "proj-lib-url-version: $(PROJ_LIB_URL_VERSION)"

.PHONY:			modeldeps
modeldeps:
			$(PIP_BIN) install $(PIP_ARGS) -r resources/requirements/model.txt --no-deps

.PHONY:			testentlink
testentlink:
			make PY_SRC_TEST=test/entlink test

.PHONY:			testrun
testrun:
			$(ENTRY_BIN) show $(PY_CLI_ARGS) "Spinal and bulbar muscular atrophy (SBMA)"

.PHONY:			testfeatures
testfeatures:
			$(ENTRY_BIN) features $(PY_CLI_ARGS) \
				--ids pref_name_,loc --medonly \
				"Spinal and bulbar muscular atrophy (SBMA)"

.PHONY:			clinicaltuis
clinicaltuis:
			$(ENTRY_BIN) group byname $(PY_CLI_ARGS) -q \
				Anatomy,Devices,Disorders,Drugs,Genes,Living,Objects,Occupations,Phenomena,Physiology,Procedures

.PHONY:			reinstallnmslib
reinstallnmslib:
			@echo "reinstall no binary nmslib for speed and warnings"
			pip uninstall -y nmslib || true
			pip install --no-binary :all: nmslib

.PHONY:			cleanlib
cleanlib:
			rm -r $(PROJ_LIB)

.PHONY:			cleanexample
cleanexample:
			rm -fr example/cache

.PHONY:			testall
testall:		test testentlink testrun testfeatures clinicaltuis
			example/uts/uts.py
			example/features/features.py show
			example/cui2vec/cui2vec.py similarity -t heart
