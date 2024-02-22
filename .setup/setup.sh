#!/bin/bash

# Check for root/sudo privileges
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root."
   exit 1
fi

# Set variables
botName="discord-bot-tickers"
vpsUsername=$SUDO_USER
repoPath=$(pwd)

echo - e "\n\nInstalling/Configuring Supervisor\n\n"
sudo apt install supervisor
sudo tee /etc/supervisor/conf.d/${botName}.conf <<EOF
[program:${botName}]
user=${vpsUsername}
directory=$repoPath
command=$repoPath/.venv/bin/python3 $repoPath/src/discord/bot_controller.py
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=${repoPath}/logs/.sys/sys.err.log
stderr_logfile_maxbytes=50MB
stderr_logfile_backups=0
stdout_logfile=${repoPath}/logs/.sys/sys.out.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=0
EOF

sudo mkdir -p ${repoPath}/logs/.sys/

echo -e "\n\nServer setup complete. Be sure to setup your .env file for BOT_TOKEN, etc."
