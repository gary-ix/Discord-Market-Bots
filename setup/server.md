## Setting up a Python Application with Supervisor on Linux

### 1. Have a VPS Provider (I use linode)

### 2. Clone Git Repo

```bash
# I clone mine into Documents
git clone yadi yada
```

### 3. Create Python .venv

```bash
# Create a virtual environment with Python
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install project dependencies from requirements.txt
pip install -r setup/requirements.txt
```

### 4. Set Your Specific Credientals

```bash
# 1. Create .env file and set "WEBHOOK_CHANNEL_ID"

# 2. Create .bots.json file and set bot credentials

Example files are provided to see the correct format
```

### 4. Install Supervisor

```bash
# Install package
sudo apt install supervisor

# Create a Supervisor configuration file for your application
sudo nano /etc/supervisor/conf.d/${botName}.conf
```

### 5. Sample Supervisor .conf

```bash
<<<<<<< HEAD
[program:ticker_bots]
user=bot_manager
directory=/home/bot_manager/code/ticker_bots
command=/home/bot_manager/code/ticker_bots/.venv/bin/python3.8 /home/bot_manager/code/ticker_bots/src/main.py
=======
[program:${botName}]
user=${vpsUsername}
directory=/home/bot_manager/Documents/${botName}
command=/home/bot_manager/Documents/${botName}/.venv/bin/python3.10 /home/bot_manager/Documents/${botName}/src/main.py
>>>>>>> 5820b41b44b46b9e09966e60db104a927e5c731f
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/${botName}/${botName}.err.log
stderr_logfile_maxbytes=50MB
stderr_logfile_backups=10
stdout_logfile=/var/log/${botName}/${botName}.out.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
```

### 6. Create Directories/Output Files for Supervisor

```bash
# Create directories and files for Supervisor output logs
sudo mkdir /var/log/${botName}
sudo touch /var/log/${botName}/${botName}.out.log
sudo touch /var/log/${botName}/${botName}.err.log
```

### 7. Start Bots

```bash
sudo supervisorctl start ${botName}
```

### 8. Check Status

```bash
sudo supervisorctl status all
```
