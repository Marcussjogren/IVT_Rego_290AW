# IVT_Rego_290AW
This is the code I use to monitor my heatpump and publish its values via MQTT. In my case, I have Home Assistant which is listening to the MQTT topic and receiving the data.

<h2>Hardware:</h2>
I have connected a H1-interface from Husdata (www.husdata.se) to a Raspberry Pi Zero Wireless, which runs the code.

<h2>Setup:</h2>
Clone the repo and create a .env-file in the repository folder which contains the below.

<i>I'm not really sure about the discovery-part of mqtt right now, I'm just testing it out.</i>

<h3>Environment file</h3>
MQTT_SERVER = "YOUR SERVER"

MQTT_TOPIC = "MQTT TOPIC"

MQTT_DISCOVERY_TOPIC = "DISCOVERY TOPIC"


<h3>Requirements</h3>
Install the requirements by running "pip3.12 install -r requirements.txt"

<h2>Service</h2>
The service is installed as /lib/systemd/system/heatMon.service and requires "screen" to be installed. In this way, I can always attach to my service and monitor what it does.
I connect to the service with "screen -r heatMon"

[Unit]

Description=HomeMate heatMon

After=multi-user.target


[Service]

Type=forking

User=pi

ExecStart=/usr/bin/screen -dmS heatMon /user/bin/python3 /home/pi/Python/heatMon/heatMon.py


[Install]

WantedBy=multi-user.target
