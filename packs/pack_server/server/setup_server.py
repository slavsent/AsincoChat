import os
import sys
from cx_Freeze import setup, Executable


build_exe_options = {
      "packages": ["log", "server_utilit", "unit_tests"],
      'include_files': [os.path.join(sys.base_prefix, 'DLLs', 'sqlite3.dll')],
}
setup(name='sents_server_chat_exe',
      version='1.0',
      description='Server packet',
      options={
            "build_exe": build_exe_options
      },
      executables=[Executable('server_v1.py', base='Win32GUI')]
      )
