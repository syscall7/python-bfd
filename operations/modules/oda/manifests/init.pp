class oda {

  $pkgs = [
    'libxml2-dev',
    'libxslt1-dev',
    'subversion',
    'texinfo',
    'patch',
    'bzip2',
    'gcc',
    'make',
    'autoconf',
    'python-pip',
    'python-virtualenv',
    'libpython-dev',
    'libssl-dev',
    'libffi-dev',
    'cython',
    'libmysqlclient-dev',
  ]

  exec { "apt-update":
    command => "/usr/bin/apt-get update"
  }
  Exec["apt-update"] -> Package <| |>

  package { $pkgs:
    ensure => 'installed',
  }

  include oda::mysql
  include oda::web

}