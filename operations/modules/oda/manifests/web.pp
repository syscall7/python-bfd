class oda::web() {
  $pkgs = [
    'apache2',
    'libapache2-mod-wsgi',
  ]

  package { $pkgs:
    ensure => 'present',
  }

  file { '/opt/oda-bfd':
    ensure => 'directory'
  } ->
  file { '/opt/oda-bfd/build_bfd.sh':
    content => file('oda/build_bfd.sh'),
    mode    => '0700',
  } ->
  file { '/opt/oda-bfd/bfd_lime.patch':
    content => file('oda/bfd_lime.patch')
  }
  exec { 'build_bfd':
    command => '/opt/oda-bfd/build_bfd.sh',
    cwd     => '/opt/oda-bfd',
    unless  => "/usr/bin/test -f /usr/local/oda/lib/libbfd.a",
    timeout => 600,
  }
}