# Integration:
# 1. git clone https://github.com/DmitryObukhov/shrec.git ~/shrec
# 2. add to ~/.bashrc the code below
#
# MY_EMAIL=xxx
# MY_ID=xxx
# DOMAIN_PASSWORD=xxx
# DEFREPO=xxx
# BITBUCKET_USER=xxx
# BITBUCKET_PASSWORD=xxx
# source ~/shrec/bash_functions.sh

PATH=$PATH:~/shrec


function reloadbash()
{
    source ~/.bashrc
}


function new-shrec()
{
    new_shrec_name=~/shrec/$1
    cp ~/shrec/base_script.py $new_shrec_name
    chmod 777 $new_shrec_name
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
        COUNT=$(git ls-remote $DEFREPO | grep $PATTERN  | wc -l)

        if [ "$COUNT" -lt "1" ]; then
           echo "Cannot find pattern $PATTERN in the list of branches";
           exit;
        fi


        if [ "$COUNT" -gt "1" ]; then
           echo "Too many branches match pattern $PATTERN";
           git ls-remote $DEFREPO | grep $PATTERN
           exit;
        fi

        BRANCH=$(git ls-remote $DEFREPO | grep $PATTERN  | awk '{print $2}')
        BRANCH=${BRANCH#"refs/heads/"}

        mkdir $PATTERN                || exit
        git clone $DEFREPO $PATTERN   || exit
        cd $PATTERN                   || exit
        git checkout $BRANCH          || exit
        git log -n 1
        git status
}

function g-co ()
{
        PATTERN=$1
        COUNT=$(git branch -a | grep $PATTERN  | wc -l)

        if [ "$COUNT" -lt "1" ]; then
           echo "Cannot find pattern $PATTERN in the list of branches";
           exit;
        fi


        if [ "$COUNT" -gt "1" ]; then
           echo "Too many branches match pattern $PATTERN";
           git branch -a | grep $PATTERN
           exit;
        fi

        BRANCH=$(git branch -a | grep $PATTERN )
        BRANCH=$(echo $BRANCH | sed -E 's/remotes\/origin\///')
        git checkout $BRANCH          || exit
        git status
}



function git-back ()
{
    git checkout origin/master "$1"
    git commit -m \"Revert $1 to the state of master branch\"
    git push
}



function git-mm ()
{
    BRANCH=$(git status | grep 'On branch' | awk '{print $3}')
    echo $BRANCH
    if [ "$BRANCH" -eq "master" ]; then
        git pull;
        exit;
    fi
    git checkout master     || exit
    git pull                || exit
    git checkout $BRANCH    || exit
    git pull
    git merge master -m \"$1\"
    git push
}


function agi ()
{
    apt-get install -y -m $@
}


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


function dk-kill-all()
{
    docker kill $(docker ps -q)
}

function dk-remove-all()
{
    docker rmi $(docker images -q)
}
