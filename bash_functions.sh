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

source ~/shrec/bash_functions/git.sh
source ~/shrec/bash_functions/docker.sh
source ~/shrec/bash_functions/apt.sh
source ~/shrec/bash_functions/shrec.sh
source ~/shrec/bash_functions/multimedia.sh

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

