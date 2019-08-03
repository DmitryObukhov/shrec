# Installations

function agi ()
{
    sudo apt-get install -y -m $@
}

function install()
{
    sudo aptitude install -y $@
}

function pip23()
{
    sudo pip   $@
    sudo pip3  $@
}

function install_docker()
{
  sudo apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  pt-key fingerprint 0EBFCD88
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
  sudo apt-get update
  sudo apt-get install docker-ce docker-ce-cli containerd.io
  sudo docker run hello-world || exit
}

function no_sudo_docker_for()
{
    # Enable Docker without sudo
    groupadd docker
    sudo gpasswd -a $1 docker
    newgrp docker
}

function install_python()
{
    install python python3 python-pip python3-pip
    pip23 install cryptography==2.4.2 paramiko pyasn1
}


###########################################################################

function setup_new_box()
{   # Install and configure software on a new Mint box
    sudo apt-get update
    sudo apt-get install -y aptitude

    install_docker
    no_sudo_docker_for $USER
}

