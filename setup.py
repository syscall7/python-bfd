from setuptools import setup, Extension
from setuptools.command.install import install
import subprocess
import sys

bfd = Extension('bfd',
                define_macros = [('MAJOR_VERSION', '1'),
                                 ('MINOR_VERSION', '0'),
                                 # get around automake
                                 ('PACKAGE', 1),
                                 ('PACKAGE_VERSION', 1)],
                libraries = ['bfd-2.30-multiarch', 'opcodes-2.30-multiarch', 'z'],
                extra_compile_args=['-fpermissive'],
                language="c++", # generate and compile C++ code
                sources = ['bfd/bfd.pyx'])

setup (name = 'PythonBFD',
       version = '1.0',
       description = 'This is the BFD package',
       author = 'Anthony DeRosa',
       author_email = 'Anthony.DeRosa@syscall7.com',
       url = '',
       long_description = '''Access to BFD library from Python''',
       ext_modules = [bfd],
       setup_requires=[
           # Setuptools 18.0 properly handles Cython extensions.
           'setuptools>=18.0',
           'Cython==0.22.1'
       ])
