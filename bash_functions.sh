# Integration:
# 1. git clone https://github.com/DmitryObukhov/shrec.git
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
# source /opt/shrec/bash_functions.sh

PATH=$PATH:~/shrec:~/shrec/utility_scripts

source ~/shrec/bash_functions/git.sh
source ~/shrec/bash_functions/docker.sh
source ~/shrec/bash_functions/apt.sh
source ~/shrec/bash_functions/shrec.sh
source ~/shrec/bash_functions/multimedia.sh

# cat user.json | grep default_repo | awk '{print $2}' | tr -d '"'
