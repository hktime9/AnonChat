from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO
from random import *
import datetime
import time
import os

################################### UTILITY FUNCTIONS ###################################	
def giveList(filename):
	with open(filename, 'r') as myfile:
		data=myfile.read()
	data= data.split('\n')
	return data

def initAvailableSlots(pool):
	retList= []
	for i in range(0, len(pool)):
		retList.append(i)
	return retList

def getTime():
	time= datetime.datetime.now()
	timestr= str(time)
	timestr= timestr.split(" ")
	time= timestr[1]
	time= time.split(":")
	flag= ""
	if(int(time[0])>12):
		flag= "PM"
	else:
		flag= "AM"

	if(flag=="PM"):
		hour= int(time[0])
		hour= hour-12
		time[0]= str(hour)

	time= time[0]+":"+time[1]+flag
	return time

def makeUniCode(string):
	retstr= ""
	for i in range(0, len(string)):
		test= ('U+%04x' % ord(string[i]))
		test= test.replace("U","\\")
		test= test.replace("+", "u")
		retstr= retstr+test
	return retstr

def printUsers(action):
	print("*")
	print("*")
	print("*")
	print("Action: "+action)
	print("Online Users: {}".format(activeUsers))
	print(users)
	print("*")
	print("*")
	print("*")

######################################## GLOBALS ########################################
anonIdentity= giveList('nicknamesList.txt')
availableSlots= initAvailableSlots(anonIdentity)
users= {'ip': ['nickname','index']}
activeUsers= 0
app= Flask(__name__)
app.config['SECRET_KEY']= 'vnkdjnfjknfl1232#'
socketio= SocketIO(app)

#################################### FLASK APP ROUTES ####################################
@app.route('/')
def sessions():
	return render_template('session.html')

#################################### SOCKETS HANDLERS ####################################
@socketio.on('my event')
def handlEevent(json, methods=['GET', 'POST']):
	identity= str(request.remote_addr)
	anon= users[identity][0]
	sendThis= ""
	
	if(len(str(json))>350):
		sendThis= "*The input is too large to handle, I'm afraid*"
	else:
		anonCode= makeUniCode(anon)
		colonCode= makeUniCode(": ")
		spaceBrack= makeUniCode(" [")
		timeCode= makeUniCode(getTime())
		brackEnd= makeUniCode("]")
		sendThis= anonCode+colonCode+str(json)+spaceBrack+timeCode+brackEnd
	
	socketio.emit('my response', sendThis)
	printUsers("Message by "+anon+" at "+getTime())

@socketio.on('handshake')
def handshake(json, methods=['GET', 'POST']):
	global activeUsers
	identity= str(request.remote_addr)
	anon= ""
	if identity not in users:
		randomIndex= randint(0, (len(availableSlots)-1))
		anon= anonIdentity[randomIndex]
		users.update({identity:[anon, randomIndex]})
		availableSlots.remove(randomIndex)
	else:
		anon= users[identity][0]

	message= anon+" just joined!  😊"
	socketio.emit('my response', message)
	socketio.emit('sid', request.sid)
	activeUsers= activeUsers+1
	printUsers("New Connection by "+anon+" at "+getTime())
	
@socketio.on('disconnect')
def test_disconnect():
	global activeUsers
	identity= str(request.remote_addr)

	if identity in users:
		anon= users[identity][0]
		index= users[identity][1]
		del users[identity]
		availableSlots.append(index)
		message= anon+" just left! ☹️"
		print(users)
		socketio.emit('my response', message)
		activeUsers= activeUsers-1
		printUsers("Disconnection by "+anon+"["+identity+"] at "+getTime())
		sendString= str(activeUsers)
		socketio.emit("usersResponse", sendString)

@socketio.on('users')
def getUsers(json, methods=['GET', 'POST']):
	global activeUsers
	sendString= str(len(users)-1)
	socketio.emit("usersResponse", sendString)

########################################## MAIN ##########################################
os.system("CLS")
socketio.run(app, debug=True, host='0.0.0.0', port=80)