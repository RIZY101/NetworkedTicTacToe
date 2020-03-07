# Author: Richard Zins
# Date: 2/26/2020
# TicTacToe server implementation

import argparse, socket, logging, threading 
from TicTacToe import TicTacToeEngine

# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)

class ClientThread(threading.Thread):

    def __init__(self, address, socket, ttt, player, turn):
        threading.Thread.__init__(self)
        self.csock = socket
        logging.info('New connection added.')
        self.socket = socket
        self.sockname = address
        self.ttt = ttt
        self.player = player
        self.turn = turn
    


    def run(self):
        # prompt client that game is starting
        prompt = r"server\start{}\xo{" + self.player + "};"
        logging.info("Sent this message to client: " + prompt)
        self.csock.sendall(prompt.encode())

        # game phase: turn by turn, as long as game isn't over.
        while self.ttt.is_game_over() is '-':
            # with our condtional lock
            with self.turn:
                # as long as it isn't our turn...
                while self.ttt.whos_turn() != self.player:
                    self.turn.wait() # wait
                
                gameover = self.ttt.is_game_over()
                if not gameover is '-':
                    gameovertxt = "server\gameover{" + gameover + "};"
                    self.csock.sendall(gameovertxt.encode())
                    # disconnect client
                    self.csock.close()
                    logging.info('Disconnect client.')
                    self.ttt.restart()
                    exit()
                
                # display board before the client is told to make their turn
                # also prompt the user to send location to play
                blist = self.ttt.get_board()
                bstr = ""
                for element in blist:
                    bstr += (element + " ")

                bstrtosend = "server\drawboard{" + bstr + "}\sendlocation{};"
                logging.info("Sent this message to client: " + bstrtosend)
                self.csock.sendall(bstrtosend.encode())
            
                #receive user response
                message = self.recvall(100)
                msg = message.decode('utf-8')
                logging.info('Recieved a message from client: ' + msg)
                list = msg.split('\\')

                # logic for the thread processing what to do based on the protocol sent
                for s in list:
                    command , str = self.process(s)
                    if command == 0:
                        # the msg command was never implemented by the client so if you get this log your in trouble
                        logging.info(str)
                    elif command == 1:
                        # I didnt have time to implement my queue system but I left this here to show that my server could atleast process all my protocol commands
                        logging.info(str)
                    elif command == 2:
                        move = int(str)
                        if self.ttt.is_move_valid(move) is False:
                            logging.info("Sent this message to client: server\error{Not a valid move!};")
                            self.csock.sendall(b'server\error{Not a valid move!};')
                        else:
                            self.ttt.make_move(move)
                    else :
                        pass

                # Display the updated board from the single instance
                self.ttt.display_board()

                # notify the other thread it may be their turn now
                self.turn.notify()

                gameover = self.ttt.is_game_over()
                if not gameover is '-':
                    gameovertxt = "server\gameover{" + gameover + "};"
                    self.csock.sendall(gameovertxt.encode())
                    # disconnect client
                    self.csock.close()
                    logging.info('Disconnect client.')
                    exit()

    # method for processing my protocol
    def process(self, msg):
        if "msg" in msg:
            locationOfmsg = msg.find("msg")
            newStr = msg[locationOfmsg : (len(msg) - 1)]
            locationOfFirstBrace = newStr.find("{")
            locationOfSecondBrace = newStr.find("}")
            processedStr = newStr[locationOfFirstBrace + 1 : locationOfSecondBrace]
            return 0 , processedStr
        elif "queue" in msg:
            return 1 , msg
        elif "location" in msg:
            locationOfFirstBrace = msg.find("{")
            locationOfSecondBrace = msg.find("}")
            processedStr = msg[locationOfFirstBrace + 1 : locationOfSecondBrace]
            return 2, processedStr
        else :
            return -1, ""


    def recvall(self, length):
        data = b''
        while len(data) < length:
            more = self.csock.recv(length - len(data))
            if not more:
                logging.error('Did not receive all the expected bytes from server.')
                break
            data += more
            decodedData = data.decode("utf-8")
            if ";" in decodedData:
                break
        return data

def server():
    # start serving (listening for clients)
    port = 9001
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost',port))
    ttt = TicTacToeEngine() # single instance of our engine
    turn = threading.Condition() # conditional lock
    player = 'x'
    playerCount = 0

    while True:
        # check if server has two peopled joined
        if playerCount < 2:
            sock.listen(1)
            logging.info('Server is listening on port ' + str(port))
            # client has connected
            sc,sockname = sock.accept()
            logging.info('Accepted connection.')
            playerCount += 1
            t = ClientThread(sockname, sc, ttt, player, turn)
            t.start()
            if player == 'x':
                player = 'o'
            else:
                player = 'x'
        gameover = ttt.is_game_over()
        if not gameover is '-':
            playerCount = 0

server()
