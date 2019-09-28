import socket
import sys
import getopt
import threading
import os

# global variables
localIP = "localhost"
localPort = -1
bufferSize = 1024
logFileName = ''
overlayPort = -1  # - o the port which will be used by other servers to connect to you via TCP (Optional).
serverOverlayPort = -1  # - t the port number of the same server which you want to connect to via TCP (Optional).
serverOverlayIP = -1  # - s the IP address of the server that you want to connect to (Optional).
msgWelcome = ''
instructions = 'Command Line Options:\n> server –s serveroverlayIP –t serveroverlayport –o overlayport –p portno –l logfile\nWhere\n-s serveroverlayIP: This parameter is the IP address of the server that\nyou want to connect to (Optional).\n-t serveroverlayport: This parameter is the port number of the same\nserver which you want to connect to via TCP (Optional).\n-o overlayport: This parameter is the port which will be used by other\nservers to connect to you via TCP (Optional).\n-p portno: This parameter is the port number over which clients will\nconnect with you via UDP (Mandatory).\n-l logfile: Name of the log file (Mandatory).'
namePApair = []  # name(unique), and the address ,port number pair. Form: pair<string, {#byteVersion of info#}>
connSocket = None


def TCPServerThread():
    conn, addr = TCPServerSocket.accept()
    f.write("server joined overlay from host " + addr[0] + " port " + str(addr[1]) + "\n")
    while 1:
        data = conn.recv(bufferSize)


# populating myopts with paris of option and argument
myopts, args = getopt.getopt(sys.argv[1:], "s:t:o:p:l:")

# setting the directions of the program using the args
###############################
# o == option
# a == argument passed to the o
###############################
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
if overlayPort != -1:
    TCPServerSocket.bind((localIP, int(overlayPort)))
    TCPServerSocket.listen(1)
    TCPServerthread = threading.Thread(target=TCPServerThread)
    f.write("server overlay started at port " + overlayPort + "\n")
    TCPServerthread.start()
    if serverOverlayPort != -1:
        TCPClientSocket.connect((serverOverlayIP, int(serverOverlayPort)))

# if "o" parameter is null, it can't get connected to by TCP

# listen for incoming datagrams
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
                # todo: broadcast this message to all of the connected servers
                for i in namePApair:
                    if cAddress == i[1]:
                        senderName = i[0]

                cString.insert(0, senderName)
                newString = ' '.join(cString)
                bytetoSend = newString.encode()
                # if serverOverlayPort == -1:  # this one is the one connected
                #     connSocket.send(bytetoSend)  # send this string with sender's name at the beginning, byte version
                # else:
                #     TCPClientSocket.sendall(bytetoSend)
                continue

            # getting the sender's name
            for i in namePApair:
                if cAddress == i[1]:
                    senderName = i[0]
            if senderName == '':  # sender's name is not found - usually not a possible situation
                print("this sender is not yet registered (not possible)")
                continue

            # getting the receiver's address
            receiverAddress = []
            for i in namePApair:
                if receiverName == i[0]:
                    receiverAddress = i[1]
            if not receiverAddress:  # sender's name is not found - usually not a possible situation
                print("this receiver has not yet registered on our server.")
                continue

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

    # msg formatting snippet
    # msgRecv = msgAddressPair[0]
    # addressRecv = msgAddressPair[1]
    #
    # # terminal report temp
    # clientMsg = "Message from Client:{}".format(msgRecv)
    # clientIP = "Client IP Address:{}".format(addressRecv)
    # print(clientMsg)
    # print(clientIP)
