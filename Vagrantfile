Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"

  config.vm.synced_folder ".", "/home/ubuntu/bfd"

  config.vm.provision "shell",
    inline: "sudo apt-get update && \
             sudo apt-get install -y python3 python3-setuptools python3-pip python3-dev && \
             sudo apt-get install -y build-essential zlib1g-dev binutils-multiarch binutils-multiarch-dev"
end
