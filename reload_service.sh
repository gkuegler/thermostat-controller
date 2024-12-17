sudo systemctl stop thermostat
sudo systemctl disable thermostat
sudo cp thermostat.service /etc/systemd/system/thermostat.service
sudo systemctl daemon-reload
sudo systemctl enable thermostat
sudo systemctl start thermostat
sudo systemctl status thermostat