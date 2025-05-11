import socket

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
    if not b:
        raise ConnectionError('No se recibió el código de resultado')
    # acceder a un elemento del objeto bytes devuelve el valor entero de ese byte
    return b[0]

def communicate_with_server(server: str, port: int, list_str: list, default_error_value: int) -> int:
    try:
        # with asegura cerrar el socket después de salir de él
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # timeout de 10 segundos para que si hay un fallo en las operaciones bloqueantes, el programa no quede bloqueado indefinidamente
            sock.settimeout(10)
            sock.connect((server, port))
            # envíamos todas las cadenas necesarias al servidor
            for string in list_str:
                send_str(sock, string)
            # devolvemos el código recibido y el socket por si hace falta más comunicaciones
            code = recv_byte(sock)
            return code, sock
            
    # si hay cualquier tipo de error en el cliente, se devuelve el valor predeterminado de error
    except (socket.error, ValueError, ConnectionError, OSError, TimeoutError, UnicodeError) as e:
        return default_error_value
    
def register(server: str, port: int, user: str) -> str:
    # mandamos solicitud de registro al servidor
    settings = SETTINGS['register']
    code, _sock = communicate_with_server(server, port, ["REGISTER", user], settings['default'])
    return settings.get(code, settings[settings['default']])

def unregister(server: str, port: int, user: str) -> str:
    # mandamos solicitud de borrar registro al servidor
    settings = SETTINGS['unregister']
    code, _sock = communicate_with_server(server, port, ["UNREGISTER", user], settings['default'])
    return settings.get(code, settings[settings['default']])

def connect(server: str, port: int, user: str, chosen_port: str) -> str:
    # mandamos solicitud de conexión al servidor
    settings = SETTINGS['connect']
    code, _sock = communicate_with_server(server, port, ["CONNECT", user, str(chosen_port)], settings['default'])
    return settings.get(code, settings[settings['default']])

def disconnect(server: str, port: int, user: str) -> str:
    # mandamos solicitud de desconexión al servidor
    settings = SETTINGS['disconnect']
    code, _sock = communicate_with_server(server, port, ["DISCONNECT", user], settings['default'])
    return settings.get(code, settings[settings['default']])
    
def publish(server: str, port: int, user: str, fileName: str, description: str) -> str:
    # mandamos solicitud de publicación al servidor
    settings = SETTINGS['publish']
    code, _sock = communicate_with_server(server, port, ["PUBLISH", user, fileName, description], settings['default'])
    return settings.get(code, settings[settings['default']])

def delete(server: str, port: int, user: str, fileName: str) -> str:
    # mandamos solicitud de publicación al servidor
    settings = SETTINGS['delete']
    code, _sock = communicate_with_server(server, port, ["DELETE", user, fileName], settings['default'])
    return settings.get(code, settings[settings['default']])

def list_users(server: str, port: int, user: str) -> str:
    # mandamos solicitud de lista de usuarios al servidor
    settings = SETTINGS['list_users']
    code, _sock = communicate_with_server(server, port, ["LIST_USERS", user], settings['default'])
    msg = settings.get(code, settings[settings['default']])
    # si el código recibido es 0, esperamos recibir la lista de usuarios
    if code == 0:
        try:
            # with asegura cerrar el socket después de salir de él
            with _sock as sock:
                #recibimos la información de cada usuario
                for i in range(int(recv_str(sock))):
                    msg += recv_str(sock)
            
        # si hay cualquier tipo de error en el cliente, se devuelve el valor predeterminado de error
        except (socket.error, ValueError, ConnectionError, OSError, TimeoutError, UnicodeError) as e:
            return settings[settings['default']]
    return msg