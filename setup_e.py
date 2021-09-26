from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('nordicSigleDownload.py', base=base, targetName = 'Download')
]

setup(name='NordicSoftDownload',
      version = '.0.1',
      description = 'Download nordic soft single',
      options = dict(build_exe = buildOptions),
      executables = executables)
