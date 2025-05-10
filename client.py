from enum import Enum
import argparse
import protocol

class client :

    # ******************** TYPES *********************
    # *
    # * @brief Return codes for the protocol methods
    # review
    class RC(Enum) :
        OK = 0
        ERROR = 1
        USER_ERROR = 2

    # clase que contiene los posibles valores de la máquina de estados del cliente
    class State(Enum):
        UNREGISTERED = 0
        REGISTERED   = 1
        CONNECTED    = 2

    _state = State.UNREGISTERED

    # ****************** ATTRIBUTES ******************
    _server = None
    _port = -1

    # ******************** METHODS *******************

    @staticmethod
    def  register(user) :
        if (client._state == client.State.UNREGISTERED) and (user is not None) and (type(user) is str) and (0 < len(user.encode("utf-8")) <= protocol.MAX_LEN):  
            msg = protocol.register(client._server, client._port, user)
            print(msg)
            if msg == "REGISTER OK":
                client._state = client.State.REGISTERED
        else:
            settings = protocol.SETTINGS['register']
            print(settings[settings['default']])
   
    @staticmethod
    def  unregister(user) :
        if (client._state != client.State.UNREGISTERED) and (user is not None) and (type(user) is str) and (0 < len(user.encode("utf-8")) <= protocol.MAX_LEN):  
            msg = protocol.unregister(client._server, client._port, user)
            print(msg)
            if msg == "UNREGISTER OK":
                client._state = client.State.UNREGISTERED
        else:
            settings = protocol.SETTINGS['unregister']
            print(settings[settings['default']])
   

    
    @staticmethod
    def  connect(user) :
        if (client._state == client.State.REGISTERED) and (user is not None) and (type(user) is str) and (0 < len(user.encode("utf-8")) <= protocol.MAX_LEN):  
            msg = protocol.connect(client._server, client._port, user)
            print(msg)
            if msg == "CONNECT OK":
                client._state = client.State.CONNECTED
        else:
            settings = protocol.SETTINGS['connect']
            print(settings[settings['default']])


    @staticmethod
    def  disconnect(user) :
        #  todo
        return client.RC.ERROR
    

    @staticmethod
    def  publish(fileName,  description) :
        #  todo
        return client.RC.ERROR

    @staticmethod
    def  delete(fileName) :
        #  todo
        return client.RC.ERROR
    


    @staticmethod
    def  listusers() :
        #  todo
        return client.RC.ERROR

    @staticmethod
    def  listcontent(user) :
        #  todo
        return client.RC.ERROR
    

    @staticmethod
    def  getfile(user,  remote_FileName,  local_FileName) :
        #  todo
        return client.RC.ERROR

    # *
    # **
    # * @brief Command interpreter for the client. It calls the protocol functions.
    @staticmethod
    def shell():

        while (True) :
            try :
                command = input("c> ")
                line = command.split(" ")
                if (len(line) > 0):

                    line[0] = line[0].upper()

                    if (line[0]=="REGISTER") :
                        if (len(line) == 2) :
                            client.register(line[1])
                        else :
                            print("Syntax error. Usage: REGISTER <userName>")

                    elif(line[0]=="UNREGISTER") :
                        if (len(line) == 2) :
                            client.unregister(line[1])
                        else :
                            print("Syntax error. Usage: UNREGISTER <userName>")

                    elif(line[0]=="CONNECT") :
                        if (len(line) == 2) :
                            client.connect(line[1])
                        else :
                            print("Syntax error. Usage: CONNECT <userName>")
                    
                    elif(line[0]=="PUBLISH") :
                        if (len(line) >= 3) :
                            #  Remove first two words
                            description = ' '.join(line[2:])
                            client.publish(line[1], description)
                        else :
                            print("Syntax error. Usage: PUBLISH <fileName> <description>")

                    elif(line[0]=="DELETE") :
                        if (len(line) == 2) :
                            client.delete(line[1])
                        else :
                            print("Syntax error. Usage: DELETE <fileName>")

                    elif(line[0]=="LIST_USERS") :
                        if (len(line) == 1) :
                            client.listusers()
                        else :
                            print("Syntax error. Use: LIST_USERS")

                    elif(line[0]=="LIST_CONTENT") :
                        if (len(line) == 2) :
                            client.listcontent(line[1])
                        else :
                            print("Syntax error. Usage: LIST_CONTENT <userName>")

                    elif(line[0]=="DISCONNECT") :
                        if (len(line) == 2) :
                            client.disconnect(line[1])
                        else :
                            print("Syntax error. Usage: DISCONNECT <userName>")

                    elif(line[0]=="GET_FILE") :
                        if (len(line) == 4) :
                            client.getfile(line[1], line[2], line[3])
                        else :
                            print("Syntax error. Usage: GET_FILE <userName> <remote_fileName> <local_fileName>")

                    elif(line[0]=="QUIT") :
                        if (len(line) == 1) :
                            break
                        else :
                            print("Syntax error. Use: QUIT")
                    else :
                        print("Error: command " + line[0] + " not valid.")
            except Exception as e:
                print("Exception: " + str(e))

    # *
    # * @brief Prints program usage
    @staticmethod
    def usage() :
        print("Usage: python3 client.py -s <server> -p <port>")


    # *
    # * @brief Parses program execution arguments
    @staticmethod
    def  parseArguments(argv) :
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', type=str, required=True, help='Server IP')
        parser.add_argument('-p', type=int, required=True, help='Server Port')
        args = parser.parse_args()

        if (args.s is None):
            parser.error("Usage: python3 client.py -s <server> -p <port>")
            return False

        if ((args.p < 1024) or (args.p > 65535)):
            parser.error("Error: Port must be in the range 1024 <= port <= 65535");
            return False
        
        client._server = args.s
        client._port = args.p

        return True


    # ******************** MAIN *********************
    @staticmethod
    def main(argv) :
        if (not client.parseArguments(argv)) :
            client.usage()
            return
        # todo: El nombre server puede ser tanto el nombre (dominio-punto) como la dirección IP (decimal-punto) del servidor.

        client.shell()
        print("+++ FINISHED +++")
    

if __name__=="__main__":
    client.main([])