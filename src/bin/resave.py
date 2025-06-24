#!/usr/bin/env python

"""Resave a MedCat model to remove the warning:

  Found config in CDB for model (.../medcat-umls-1). This is an old
  format. Please re-save the model in the new format to avoid potential issues.

*Important!*: Backup the entire directory first!  This script is very
destructive!

:see: `GitHub: <https://github.com/CogStack/MedCAT/issues/548#issuecomment-2994476802>`_

"""
from pathlib import Path
import shutil
import plac
from medcat.cat import CAT


KEEPS: str = 'umls-groups.txt umls-tuis.txt'.split()
"""Files to keep (move from the old dir to the new)."""


@plac.annotations(
    path=('The path to the medcat model meta_Status.zip',
          'positional', None, Path))
def resave_medcat_model(path: Path):
    """Resave a MedCat model to remove warnings."""
    # model file
    old_model: Path = path / 'meta_Status.zip'
    # directory with the model zip
    old_model_dir: Path = old_model.parent
    old_model_status_dir: Path = old_model_dir / 'meta_Status'
    print(f'delete old model dir (expects to not be uncompressed): {old_model_status_dir}')
    if old_model_status_dir.is_dir():
        shutil.rmtree(old_model_status_dir)
    print(f'loading the old model: {old_model}...')
    if not old_model.is_file():
        raise OSError(f'Model not found: {old_model}')
    cat = CAT.load_model_pack(old_model)
    print(f'creating a new model with the new format: {old_model_dir.parent}...')
    new_name: str = cat.create_model_pack(old_model_dir.parent)
    # the new model zip file it created and directory with the model contents
    new_model_zip: Path = old_model_dir.parent / f'{new_name}.zip'
    new_model_dir: Path = old_model_dir.parent / new_name
    # keep any non-model files
    for name in KEEPS:
        old_file: Path = old_model_dir / name
        new_file: Path = new_model_dir / name
        if old_file.exists():
            print(f'moving {old_file} -> {new_file}')
            old_file.rename(new_file)
    print(f'delete the model zip file it created: {old_model_dir}')
    shutil.rmtree(old_model_dir)
    print(f'delete the new model zip file: {new_model_zip}')
    new_model_zip.unlink()
    print(f'but keeping the directory and rename it in place: {new_model_dir} -> {old_model_dir}')
    new_model_dir.rename(old_model_dir)


if (__name__ == '__main__'):
    plac.call(resave_medcat_model)
