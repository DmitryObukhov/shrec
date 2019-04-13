# SHREC functions

function shrec-create()
{
    cd ~
    git clone https://github.com/DmitryObukhov/shrec.git
    cd ~/shrec
}

function shrec-reload()
{
    cd ~/shrec
    git pull
    cd -
    source ~/.bashrc
}

function shrec-new-py()
{
    new_shrec_name=~/shrec/$1
    cp ~/shrec/base_script.py $new_shrec_name
    chmod 777 $new_shrec_name
}

