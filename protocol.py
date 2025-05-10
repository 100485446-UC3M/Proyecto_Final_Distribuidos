import socket, threading

MAX_LEN = 256  # tamaño máximo de nombre, ruta, etc.


# Configuración para operaciones
SETTINGS = {
    'register': {
        0: "REGISTER OK",
        1: "USERNAME IN USE",
        2: "REGISTER FAIL",
        'default': 2
    },
    'unregister': {
        0: "UNREGISTER OK",
        1: "USER DOES NOT EXIST",
        2: "UNREGISTER FAIL",
        'default': 2
    },
    'connect': {
        0: "CONNECT OK",
        1: "CONNECT FAIL , USER DOES NOT EXIST", # review: espacio antes de la coma
        2: "USER ALREADY CONNECTED",
        3: "CONNECT FAIL",
        'default': 3
    },
    'publish': {
        0: "PUBLISH OK",
        1: "PUBLISH FAIL , USER DOES NOT EXIST",
        2: "PUBLISH FAIL , USER NOT CONNECTED",
        3: "PUBLISH FAIL , CONTENT ALREADY PUBLISHED",
        4: "PUBLISH FAIL",
        'default': 4
    },
    'delete': {
        0: "DELETE OK",
        1: "DELETE FAIL , USER DOES NOT EXIST",
        2: "DELETE FAIL , USER NOT CONNECTED",
        3: "DELETE FAIL , CONTENT NOT PUBLISHED",
        4: "DELETE FAIL",
        'default': 4
    },
    'list_users': {
        0: "LIST_USERS OK",
        1: "LIST_USERS FAIL , USER DOES NOT EXIST",
        2: "LIST_USERS FAIL , USER NOT CONNECTED",
        3: "LIST_USERS FAIL",
        'default': 3
    },
    'list_content': {
        0: "LIST_CONTENT OK",
        1: "LIST_CONTENT FAIL , USER DOES NOT EXIST",
        2: "LIST_CONTENT FAIL , USER NOT CONNECTED",
        3: "LIST_CONTENT FAIL , REMOTE USER DOES NOT EXIST",
        4: "LIST_CONTENT FAIL",
        'default': 4
    },
    'disconnect': {
        0: "DISCONNECT OK",
        1: "DISCONNECT FAIL , USER DOES NOT EXIST",
        2: "DISCONNECT FAIL , USER NOT CONNECTED",
        3: "DISCONNECT FAIL",
        'default': 3
    },
    'get_file': {
        0: "GET_FILE OK",
        1: "GET_FILE FAIL , FILE NOT EXIST",
        2: "GET_FILE FAIL",
        'default': 2
    }
}

def send_str(sock: socket.socket, txt: str) -> None:
    # data es un objeto bytes que codifica los carácteres del string según utf-8
    data = txt.encode('utf-8')
    # review: no enviar string si está vacío?
    if len(data) == 0:
        raise ValueError("El campo está vacío")
    elif len(data) > MAX_LEN:
        raise ValueError(f'El campo supera {MAX_LEN} bytes: {txt!r}')
    # crea un objeto bytes con los bytes de ambos
    sock.sendall(data + b'\0')

def recv_str(sock: socket.socket) -> str:
    # como el objeto bytes, pero un bytearray es mutable
    buf = bytearray()
    while True:
        # b es un objeto bytes que contiene un único byte
        b = sock.recv(1)
        if not b:
            raise ConnectionError('Conexión cerrada inesperadamente')
        # b'\0' es un objeto bytes que contiene el byte \0
        if b == b'\0':
            break
        buf.extend(b)
        if len(buf) > MAX_LEN:
            raise ValueError('Recibido demasiado largo')
    # una vez estamos seguros de tener todo el string, lo decodificamos y devolvemos
    return buf.decode('utf-8')

def recv_byte(sock: socket.socket) -> int:
    b = sock.recv(1)
    print(b)
    if not b:
        raise ConnectionError('No se recibió el código de resultado')
    # acceder a un elemento del objeto bytes devuelve el valor entero de ese byte
    return b[0]

def communicate_with_server(server: str, port: int, list_str: list, default_error_value: int) -> int:
    try:
        # with asegura cerrar el socket después de salir de él
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # timeout de 30 segundos para que si hay un fallo en las operaciones bloqueantes, el programa no quede bloqueado indefinidamente
            sock.connect((server, port))
            # envíamos todas las cadenas necesarias al servidor
            for string in list_str:
                send_str(sock, string)
            # devolvemos el código recibido
            code = recv_byte(sock)
            print(code)
            return code
            
    # si hay cualquier tipo de error en el cliente, se devuelve el valor predeterminado de error
    except (socket.error, ValueError, ConnectionError, OSError, TimeoutError, UnicodeError) as e:
        return default_error_value
    
def register(server: str, port: int, user: str) -> int:
    settings = SETTINGS['register']
    code = communicate_with_server(server, port, ["REGISTER", user], settings['default'])
    return settings.get(code, settings[settings['default']])

def unregister(server: str, port: int, user: str) -> int:
    settings = SETTINGS['unregister']
    code = communicate_with_server(server, port, ["UNREGISTER", user], settings['default'])
    return settings.get(code, settings[settings['default']])

def connect(server: str, port: int, user: str) -> int:
    global running, listener, thread
    
    # Creamos el socket de servidor
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # El listener revisará periódicamente si debe ser desactivado
    listener.settimeout(1)

    # Configuramos este socket con la IP host local y puerto 0 → el SO elige un puerto libre
    listener.bind(('0.0.0.0', 0))

    # Recuperamos el puerto asignado
    _, chosen_port = listener.getsockname()
    print(f"Puerto libre asignado: {chosen_port}")

    # Empieza a escuchar. Permitimos que haya hasta 5 clientes en cola si ya hay uno conectado
    listener.listen(5)

    # función del hilo que escucha las peticiones de descarga de ficheros de otros usuarios
    def p2p(sock):
        while running:
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


    # creamos el hilo
    thread = threading.Thread(target=p2p, daemon='True', args=(listener,))
    running = True
    thread.start()

    # mandamos solicitud de conexión al servidor
    settings = SETTINGS['connect']
    code = communicate_with_server(server, port, ["CONNECT", user, str(chosen_port)], settings['default'])
    return settings.get(code, settings[settings['default']])

def disconnect(server: str, port: int, user: str) -> int:
    global running, listener, thread
    # señalo al thread que debe parar su ejecución
    running = False
    # cierro el socket de escucha, lo que fuerza un OS error en el thread
    listener.close()
    # espero a que el hilo termine
    thread.join()
     
    # mandamos solicitud de desconexión al servidor
    settings = SETTINGS['disconnect']
    code = communicate_with_server(server, port, ["DISCONNECT", user], settings['default'])
    return settings.get(code, settings[settings['default']])
    