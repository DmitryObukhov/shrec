# Integration:
# 1. git clone https://github.com/DmitryObukhov/shrec.git
# 2. add to ~/.bashrc the code below
#
# source /home/USER/shrec/bash/bash_functions.sh

PATH=$PATH:~/shrec:~/shrec/tools:~/shrec/bash

alias pins='python   -m pip --proxy $http_proxy install --upgrade '
alias pins3='python3 -m pip --proxy $http_proxy install --upgrade '
alias ..='cd ..'
alias apt-get='sudo apt-get'
alias update='sudo apt-get update && sudo apt-get upgrade -y'
alias install='sudo apt-get install --upgrade -y'
alias ping='ping -c 5'
alias fastping='ping -c 100 -s.2'
alias root='sudo -i'
alias su='sudo -i'
alias reboot='sudo /sbin/reboot'
alias poweroff='sudo /sbin/poweroff'
alias halt='sudo /sbin/halt'
alias shutdown='sudo /sbin/shutdown'
alias reboot='sudo shutdown -r now'
alias rerc='source ~/.bashrc'

function cdp ()
{
    PATTERN=$1
    COUNT=$(find . -path $PATTERN -type d  | wc -l)
    if [ "$COUNT" -lt "1" ]; then
       echo "Cannot find pattern $PATTERN in the tree below";
       return
    fi

    if [ "$COUNT" -gt "1" ]; then
       echo "Too many matches for pattern $PATTERN";
       find . -path $PATTERN -type d
       return
    fi

    CANDIDATE=$(find . -path $PATTERN -type d)
    cd $CANDIDATE
}

function git-acp ()
{
    git add --all
    git commit -m \""$@"\"
    git push
}

function git-new ()
{
    PATTERN=$1
    if [ -f .repo ]; then  # Find file .repo in the current dir.
        echo "Reading repo URL from file .repo"
        REPO=$(cat .repo)
        echo "Using $REPO"
    else
        echo "Cannot find file .repo"
        ls -l
        return
    fi

    echo "Cloning $PATTERN from $REPO"

    COUNT=$(git ls-remote $REPO | grep $PATTERN  | wc -l)

    if [ "$COUNT" -lt "1" ]; then
       echo "Cannot find pattern $PATTERN in the list of branches";
       return
    fi

    if [ "$COUNT" -gt "1" ]; then
       echo "Too many branches match pattern $PATTERN";
       git ls-remote $DEFREPO | grep $PATTERN
       return
    fi

    BRANCH=$(git ls-remote $REPO | grep $PATTERN  | awk '{print $2}')
    BRANCH=${BRANCH#"refs/heads/"}

    mkdir $PATTERN                || return
    git clone $REPO $PATTERN      || return
    cd $PATTERN                   || return
    git checkout $BRANCH          || return
    git log -n 1
    git status
}

function git-co ()
{
        PATTERN=$1
        COUNT=$(git branch -a | grep $PATTERN  | wc -l)

        if [ "$COUNT" -lt "1" ]; then
           echo "Cannot find pattern $PATTERN in the list of branches";
           return
        fi


        if [ "$COUNT" -gt "1" ]; then
           echo "Too many branches match pattern $PATTERN";
           git branch -a | grep $PATTERN
           return
        fi

        BRANCH=$(git branch -a | grep $PATTERN )
        BRANCH=$(echo $BRANCH | sed -E 's/remotes\/origin\///')
        git checkout $BRANCH          || return
        git status
}

function git-catch-up()
{
    git checkout master
    git pull
    git checkout -
    git pull
    git merge master -m "Merging latest changes in master into branch"  || return
    git add --all
    git commit -m "Merging latest changes in master into branch"
    git push
    git status
}


function git-back ()
{
    git checkout origin/master "$1"
    git commit -m \"Revert $1 to the state of master branch\"
    git push
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

function dk-kill-all()
{
    docker kill $(docker ps -q)
}

function dk-remove-all()
{
    docker rmi $(docker images -q)
}

function m423()
{
    for f in *.m4a; do ffmpeg -i "$f" -acodec libmp3lame -ab 64k "${f%}.mp3"; done
    for f in *.m4b; do ffmpeg -i "$f" -acodec libmp3lame -ab 64k "${f%}.mp3"; done
}


function flac2mp3()
{
    find . -name "*.flac" -exec sh -c 'ffmpeg -i "$1" -ar 44100 -ac 2 -b:a 320k "${1%.flac}.mp3"' sh {} \;
}

function remove_quotes()
{
    temp="${1%\"}"
    temp="${temp#\"}"
    RES="${temp%.*}"
    return $RES
}


function duration()
{
    RES=$(ffprobe -show_streams -print_format json "$1"  -v fatal | jq '.streams[0].duration')
    temp="${RES%\"}"
    temp="${temp#\"}"
    RES="${temp%.*}"
    echo "$RES"
    return $RES
}

function duration_all_files()
{
    FILES=$1
    total=0
    for f in $FILES
    do
        res=$(duration "$f")
        total=$(($total+$res))
    done
    echo "$total"
    return $total
}

function remove_track_numbers()
{
    for f in *
    do
        echo "--- processing $f"
        rename 's/^[0-9]+[\s\.\-]+//' "$f"
    done
}


function ya()
{
    youtube-dl --get-duration $1
    youtube-dl --extract-audio  --audio-format mp3 --audio-quality 1 $1
}

function yv()
{
    youtube-dl --get-duration $1
    youtube-dl --recode-video avi $1
}

function nonums()
{
     rename -e 's/^[\d\.\s\-]+//' $1
}


















###########################################################################

function setup_new_box()
{   # Install and configure software on a new Mint box
    sudo apt-get update
    PYTHON_MODS=python python3 python-pip python3-pip
    NETWORK_TOOLS=openssh-server openssh-client curl
    UTILS=mc aptitude ffmpeg lame
    sudo apt-get install --upgrade -y $UTILS $NETWORK_TOOLS  $PYTHON_MODS
    sudo python -m pip install --upgrade pip
    sudo python3 -m pip install --upgrade pip

    install_docker
    no_sudo_docker_for $USER
}


