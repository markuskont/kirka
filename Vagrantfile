# -*- mode: ruby -*-
# vi: set ft=ruby :

#$NS = <<SCRIPT
#
#sudo cat <<REPO >> /etc/apt/sources.list
#deb http://http.us.debian.org/debian/ testing non-free contrib main
#REPO
#
#sudo apt-get update
#sudo apt-get install -y bind9 vim htop tmux git golang/testing < /dev/null
#
#sudo cat <<BASHRC | sudo tee -a /root/.bashrc /home/vagrant/.bashrc
#alias ls='ls $LS_OPTIONS'
#alias ll='ls $LS_OPTIONS -la'
#export GOPATH=/home/vagrant
#BASHRC
#
#sudo cat <<VIMRC | sudo tee -a /root/.vimrc /home/vagrant/.vimrc
#syntax on
#VIMRC
#
#sudo cat <<STATS >> /etc/bind/named.conf.local
#statistics-channels {
#        inet 127.0.0.1 port 8080 allow { 127.0.0.1; };
#};
#STATS
#sudo service bind9 restart
#
#wget -q -O influx.deb https://s3.amazonaws.com/influxdb/influxdb_0.11.1-1_amd64.deb
#sudo dpkg -i influx.deb
#sudo service influxdb start
#
##wget -q -O telegraf.deb http://get.influxdb.org/telegraf/telegraf_0.12.0-1_amd64.deb
##sudo dpkg -i telegraf.deb
##sudo service telegraf start
#
#sudo chown -R vagrant:vagrant /home/vagrant/
#
#SCRIPT

$GO = <<SCRIPT
  sudo add-apt-repository ppa:ubuntu-lxc/lxd-stable -y
  sudo apt-get update && sudo apt-get install golang -y
SCRIPT

$NODEJS = <<SCRIPT
  curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
  sudo apt-get install nodejs build-essential -y
SCRIPT

$SYSLOGNG = <<SCRIPT
  wget -qO - http://download.opensuse.org/repositories/home:/laszlo_budai:/syslog-ng/Debian_8.0/Release.key | sudo apt-key add -
  sudo echo "deb http://download.opensuse.org/repositories/home:/laszlo_budai:/syslog-ng/xUbuntu_14.04 ./" > /etc/apt/sources.list.d/syslog-ng.list
  sudo apt-get update && sudo apt-get remove rsyslog -y && sudo apt-get install syslog-ng -y
SCRIPT

$PACKAGES = <<SCRIPT
  sudo apt-get install python-daemon jq htop tmux -y
SCRIPT

boxes = [
  {
    :name => "kirka",
    :mem  => "2048",
    :cpu  => "4",
    :ip   => "192.168.56.166"
  },
]

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"

  boxes.each do |opts|
    config.vm.define opts[:name] do |config|
      config.vm.hostname = opts[:name]
      config.vm.network 'private_network', ip: opts[:ip]

      config.vm.provider "virtualbox" do |v|
        v.customize ["modifyvm", :id, "--memory", opts[:mem]]
        v.customize ["modifyvm", :id, "--cpus", opts[:cpu]]
      end
      config.vm.provision "shell", inline: $GO
      config.vm.provision "shell", inline: $NODEJS
      config.vm.provision "shell", inline: $SYSLOGNG
      config.vm.provision "shell", inline: $PACKAGES
      #config.vm.synced_folder ".", "/home/vagrant/src/github.com/influxdata/telegraf"
    end
  end
end
