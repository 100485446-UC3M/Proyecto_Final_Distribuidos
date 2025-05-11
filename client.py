from enum import Enum
import argparse
import protocol
import socket
import threading

class client :

    # ******************** TYPES *********************
    # *
    # * @brief Return codes for the protocol methods
    # review
    class RC(Enum) :
        OK = 0
        ERROR = 1
        USER_ERROR = 2

    # review
    """ 
    # clase que contiene los posibles valores de la máquina de estados del cliente
    class State(Enum):
        UNREGISTERED = 0
        REGISTERED   = 1
        CONNECTED    = 2
    """

    # ****************** ATTRIBUTES ******************
    _server = None
    _port = -1

    _user = None
    _running = False
    _listener = None
    _thread = None

    # ******************** METHODS *******************

    @staticmethod
    def  register(user) :
        if (user is not None) and (type(user) is str) and (0 < len(user.encode("utf-8")) <= protocol.MAX_LEN):  
            msg = protocol.register(client._server, client._port, user)
            print(msg)
        else:
            settings = protocol.SETTINGS['register']
            print(settings[settings['default']])
   
    @staticmethod
    def  unregister(user) :
        if (user is not None) and (type(user) is str) and (0 < len(user.encode("utf-8")) <= protocol.MAX_LEN):  
            msg = protocol.unregister(client._server, client._port, user)
            print(msg)
        else:
            settings = protocol.SETTINGS['unregister']
            print(settings[settings['default']])
   

    
    @staticmethod
    def  connect(user) :
        if (user is not None) and (type(user) is str) and (0 < len(user.encode("utf-8")) <= protocol.MAX_LEN):
            if (client._user is not None) and (client._user != user):
                client.disconnect(client._user)

            # Creamos el socket de servidor
            client._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client._listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # El listener revisará periódicamente si debe ser desactivado
            client._listener.settimeout(1)

            # Configuramos este socket con la IP host local y puerto 0 → el SO elige un puerto libre
            client._listener.bind(('0.0.0.0', 0))

            # Recuperamos el puerto asignado
            _, chosen_port = client._listener.getsockname()

            # Empieza a escuchar. Permitimos que haya hasta 5 clientes en cola si ya hay uno conectado
            client._listener.listen(5)

            # función del hilo que escucha las peticiones de descarga de ficheros de otros usuarios
            def p2p(sock):
                while client._running:
                    try:
                        # connection es un nuevo socket que se usa para transmitir datos con el otro cliente
                        # client adress es una tupla con la dirección ip y el puerto del cliente
                        connection, client_address = sock.accept()
                        
                        # todo: manejar petición
                        try:
                            pass
                        finally:
                            connection.close()
                    except socket.timeout:
                        # cada segundo revisa de nuevo el flag
                        continue
                    except OSError:
                        # listener.close() lanza OSError. debemos salir del bucle
                        break
            
            # por defecto, el hilo ejecutará
            client._running = True
            # creamos el hilo
            client._thread = threading.Thread(target=p2p, args=(client._listener,))
            client._thread.start()

            msg = protocol.connect(client._server, client._port, user, chosen_port)
            print(msg)
            if msg == "CONNECT OK":
                # en caso de una conexión exitosa, cambiamos el nombre de usuario actualmente conectado
                client._user = user
        else:
            settings = protocol.SETTINGS['connect']
            print(settings[settings['default']])


    @staticmethod
    def  disconnect(user) :
        # toda desconexión implica borrar el nombre del usuario conectado actualmente
        client._user = None
        if (user is not None) and (type(user) is str) and (0 < len(user.encode("utf-8")) <= protocol.MAX_LEN):  
            if client._listener:
                # señalo al thread que debe parar su ejecución
                client._running = False
                # cierro el socket de escucha, lo que fuerza un OS error en el thread
                client._listener.close()
                # espero a que el hilo termine
                client._thread.join()

            msg = protocol.disconnect(client._server, client._port, user)
            print(msg)
        else:
            settings = protocol.SETTINGS['disconnect']
            print(settings[settings['default']])

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
                            # review
                            if (client._user is not None):
                                client.disconnect(client._user)
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