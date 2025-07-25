import serial
import paho.mqtt.client as mqtt
import time
import datetime

# SERIAL PORT CONFIGURATION  #
serialPort = serial.Serial(port = "/dev/ttyUSB0", baudrate=19200, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE)

# VARIABLE DECLARATION #
serialString = ""
regValue = ""
messageLastSent = time.time()
messageSendInterval = 15
flag_connected = 0
MQTT_SERVER = "SERVER"

heatPumpValues = {
	"radiatorForward": "",
	"heatCarrReturn": "",
	"heatCarrForward": "",
	"compressor": 0,
	"alarm": "",
	"heatGas": "",
	"condenser": "",
	"hotwaterTop": "",
	"compressorSpeed": 0,
	"outdoorTemp": 0,
	"indoorTemp": 0,
	"evaporator": "",
	"airIntake": "",
	"fan": 0,
	"switchValve1": 1,
	"switchValve2": 1,
	"pumpColdCircuit": 1,
	"pumpHeatCircuit": 1,
	"pumpRadiator": 1,
}

# FUNCTIONS #
# Calculate hex values to dec values, izi pizi
def hexToDec(hexValue):
	return int(hexValue,16)

# Calculate received registry value. Rego 800 is a bit wacko 
# and will return a value, sometimes in decimal, sometimes with +65538 added to it.
# If the value is above 65000, we subtract 65538 and get the correct value after 
# dividing it by 10.
def calcRegValue(regValueHex):
	if (hexToDec(regValueHex)) > 65000:
		subValue = 65536
	else:
		subValue = 0
	
	return ((hexToDec(regValueHex)-subValue)/10)

def on_connect(client, userdata, flags, rc):
	global flag_connected
	flag_connected = 1

def on_disconnect(client,userdata, rc):
	global flag_connected
	flag_connected = 0

# MQTT SETUP #
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.connect(MQTT_SERVER,1883,60)
client.loop_start()
# MQTT - Set Last Will
print("MQTT - Setting Last Will")
client.will_set("homemate/heatMon","heatMon LWM - Offline")

print("Sending initial command XS...")
serialPort.flushInput()
serialPort.flush()
serialPort.write(b"XS\r")
time.sleep(0.1)
	
print("Starting...")

while(1):
	if(serialPort.in_waiting > 0):

		if not serialString is None:
			serialString = serialPort.readline()
			serialOutput = serialString.decode('utf-8').rstrip("\n\r")
			serialOutput = serialOutput.strip()

			# If we receive more than 2 characters, continue and make regId the first char 2-4 and
			# regValueHex char 6-12
      # Char 0-1 consists only of XR which is a description of which registry the value comes from.
      #
      
			if not serialString is None and len(serialString) > 2:
				regId = serialOutput[2:6]
				regValueHex = serialOutput[6:12]


				if regId == "0001":
					print("Radiator fram: " + str(calcRegValue(regValueHex)))
					heatPumpValues["radiatorForward"] = str(calcRegValue(regValueHex))

				elif regId == "0003":
					print("Varmebarare retur: " + str(calcRegValue(regValueHex)))
					heatPumpValues["heatCarrReturn"] = str(calcRegValue(regValueHex))

				elif regId == "0004":
					print("Varmebarare fram: " + str(calcRegValue(regValueHex)))
					heatPumpValues["heatCarrForward"] = str(calcRegValue(regValueHex))

				elif regId == "1A01":
					regValueDec = (hexToDec(regValueHex))
					print("Kompressor 0/1: " + str(regValueDec))
					heatPumpValues["compressor"] = str(regValueDec)

				elif regId == "1A20":
					regValueDec = (hexToDec(regValueHex))
					print("Alarm 0/1: " + str(regValueDec))
					heatPumpValues["alarm"] = str(regValueDec)

				elif regId == "000B":
					print("Heat gas: " + str(calcRegValue(regValueHex)))
					heatPumpValues["heatGas"] = str(calcRegValue(regValueHex))

				elif regId == "0006":
					print("Kondensor: " + str(calcRegValue(regValueHex)))
					heatPumpValues["condenser"] = str(calcRegValue(regValueHex))

				elif regId == "0009":
					print("Varmvatten Topp: " + str(calcRegValue(regValueHex)))
					heatPumpValues["hotwaterTop"] = str(calcRegValue(regValueHex))

				elif regId == "2108":
					regValueDec = (hexToDec(regValueHex))*100
					print("Hastighet Kompressor: " + str(regValueDec))
					heatPumpValues["compressorSpeed"] = str(regValueDec)

				elif regId == "0007":
					print("Temperatur Ute: " + str(calcRegValue(regValueHex)))
					heatPumpValues["outdoorTemp"] = str(calcRegValue(regValueHex))

				elif regId == "0008":
					print("Temperatur Inne: " + str(calcRegValue(regValueHex)))
					heatPumpValues["indoorTemp"] = str(calcRegValue(regValueHex))

				elif regId == "0005":
					print("Förångare: " + str(calcRegValue(regValueHex)))
					heatPumpValues["evaporator"] = str(calcRegValue(regValueHex))

				elif regId == "000E":
					print("Luftintag: " + str((calcRegValue(regValueHex))))
					heatPumpValues["airIntake"] = str(calcRegValue(regValueHex))

				elif regId == "1A09":
					regValueDec = (hexToDec(regValueHex))
					print("Fläkt: " + str(regValueDec))
					heatPumpValues["fan"] = str(regValueDec)

				elif regId == "1A07":
					regValueDec = (hexToDec(regValueHex))
					print("Växelventil 1: " + str(regValueDec))
					heatPumpValues["switchValve1"] = str(regValueDec)

				elif regId == "1A08":
					regValueDec = (hexToDec(regValueHex))
					print("Växelventil 2: " + str(regValueDec))
					heatPumpValues["switchValve2"] = str(regValueDec)
					
				elif regId == "1A04":
					regValueDec = (hexToDec(regValueHex))
					print("Pump kallkrets: " + str(regValueDec))
					heatPumpValues["pumpColdCircuit"]= str(regValueDec)
					
				elif regId == "1A05":
					regValueDec = (hexToDec(regValueHex))
					print("Pump varmkrets: " + str(regValueDec))
					heatPumpValues["pumpHeatCircuit"] = str(regValueDec)
					
				elif regId == "1A06":
					regValueDec = (hexToDec(regValueHex))
					print("Pump Radiatorkrets: " + str(regValueDec))
					heatPumpValues["pumpRadiator"] = str(regValueDec)

			else:
				print("Tom rad: " + serialOutput)
				print(". " + serialOutput + " - " + serialOutput[2:6] + " - " + serialOutput[6:12])

	if flag_connected == 1 and time.time() - messageLastSent > messageSendInterval:
		print(datetime.datetime.fromtimestamp(time.time()), ", Skickar uppdatering")
		client.publish('homemate/heatMon/radiator_forward', str(heatPumpValues["radiatorForward"]))
		client.publish('homemate/heatMon/heat_carr_return', str(heatPumpValues["heatCarrReturn"]))
		client.publish('homemate/heatMon/heat_carr_Forward', str(heatPumpValues["heatCarrForward"]))
		client.publish('homemate/heatMon/compressor', str(heatPumpValues["compressor"]))
		client.publish('homemate/heatMon/alarm', str(heatPumpValues["alarm"]))
		client.publish('homemate/heatMon/heatgas', str(heatPumpValues["heatGas"]))
		client.publish('homemate/heatMon/condenser', str(heatPumpValues["condenser"]))
		client.publish('homemate/heatMon/hotwater-top', str(heatPumpValues["hotwaterTop"]))
		client.publish('homemate/heatMon/compressor-speed', str(heatPumpValues["compressorSpeed"]))
		client.publish('homemate/heatMon/outdoor-temp', str(heatPumpValues["outdoorTemp"]))
		client.publish('homemate/heatMon/indoor-temp', str(heatPumpValues["indoorTemp"]))
		client.publish('homemate/heatMon/evaporator', str(heatPumpValues["evaporator"]))
		client.publish('homemate/heatMon/air-intake', str(heatPumpValues["airIntake"]))
		client.publish('homemate/heatMon/fan', str(heatPumpValues["fan"]))
		client.publish('homemate/heatMon/switch-valve-1', str(heatPumpValues["switchValve1"]))
		client.publish('homemate/heatMon/switch-valve-2', str(heatPumpValues["switchValve2"]))
		client.publish('homemate/heatMon/pump-cold-circuit', str(heatPumpValues["pumpColdCircuit"]))
		client.publish('homemate/heatMon/pump-heat-circuit', str(heatPumpValues["pumpHeatCircuit"]))
		client.publish('homemate/heatMon/pump-radiator', str(heatPumpValues["pumpRadiator"]))

		messageLastSent = time.time()
	elif flag_connected == 0:
		while flag_connected == 0:
			try:
				print("MQTT Client: Connection offline - reconnecting...")
				client.connect("10.10.0.203",1883,60)
				client.loop_start()
				print("MQTT Client: Successfully reconnected.")
				flag_connected = 1
			except ConnectionRefusedError as error:
				print("MQTT Client: Connection refused, trying again in 10 seconds.")
				time.sleep(10)
			except:
				print("MQTT Client: Unknown error handeled, trying again in 10 seconds.")
				time.sleep(10)

client.disconnect()
client.loop_stop()
