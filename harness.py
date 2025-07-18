#!/usr/bin/env python

from zensols.cli import ConfigurationImporterCliHarness

if (__name__ == '__main__'):
    st = {0: 'John was diagnosed with kidney failure. He has lung cancer too.',
          1: 'I have palpitations.',
          2: 'He was diagnosed with kidney failure and heart failure in Chicago.',
          3: 'He was diagnosed with kidney failure and chronic ischemic heart disease in the United States.',
          4: 'Hypertension is one of the most important risk factors for heart disease.',
          5: '72 year old man with 3 weeks of Altered Mental Status with PMH of bipolar disorder.',
          6: 'Mr Smith was admitted to the hospital yesterday with severe Parkison\'s disease and a history of CVAs.',
          7: 'Patient with severe Parkison\'s disease and a history of CVAs.',
          # heorrhage misspelling and CKD acronym detected
          8: 'Intracerebral heorrhage and CKD',
          9: 'I\'d say he has severe Parkison\'s disease.'
          }[9]
    harn = ConfigurationImporterCliHarness(
        src_dir_name='src',
        app_factory_class='zensols.mednlp.ApplicationFactory',
        proto_args={
            -1: ['proto', st],
            0: 'config',
            1: ['show', st],
            2: 'atom C0242379'.split(),
            3: 'define C0242379'.split(),
            4: ['search', 'lung cancer'],
            5: ['features', st] + '--ids cui_,tuis_,tui_descs_,pref_name_,lexspan -e'.split(),
            6: ['features', st] + '--out a.csv --ids pref_name_,lexspan -e'.split(),
            7: ['ctakes', st],
            8: ['group', 'byname', '-q', 'Disorders,Drugs'],
            9: ['similarity', 'heart'],
        }[-1],
        proto_factory_kwargs={
            'reload_pattern': r'^zensols.mednlp'},
    )
    harn.run()
