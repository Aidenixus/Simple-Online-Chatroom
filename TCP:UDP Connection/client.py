import socket
import sys
import getopt
import threading
import os

# global variables
serverAddressPortPair = ("-1", -1)  # not initialized. Form: address, port
bufferSize = 1024
logFileName = ''
myName = ''
instructions = "Command Line Options:\n> client –s serverIP –p portno –l logfile –n myname\nwhere\n-s <serverIP> indicates the serverIP address\n-p <portno> port number for client to connect to server\n-l <logfile> name of the logfile\n-n <myname> indicates client name"


# if "exit" is typed in, exit the program
def inputPerceive():
    while(1):
        uinput = input()
        if uinput == "exit":
            byteSend = str.encode(uinput)
            UDPClientSocket.sendto(byteSend, serverAddressPortPair)
            print(myName, "exit")
            f.write("terminating client..." + "\n")
            f.close()
            os._exit(1)   # deprecated usage. Use until better methods are found
        setInputString = uinput.split()
        if setInputString[0] == "sendto":
            # send this command to server
            f.write(uinput + "\n")
            byteSend = str.encode(uinput)
            UDPClientSocket.sendto(byteSend, serverAddressPortPair)


# populating myopts with paris of option and argument
myopts, args = getopt.getopt(sys.argv[1:], "s:p:l:n:")

# setting the directions of the program using the args
###############################
# o == option
# a == argument passed to the o
###############################
for o, a in myopts:
    if o == '-l':
        logFileName = a
    elif o == '-p':
        tempAddr = serverAddressPortPair[0]
        serverAddressPortPair = (tempAddr, int(a))
    elif o == '-s':
        tempPort = serverAddressPortPair[1]
        serverAddressPortPair = (a, int(tempPort))
    elif o == '-n':
        myName = a

# checking if the proper settings are up
if serverAddressPortPair[0] == "-1" or serverAddressPortPair[1] == -1 or logFileName == '' or myName == '':
    print(instructions)
    sys.exit()

# opening the log file
f = open(logFileName, "w+")

# initializing socket
UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send register info (automatic)
byteRegister = str.encode("register " + myName)
UDPClientSocket.sendto(byteRegister, serverAddressPortPair)
print(myName, "waiting for messages..")
f.write("connecting to the server " + str(serverAddressPortPair[0]) + " at port " + str(serverAddressPortPair[1]) + "\n")
f.write("sending register message " + myName + "\n")

# start accepting inputs
inputThread = threading.Thread(target=inputPerceive)
inputThread.start()

while 1:
    try:
        msgRecv = UDPClientSocket.recvfrom(bufferSize)  # receiving messsage
        cString = msgRecv[0].decode().split()
        if cString[0] == "welcome":
            print(myName, "connected to server and registered")
            f.write("received " + cString[0] + "\n")

        elif cString[0] == "recvfrom":
            newString = ' '.join(cString)
            print(myName + " " + newString)
            f.write(newString + "\n")

    except KeyboardInterrupt:
        print(myName, "exit")
        f.write("terminating client..." + "\n")
        f.close()
        os._exit(0)  # deprecated usage. Use until better methods are found

    # # receive display snippet
    # msg = "Message from Server {}".format(msgRecv[0])
    # addr = "Address from Server {}".format(msgRecv[1])
    # print(msg)
    # print(addr)
