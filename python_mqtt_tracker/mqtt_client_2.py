import paho.mqtt.client as mqtt # importation d un client mqtt
import time
import csv

#broker="broker.hivemq.com"
broker="127.0.0.1"

# les fonctions callback
def on_log(client, userdata, level, buf):
	print "log: "+buf

def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print "connexion OK"
	else:
		print "Bad connexion code de retour", rc

def on_disconnect(client, userdata, flags, rc=0):
	print "code de resultat de deconnexion ", str(rc)

def on_message(client,userdata,msg):
	topic=msg.topic
	m_decode=str(msg.payload.decode("utf-8"))
	#print "message recu ", m_decode
	#client.publish("Tracker/coord",coord)

client = mqtt.Client("moh_2")

#lien et utilisation des fonction callback
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_log = on_log
client.on_message=on_message

print "connexion au broker ",broker

client.connect(broker) # connection au broker

client.loop_start()

with open('DATA_GPS.csv', 'rb') as csvfile:
	csvFile = csv.reader(csvfile)
                
	for row in csvFile :

		coord = ','.join(row)
		client.publish("Tracker/coord",coord)
		time.sleep(20)
 
client.disconnect()
client.loop_stop()
