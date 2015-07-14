from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('score.py', base=base)
]

setup(name='test',
      version = '0.1',
      description = 'test desc',
      options = dict(build_exe = buildOptions),
      executables = executables)
