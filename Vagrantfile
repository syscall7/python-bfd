Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"

  config.vm.synced_folder ".", "/home/ubuntu/bfd"

  config.vm.provision "shell",
    inline: "sudo apt-get update && sudo apt-get install -y python python-setuptools python-pip python-dev"
end
