#!/bin/bash
# 1. Setup Python requirements
pip install django mysqlclient django-storages boto3 django-environ

# 2. Setup SSH for AWS (using GitHub Secrets)
mkdir -p ~/.ssh
if [ -n "$AWS_SSH_KEY" ]; then
    echo "$AWS_SSH_KEY" > ~/.ssh/mission_control.pem
    chmod 400 ~/.ssh/mission_control.pem
fi

# 3. Create a shortcut to start the MySQL tunnel
echo "alias tunnel='ssh -L 3306:127.0.0.1:3306 -N -f -i ~/.ssh/mission_control.pem ubuntu@$AWS_INSTANCE_IP'" >> ~/.bashrc
