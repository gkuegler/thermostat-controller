Install 'Screen'
Screen is a terminal management app?

# Manual Start For Development
1. Give Permission to script to be launched
chmod +x ./launch_via_ssh.sh
2. cd to project directory
3. run './launch_via_ssh.sh'
4. press ctrl-a then ctrl-d to disconnect terminal
Process will run in background.
Safe to disconnect ssh.
# Logging Back In
execute 'screen -r' to reattach from any ssh
use 'screen -ls' to list available screens
e.g.
    615.thermostat

to re-attach 'screen -r thermostat'

# Edit a file with VsCode
VISUAL="code -n -w" sudo -e <filename>

# AutoStart at boot with Linux Service (systemd)
https://wiki.archlinux.org/title/Systemd/User#Basic_setup
https://medium.com/@benmorel/creating-a-linux-service-with-systemd-611b5c8b91d6
https://www.youtube.com/watch?v=9ySgYAb27FA


1. Copy systemd service description file to systemd directory.
sudo cp thermostat.service /etc/systemd/system/thermostat.service
2. Verify service is enabled and works:
sudo systemctl enable thermostat
sudo systemctl status thermostat
sudo systemctl start thermostat

## Diagnose Service Problems
View journal file:
sudo journalctl --unit=thermostat -e
Note: '-e' brings you to the end of the journal file.

Reload the service file after modifying:
sudo systemctl disable thermostat
sudo systemctl daemon-reload
sudo systemctl enable thermostat
sudo systemctl start thermostat
sudo systemctl status thermostat

# Hostname Resolution
The router can use a mix of protocols to determine the hostnames. It can be a mix of DNS, mDNS, reverse DNS (that actually uses DNS), DHCP requests and maybe something else.