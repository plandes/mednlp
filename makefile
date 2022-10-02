## makefile automates the build and deployment for python projects


## build config

# type of project
PROJ_TYPE =		python
PROJ_MODULES =		git python-resources python-cli python-doc python-doc-deploy
PIP_ARGS +=		--use-deprecated=legacy-resolver
PY_DEP_POST_DEPS +=	modeldeps
INFO_TARGETS +=		appinfo
ADD_CLEAN +=		medcat.log
CLEAN_DEPS +=		pycleancache cleanexample

# project
ENTRY_BIN =		./mednlp


## project specific

# add app configuration to command line arguments
PY_CLI_ARGS +=		-c test-resources/mednlp.conf

PY_SRC_TEST_PAT ?=	'test_parse.py'


include ./zenbuild/main.mk

.PHONY:			appinfo
appinfo:
			@echo "app-resources-dir: $(RESOURCES_DIR)"
			@echo "proj-lib-url-version: $(PROJ_LIB_URL_VERSION)"

.PHONY:			modeldeps
modeldeps:
			$(PIP_BIN) install $(PIP_ARGS) -r $(PY_SRC)/requirements-model.txt
			$(PIP_BIN) install $(PIP_ARGS) -r $(PY_SRC)/requirements-force.txt

.PHONY:			testrun
testrun:
			$(ENTRY_BIN) show $(PY_CLI_ARGS) "Spinal and bulbar muscular atrophy (SBMA)"

.PHONY:			testfeatures
testfeatures:
			$(ENTRY_BIN) features $(PY_CLI_ARGS) \
				--ids pref_name_,loc --onlymedical \
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
testall:		test testrun testfeatures clinicaltuis
			example/uts/uts.py
			example/features/features.py show
			example/cui2vec/cui2vec.py similarity -t heart
