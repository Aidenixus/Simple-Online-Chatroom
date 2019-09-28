import socket
import sys
import getopt
import threading
import os

# global variables
localIP = "localhost"
localPort = -1  # -p, local port number
bufferSize = 1024
logFileName = ''
overlayPort = -1  # - o the port which will be used by other servers to connect to you via TCP (Optional).
serverOverlayPort = -1  # - t the port number of the same server which you want to connect to via TCP (Optional).
serverOverlayIP = -1  # - s the IP address of the server that you want to connect to (Optional).
msgWelcome = ''
instructions = 'Command Line Options:\n> server –s serveroverlayIP –t serveroverlayport –o overlayport –p portno –l ' \
               'logfile\nWhere\n-s serveroverlayIP: This parameter is the IP address of the server that\nyou want to ' \
               'connect to (Optional).\n-t serveroverlayport: This parameter is the port number of the same\nserver ' \
               'which you want to connect to via TCP (Optional).\n-o overlayport: This parameter is the port which ' \
               'will be used by other\nservers to connect to you via TCP (Optional).\n-p portno: This parameter is ' \
               'the port number over which clients will\nconnect with you via UDP (Mandatory).\n-l logfile: Name of ' \
               'the log file (Mandatory). '
namePApair = []  # name(unique), and the address ,port number pair. Form: pair<string, {#byteVersion of info#}>
connSocket = None


def TCPClientThread():
    while 1:
        try:
            # when the server this server connect to as a client send back msg
            data = TCPClientSocket.recv(bufferSize)
            if not data:
                continue
            returnString = data.decode()
            cClientString = returnString.split()
            senderClientName = cClientString[0]
            cClientString.remove(senderClientName)
            receiverClientName = cClientString[1]

            # first check if the client exist in our server
            Clientcheck = False
            for ii in namePApair:
                if receiverClientName == ii[0]:
                    Clientcheck = True
                    break
            if not Clientcheck:
                # forward this message to all those who have connected to this server as a client
                if connSocket is not None:
                    connSocket.send(bytetoSend)
                continue

            # obtaining the receiver's address
            receiverClientAddress = []
            for ii in namePApair:
                if receiverClientName == ii[0]:
                    receiverClientAddress = ii[1]
            cClientString.insert(2, senderClientName)
            cClientString.insert(2, "from")
            f.write(' '.join(cClientString) + "\n")
            cClientString.remove(cClientString[0])
            cClientString.remove(cClientString[0])
            cClientString.remove(cClientString[0])
            cClientString.remove(cClientString[0])  # now the cClientString is a list of the message to send
            newClientString = ' '.join(cClientString)  # making the sentence to send a string
            sendClientString = "recvfrom " + senderClientName + " " + newClientString
            logClientString = "recvfrom " + senderClientName + " to " + receiverClientName + " " + newClientString
            f.write(logClientString + "\n")
            byteClientMsg = str.encode(sendClientString)
            UDPServerSocket.sendto(byteClientMsg, receiverClientAddress)

        except KeyboardInterrupt:
            f.write("terminating server..." + "\n")
            f.close()
            os._exit(1)  # deprecated usage. Use until better methods are found


def TCPServerThread():
    conn, addr = TCPServerSocket.accept()
    global connSocket
    connSocket = conn  # saving the connected server who act as a client into a global variable
    f.write("server joined overlay from host " + addr[0] + " port " + str(addr[1]) + "\n")
    print("server joined overlay from host " + addr[0] + " port " + str(addr[1]))
    while 1:
        try:
            data = conn.recv(bufferSize)  # this should be a byte version string with first word as the sender's name
            if not data:
                continue
            returnString = data.decode()
            cServerString = returnString.split()
            senderServerName = cServerString[0]
            cServerString.remove(senderServerName)
            receiverServerName = cServerString[1]

            # first check if the client exist in our server
            checkServer = False
            for ii in namePApair:
                if receiverServerName == ii[0]:
                    checkServer = True
                    break
            if not checkServer:
                # forward this message to all the servers where this server
                # connect to as a client
                TCPClientSocket.sendall(bytetoSend)
                continue

            # obtaining the receiver's address
            receiverServerAddress = []
            for ii in namePApair:
                if receiverServerName == ii[0]:
                    receiverServerAddress = ii[1]
            cServerString.insert(2, senderServerName)
            cServerString.insert(2, "from")
            f.write(' '.join(cServerString) + "\n")
            cServerString.remove(cServerString[0])
            cServerString.remove(cServerString[0])
            cServerString.remove(cServerString[0])
            cServerString.remove(cServerString[0])  # now the cServerString is a list of the message to send
            newServerString = ' '.join(cServerString)  # making the sentence to send
            sendServerString = "recvfrom " + senderServerName + " " + newServerString
            logServerString = "recvfrom " + senderServerName + " to " + receiverServerName + " " + newServerString
            f.write(logServerString + "\n")
            byteServerMsg = str.encode(sendServerString)
            UDPServerSocket.sendto(byteServerMsg, receiverServerAddress)

        except KeyboardInterrupt:
            f.write("terminating server..." + "\n")
            f.close()
            os._exit(1)  # deprecated usage. Use until better methods are found


# populating myopts with paris of option and argument
myopts, args = getopt.getopt(sys.argv[1:], "s:t:o:p:l:")

# setting the params of the program using the args
##################################
# o == option
# a == argument onto o
##################################

for o, a in myopts:
    if o == '-l':
        logFileName = a
    elif o == '-p':
        localPort = int(a)
    elif o == '-o':
        overlayPort = a
    elif o == '-t':
        serverOverlayPort = a
    elif o == '-s':
        serverOverlayIP = a

# checking if the proper settings are up
if localPort == -1 or logFileName == '':
    print(instructions)
    sys.exit()

# opening the log file
f = open(logFileName, "w+")

# initializing UDP socket
UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# binding ip and port
UDPServerSocket.bind((localIP, localPort))
f.write("server started on " + localIP + " at port " + str(localPort) + "\n")

# initializing TCP socket
# TCP can't connect and bind at the same time
TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# if "o" parameter is null, it can't get connected to by TCP
if overlayPort != -1:
    TCPServerSocket.bind((localIP, int(overlayPort)))
    TCPServerSocket.listen(1)
    TCPServerthread = threading.Thread(target=TCPServerThread)
    f.write("server overlay started at port " + overlayPort + "\n")
    print("server overlay started at port " + overlayPort)
    TCPServerthread.start()
    if serverOverlayPort != -1:
        TCPClientSocket.connect((serverOverlayIP, int(serverOverlayPort)))
        TCPClientthread = threading.Thread(target=TCPClientThread)
        TCPClientthread.start()

# listen for incoming UDP data
while 1:
    try:
        # automatic send welcome msg after receiving registration
        infoAddressPair = UDPServerSocket.recvfrom(bufferSize)  # blocking call
        cString = infoAddressPair[0].decode().split()
        cAddress = infoAddressPair[1]  # still byte version
        if cString[0] == "register":
            cName = cString[1]
            print(cAddress)
            msgWelcome = "welcome " + cName
            byteMsg = str.encode(msgWelcome)
            print(cName, "registered from host", cAddress[0], "port", cAddress[1])
            UDPServerSocket.sendto(byteMsg, cAddress)
            f.write("client connection from host " + str(cAddress[0]) + " port " + str(cAddress[1]) + "\n")
            f.write(
                "received register " + cName + " from host " + str(cAddress[0]) + " port " + str(cAddress[1]) + "\n")
            namePApair.insert(0, [cName, cAddress])  # registered client with its name and address associated

        elif cString[0] == "sendto":
            receiverName = cString[1]
            senderName = ''

            # first check if the client exist in our server
            check = False
            for i in namePApair:
                if receiverName == i[0]:
                    check = True
                    break
            if not check:
                for i in namePApair:
                    if cAddress == i[1]:
                        senderName = i[0]  # usually not possible that it doesnt exist in namePApair

                cString.remove("sendto")
                cString.remove(receiverName)  # newString is now a pure list of strings without sendto and names
                f.write("sendto " + receiverName + " from " + senderName + " " + ' '.join(cString) + "\n")
                f.write(receiverName + " not registered with server" + "\n")
                f.write("sending message to server overlay " + ' '.join(cString) + "\n")
                cString.insert(0, senderName)
                cString.insert(1, "sendto")
                cString.insert(2, receiverName)
                newString = ' '.join(cString)
                bytetoSend = newString.encode()
                if serverOverlayPort == -1:
                    # means this server can only be connected, so we only forward this message to those who
                    # connected to this server
                    if connSocket is not None:
                        connSocket.send(bytetoSend)
                else:
                    # forward this message to all the server that this server connected
                    TCPClientSocket.sendall(bytetoSend)
                    if connSocket is not None:
                        # forward this message to the server that has connected to this server
                        connSocket.send(bytetoSend)
                continue

            # obtaining the sender's name
            for i in namePApair:
                if cAddress == i[1]:
                    senderName = i[0]

            # obtaining the receiver's address
            receiverAddress = []
            for i in namePApair:
                if receiverName == i[0]:
                    receiverAddress = i[1]  # this for loop is guaranteed to be successful of its search

            cString.insert(2, senderName)
            cString.insert(2, "from")
            f.write(' '.join(cString) + "\n")
            cString.remove(cString[0])
            cString.remove(cString[0])
            cString.remove(cString[0])
            cString.remove(cString[0])  # now the cString is the set of the message to send
            newString = ' '.join(cString)  # making the sentence to send
            sendString = "recvfrom " + senderName + " " + newString
            logString = "recvfrom " + senderName + " to " + receiverName + " " + newString
            f.write(logString + "\n")
            byteMsg = str.encode(sendString)
            UDPServerSocket.sendto(byteMsg, receiverAddress)

        elif cString[0] == "exit":
            for i in namePApair:
                if cAddress == i[1]:
                    namePApair.remove(i)
                    break

    except KeyboardInterrupt:
        f.write("terminating server..." + "\n")
        f.close()
        os._exit(1)  # deprecated usage. Use until better methods are found