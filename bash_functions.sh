# Integration:
# 1. git clone https://github.com/DmitryObukhov/shrec.git ~/shrec
# 2. add to ~/.bashrc the code below
#
# MY_EMAIL=xxx
# MY_ID=xxx
# DOMAIN_PASSWORD=xxxxxxx
# USER_PASSWORD=xxxxxx
# ROOT_PASSWORD=xxxxxx
# DEFREPO=xxx
# BITBUCKET_USER=xxx
# BITBUCKET_PASSWORD=xxx
# source ~/shrec/bash_functions.sh

PATH=$PATH:~/shrec

source ~/shrec/bash_git.sh
source ~/shrec/bash_docker.sh
source ~/shrec/bash_apt.sh
source ~/shrec/bash_shrec.sh

# cat user.json | grep default_repo | awk '{print $2}' | tr -d '"'

function submerge()
{
    BASE=CSSSYSVAL-21065
    PARTNUM=MERGE_$1
    figlet $PARTNUM
    git clone $DEFREPO $PARTNUM
    cd $PARTNUM
    BRANCH=feature/$BASE-$PARTNUM
    git checkout -b $BRANCH
    git push --set-upstream origin $BRANCH
}


function m423()
{
    for f in *.m4a; do ffmpeg -i "$f" -acodec libmp3lame -ab 64k "${f%}.mp3"; done
    for f in *.m4b; do ffmpeg -i "$f" -acodec libmp3lame -ab 64k "${f%}.mp3"; done
}


