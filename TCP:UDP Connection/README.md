Use the default IP address 127.0.0.1 [localhost]
Compiling instructions: 
	Please open different terminals, and one terminal can only serve one role and one end(either a client, or a server)
	say, if there are 2 servers and 2 clients, open 4 distinct terminals for diferent command.


########################################################################################


Command Line Options:

Server:

> server –s serveroverlayIP –t serveroverlayport –o overlayport –p portno –l
logfile
Where
-s serveroverlayIP: This parameter is the IP address of the server that
you want to connect to (Optional).
-t serveroverlayport: This parameter is the port number of the same
server which you want to connect to via TCP (Optional).
-o overlayport: This parameter is the port which will be used by other
servers to connect to you via TCP (Optional).
-p portno: This parameter is the port number over which clients will
connect with you via UDP (Mandatory).
-l logfile: Name of the log file (Mandatory).
All the arguments are not mandatory for a server to spawn. For example, if the first
server is being spawned, it will not have a –s and –t options since it does not want
to connect to anyone (No other servers exist as of now).
However, from second server onward, -s and –t will be necessary in order to
create the connections. The mandatory arguments are -p, and –l
Servers can spawn without an -o argument but will not be able to be connected to
via TCP. They will, however, still be able to handle clients via UDP.


Client

> client –s serverIP –p portno –l logfile –n myname
where
-s <serverIP> indicates the serverIP address
-p <portno> port number for client to connect to server
-l <logfile> name of the logfile
-n <myname> indicates client name


examples:
python3 server.py -p 7584 -o 2500 -l LogServer1.txt
python3 server.py -s localhost -t 2500 -p 9000 -o 2501 -l LogServer2.txt
python3 client.py -s localhost -p 7584 -l LogClient1.txt -n John
python3 client.py -s localhost -p 9000 -l LogClient2.txt -n Mary

########################################################################################

Client also takes user inputs for "sendto ...." and "exit"

Using the client that has the name John:
-> sendto Mary Hi. How are you?

Using the client that has the name Mary:
-> sendto John I am good. Thank you.

-> exit


