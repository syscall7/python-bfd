from setuptools import setup, Extension
from setuptools.command.install import install
import subprocess

# Some custom command to run during setup. Each command will spawn a child
# process. Typically, these commands will include steps to install non-Python
# packages. For instance, to install a C++-based library libjpeg62 the following
# two commands will have to be added:
#
#     ['apt-get', 'update'],
#     ['apt-get', '--assume-yes', install', 'libjpeg62'],
#
# First, note that there is no need to use the sudo command because the setup
# script runs with appropriate access.
# Second, if apt-get tool is used then the first command needs to be 'apt-get
# update' so the tool refreshes itself and initializes links to download
# repositories.  Without this initial step the other apt-get install commands
# will fail with package not found errors. Note also -y option which shortcuts
# the interactive confirmation.
#
# The output of custom commands (including failures) will be logged in the
# worker-startup log.
CUSTOM_COMMANDS = [
    ['apt-get', '-y', 'update'],
    ['apt-get', '-y', 'install', 'build-essential', 'zlib1g-dev'],
    ['apt-get', '-y', 'install', 'binutils-multiarch', 'binutils-multiarch-dev'],
]

class CustomCommands(install):
    def RunCustomCommand(self, command_list):
        print('Running command: %s' % command_list)
        p = subprocess.Popen(
            command_list,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # Can use communicate(input='y\n'.encode()) if the command run requires
        # some confirmation.
        stdout_data, _ = p.communicate()
        print('Command output: %s' % stdout_data)
        if p.returncode != 0:
          raise RuntimeError(
              'Command %s failed: exit code: %s' % (command_list, p.returncode))

    def run(self):
        for command in CUSTOM_COMMANDS:
            self.RunCustomCommand(command)
        install.run(self)


bfd = Extension('bfd',
                define_macros = [('MAJOR_VERSION', '1'),
                                 ('MINOR_VERSION', '0'),
                                 # get around automake
                                 ('PACKAGE', 1),
                                 ('PACKAGE_VERSION', 1)],
                libraries = ['bfd-2.26.1-multiarch', 'opcodes-2.26.1-multiarch', 'z'],
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
       ],
       cmdclass={
           'install': CustomCommands
       })
