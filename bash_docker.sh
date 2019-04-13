# Docker-related functions

function dk-kill-all()
{
    docker kill $(docker ps -q)
}

function dk-remove-all()
{
    docker rmi $(docker images -q)
}

