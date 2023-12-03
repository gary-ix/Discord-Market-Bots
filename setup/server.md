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
sudo nano /etc/supervisor/conf.d/ticker_bots.conf
```

### 5. Sample Supervisor .conf

```bash
[program:ticker_bots]
user=bot_manager
directory=/home/bot_manager/code/ticker_bots
command=/home/bot_manager/code/ticker_bots/.venv/bin/python3.8 /home/bot_manager/code/ticker_bots/src/main.py
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/ticker_bots/ticker_bots.err.log
stderr_logfile_maxbytes=50MB
stderr_logfile_backups=10
stdout_logfile=/var/log/ticker_bots/ticker_bots.out.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
```

### 6. Create Directories/Output Files for Supervisor

```bash
# Create directories and files for Supervisor output logs
sudo mkdir /var/log/ticker_bots
sudo touch /var/log/ticker_bots/ticker_bots.out.log
sudo touch /var/log/ticker_bots/ticker_bots.err.log
```

### 7. Start Bots

```bash
sudo supervisorctl start ticker_bots
```

### 8. Check Status

```bash
sudo supervisorctl status all
```
