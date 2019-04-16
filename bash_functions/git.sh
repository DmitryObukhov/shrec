# Git functions

function git-acp ()
{
    git add --all
    git commit -m \""$@"\"
    git push
}


function git-new ()
{
        PATTERN=$1
        if [ -f repo ]; then
            REPO=$(cat repo)
        else
            REPO=$DEFREPO
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



function git-mm ()
{
    git checkout master     || return
    git pull                || return
    git checkout -          || return
    git pull
    git merge master -m \"$1\" || return
    #git push
}
