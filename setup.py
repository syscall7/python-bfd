from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

bfd = Extension('bfd',
                    define_macros = [('MAJOR_VERSION', '1'),
                                     ('MINOR_VERSION', '0'),
                                     # get around automake
                                     ('PACKAGE', 1),
                                     ('PACKAGE_VERSION', 1)],
                    include_dirs = ['/usr/local/oda/include'],
                    libraries = ['bfd', 'opcodes', 'iberty', 'z'],
                    library_dirs = ['/usr/local/oda/lib'],
                    sources = ['bfd.pyx'])

setup (name = 'PythonBFD',
       version = '1.0',
       description = 'This is the BFD package',
       author = 'Anthony DeRosa',
       author_email = 'Anthony.DeRosa@gmail.com',
       url = '',
       long_description = '''Access to BFD library from Python''',
       cmdclass = {'build_ext': build_ext},
       ext_modules = [bfd])

