import socket
import sys
import argparse

def main():
    # Configurar los argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Cliente para conectarse al servidor.")
    parser.add_argument("-s", "--server", required=True, help="Dirección IP del servidor")
    parser.add_argument("-p", "--port", required=True, type=int, help="Puerto del servidor")
    args = parser.parse_args()

    server_ip = args.server
    server_port = args.port

    # Crear el socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print(f"Error al crear el socket: {e}")
        sys.exit(1)

    # Conectar al servidor
    try:
        client_socket.connect((server_ip, server_port))
        print(f"Conectado al servidor {server_ip}:{server_port}")
    except socket.error as e:
        print(f"Error al conectar al servidor: {e}")
        sys.exit(1)

    # Bucle para enviar solicitudes
    try:     
        while True:     
            # Leer la solicitud del usuario
            user_input = input("Ingrese su solicitud: ").strip()
            
            if user_input == "9":
                print("Cerrando conexión...")
                break

            # Validar y procesar la solicitud
            parts = user_input.split(" ")
            if len(parts) < 2:
                print("Formato inválido. Debe incluir una acción y al menos un argumento.")
                continue

            action = parts[0].upper()
            arguments = parts[1:]

            # Construir el mensaje según la acción
            if action in ["REGISTER", "UNREGISTER", "DISCONNECT", "LIST_USERS"]:
                # Estas acciones esperan cadenas separadas por '\0'
                message = f"{action}\0{arguments[0]}\0"
            elif action == "CONNECT":
                # CONNECT espera username y puerto separados por '\0'
                if len(arguments) != 2:
                    print("Formato inválido. CONNECT requiere <username> <port>.")
                    continue
                message = f"{action}\0{arguments[0]}\0{arguments[1]}\0"
            elif action == "PUBLISH":
                # PUBLISH espera username, file_name y description separados por '\0'
                if len(arguments) != 3:
                    print("Formato inválido. PUBLISH requiere <username> <file_name> <description>.")
                    continue
                message = f"{action}\0{arguments[0]}\0{arguments[1]}\0{arguments[2]}\0"
            elif action == "DELETE":
                # DELETE espera username y file_name separados por '\0'
                if len(arguments) != 2:
                    print("Formato inválido. DELETE requiere <username> <file_name>.")
                    continue
                message = f"{action}\0{arguments[0]}\0{arguments[1]}\0"
            elif action == "LIST_CONTENT":
                # LIST_CONTENT espera username y target_username separados por '\0'
                if len(arguments) != 2:
                    print("Formato inválido. LIST_CONTENT requiere <username> <target_username>.")
                    continue
                message = f"{action}\0{arguments[0]}\0{arguments[1]}\0"
            else:
                print("Acción no reconocida.")
                continue

            # Enviar el mensaje al servidor
            try:
                client_socket.sendall(message.encode('utf-8'))
            except socket.error as e:
                print(f"Error al enviar el mensaje al servidor: {e}")
                break

            # Recibir el código de respuesta del servidor
            try:
                response_code = client_socket.recv(1)
                if not response_code:
                    print("El servidor cerró la conexión.")
                    break

                response_code = int.from_bytes(response_code, byteorder='big')
                print(f"Código de respuesta del servidor: {response_code}")

                # Si el código es 0, recibir información adicional (si aplica)
                if response_code == 0:
                    buffer = b""
                    while True:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        buffer += data
                    if buffer:
                        print("Respuesta del servidor:")
                        print(buffer.decode('utf-8'))

            except socket.error as e:
                print(f"Error al recibir la respuesta del servidor: {e}")
                break

    except KeyboardInterrupt:
        print("\nCerrando conexión...")
    finally:
        client_socket.close()
        print("Conexión cerrada.")

if __name__ == "__main__":
    main()