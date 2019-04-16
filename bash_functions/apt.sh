# Installations

function agi ()
{
    apt-get install -y -m $@
}

function inst()
{
    sudo aptitude install -y $@
}

# Install docker
# apt-get update
# apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common
# curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
# pt-key fingerprint 0EBFCD88
# add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
# apt-get update
# apt-get install docker-ce docker-ce-cli containerd.io
# docker run hello-world
