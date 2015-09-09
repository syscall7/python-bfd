class oda::mysql {

  class { '::mysql::server':
    root_password           => '***REMOVED***',
    remove_default_accounts => true,
    override_options => {
      'mysqld' => {
        innodb_file_per_table   => "ON",
        innodb_flush_method     => 'O_DIRECT',
        innodb_log_file_size    => '1G',
        innodb_buffer_pool_size => '4G'
      }
    }
  }
}