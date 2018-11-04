# -*- coding: utf-8 -*-
from Tkinter import *
from tkMessageBox import askokcancel,showinfo,showwarning
from staticmap import StaticMap, CircleMarker
import tkSimpleDialog
import paho.mqtt.client as mqtt # importation d un client mqtt
import time

broker=""
port = 1883

#dimention de la carte
largeur = 640
hauteur = 480
zoom = 15

# les fonctions callback
def on_log(client, userdata, level, buf):
	print "log: "+buf

def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print "connexion OK"
		showinfo("Connexion","Connexion OK")
	else:
		print "Bad connexion code de retour", rc
		showwarning("Erreur","bad connexion")

def on_disconnect(client, userdata, flags, rc=0):
	print "code de resultat de deconnexion ", str(rc)

def on_message(client,userdata,msg):
	global coord
	topic=msg.topic
	m_decode=str(msg.payload.decode("utf-8"))
	print "message recu ", m_decode
	coord = m_decode.split(",")
	
	Latitude.configure(text=coord[0])
	Longitude.configure(text=coord[1])
	Altitude.configure(text=coord[3])
	Speed.configure(text=coord[2])

	show_image()

def getmap(latitude, longitude, largeur, hauteur, zoom):
	m = StaticMap(largeur,hauteur, url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')

	marker_outline = CircleMarker((longitude,latitude), 'white', 18)
	marker = CircleMarker((longitude,latitude), '#0036FF', 12)

	m.add_marker(marker_outline)
	m.add_marker(marker)

	image = m.render(zoom)
	image.save('marker.png')

def get_image():
	getmap(float(coord[0]), float(coord[1]), largeur, hauteur, zoom)	
	image = PhotoImage(file='marker.png')
	return image

def deconnect():
	client.loop_stop()
	client.disconnect()	#deconnect

def arret():
	ans = askokcancel('Verify exit', "Really quit?")
	if ans: 
		client.loop_stop()
		client.disconnect()	#deconnect
		fenetre.quit()
	
def show_image():
	global image,trash,poubelle
	image=get_image()
	canvas.create_image(0,0,image=image,anchor=NW)
 	
def get_connexion():
	def connexion():
		broker=ip_server.get()
		print "connexion au broker ",broker

		client.connect(broker) # connection au broker
		client.loop_start()

		#abonnement au broker 
		client.subscribe("Tracker/coord")
		
		conwin.destroy()

	conwin = Toplevel(fenetre)
	conwin.grab_set()

	ip_server = StringVar()
	var_port = IntVar()
		
	txt1 = Label(conwin, text ='Adresse du Server')
	txt2 = Label(conwin, text ='Port')
	entr1 = Entry(conwin,textvariable=ip_server)
	entr2 = Entry(conwin,textvariable=var_port)
	txt1.grid(row =0)
	txt2.grid(row =1)
	entr1.grid(row =0, column=1)
	entr2.grid(row =1, column=1)

	button_con = Button(conwin, text="Connexion",command=connexion)
   	button_con.grid(row=2, column=1)

def donothing():
   filewin = Toplevel(fenetre)
   button = Button(filewin, text="Do nothing button",command=filewin.destroy)
   button.pack()

client = mqtt.Client("moh_1")

#lien et utilisation des fonction callback
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_log = on_log
client.on_message=on_message

# GUI
fenetre = Tk()
fenetre.resizable(width=False, height=False)
fenetre['bg']='white'
fenetre.title("OHA Tracker v 0.01")

menubar = Menu(fenetre)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Connexion", command=get_connexion)
filemenu.add_command(label="Carte", command=show_image)

filemenu.add_separator()

filemenu.add_command(label="Deconnexion", command=deconnect)
filemenu.add_command(label="Exit", command=arret)
menubar.add_cascade(label="File", menu=filemenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help", command=donothing)
helpmenu.add_command(label="About...", command=donothing)
menubar.add_cascade(label="Help", menu=helpmenu)

fenetre.config(menu=menubar)


# frame 1
Frame1 = Frame(fenetre, borderwidth=2, relief=GROOVE,bg='white')
Frame1.pack(side=LEFT, padx=5, pady=5)

# frame 2
Frame2 = Frame(fenetre, bg="white", borderwidth=2, relief=GROOVE)
Frame2.pack(side=TOP, padx=5, pady=5)

longFram = LabelFrame(Frame2,bg="white", text="Longitude ", padx=5,pady=5)
longFram.pack(padx=10, pady=10)

latFram = LabelFrame(Frame2,bg="white", text="Latitude ", padx=5,pady=5)
latFram.pack(padx=10, pady=10)

Longitude = Label(longFram,bg="white", text="00000000")
Longitude.pack()

Latitude = Label(latFram,bg="white", text="00000000")
Latitude.pack()

altFram = LabelFrame(Frame2,bg="white", text="Altitude ", padx=5,pady=5)
altFram.pack(padx=10, pady=10)

Altitude = Label(altFram,bg="white", text="00000000")
Altitude.pack()

speedFram = LabelFrame(Frame2,bg="white", text="Vitesse ", padx=5,pady=5)
speedFram.pack(padx=10, pady=10)

Speed = Label(speedFram,bg="white", text="00000000")
Speed.pack()

image_logo= PhotoImage(file="OHA")

canvas = Canvas(Frame1, width=largeur, height=hauteur,background='white')
canvas.pack(padx=10, pady=10)
carte=canvas.create_image(320,240,image=image_logo,anchor=CENTER)


fenetre.mainloop()
