# Author: Richard Zins
# Date: 2/26/2020
# TicTacToe client implementation

import argparse, socket, logging

logging.basicConfig(level=logging.INFO)

def recvall(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            logging.error("Did not receive all the expected bytes from server.")
            break
        data += more
        decodedData = data.decode("utf-8")
        if ";" in decodedData:
                break
    return data

def process(msg):
    if "start" in msg:
        processedStr = "We will now start the game of TicTacToe. The top left spot on the board is specified by the number 0, increasing from left to right for the other spots on the board. This means the bottom right corner is spot 8. Please note you can make your first move while waiting for the second client, and when a second client joins and makes their first move then you will be prompted to make your second move."
        return 0, processedStr
    elif "sendlocation" in msg:
        return 1, " "
    elif "xo" in msg:
        locationOfFirstBrace = msg.find("{")
        locationOfSecondBrace = msg.find("}")
        processedStr = msg[locationOfFirstBrace + 1 : locationOfSecondBrace]
        processedStr2 = "You are player: " + processedStr
        return 2, processedStr2
    elif "gameover" in msg:
        locationOfFirstBrace = msg.find("{")
        locationOfSecondBrace = msg.find("}")
        processedStr = msg[locationOfFirstBrace + 1 : locationOfSecondBrace]
        if processedStr is 't':
            return 3, "Game over! It was a tie..."
        else :
            return 3, ("Game over! " + processedStr + " won!")
    elif "drawboard" in msg:
        locationOfFirstBrace = msg.find("{")
        locationOfSecondBrace = msg.find("}")
        processedStr = msg[locationOfFirstBrace + 1 : locationOfSecondBrace]
        return 4, processedStr
    elif "error" in msg:
        locationOfFirstBrace = msg.find("{")
        locationOfSecondBrace = msg.find("}")
        processedStr = msg[locationOfFirstBrace + 1 : locationOfSecondBrace]
        processedStr2 = "Error: " + processedStr
        return 5, processedStr2
    else :
        return -1, " "

def client(host, port):
    # connection opening
    # AF_INET is IPV4 and SOCK_STREAM is TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    logging.info("Connect to server: " + host + " on port: " + str(port))

    # recieveing messages
    bol = True
    while bol:
        message = recvall(sock, 100).decode('utf-8')
        # logging.info('Received: ' + message)
        list = message.split("\\")
        # logic for the thread processing what to do based on the protocol sent
        for s in list:
            command , str2 = process(s)
            if command == 0:
                print(str2)
            elif command == 1:
                # prompt user to enter location
                move = input("Enter the # of the spot you wish to make your move: ")
                location = "client\location{" + move + "};"
                sock.sendall(location.encode())
            elif command == 2:
                print(str2)
            elif command == 3:
                print(str2)
                bol = False
            elif command == 4:
                blist = str2.split(" ")
                j = 0
                for i in range(0,9): # for (i = 0; i < 9; i++)
                    # print without a new line
                    print(blist[i], end=' ')
                    j += 1
                    # add a new line every 3 board spaces
                    if j % 3 == 0:
                        print('')
            elif command == 5:
                print(str2)
            else :
                pass

    # close connection
    sock.close()

if __name__ == '__main__':
    port = 9001

    parser = argparse.ArgumentParser(description='Tic Tac Oh No Client (TCP edition)')
    parser.add_argument('host', help='IP address of the server.')
    args = parser.parse_args()

    client(args.host, port)
