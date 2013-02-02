from distutils.core import setup
from Pyrex.Distutils.extension import Extension
from Pyrex.Distutils import build_ext

module1 = Extension('bfd',
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
       long_description = '''
First attempt to access BFD library from Python
''',
       cmdclass = {'build_ext': build_ext},
       ext_modules = [module1])

