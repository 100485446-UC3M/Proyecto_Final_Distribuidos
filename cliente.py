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
            user_input = input("Ingrese su solicitud (formato: c > PUBLISH <username> <file_name> <description>): ").strip()
            
            # Validar el formato de la solicitud
            if not user_input.startswith("c > "):
                print("Formato inválido. La solicitud debe comenzar con 'c > '.")
                continue

            # Extraer la acción y los argumentos
            parts = user_input[4:].split(" ", 3)  # Dividir en acción, username, file_name, description
            if len(parts) < 4:
                print("Formato inválido. Debe incluir: PUBLISH <username> <file_name> <description>")
                continue

            action, username, file_name, description = parts

            # Construir el mensaje para el servidor
            message = f"{action}\0{username}\0{file_name}\0{description}\0"

            # Enviar el mensaje al servidor
            client_socket.sendall(message.encode('utf-8'))

            # Recibir el código de respuesta del servidor
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
                print("Respuesta del servidor:")
                print(buffer.decode('utf-8'))

    except KeyboardInterrupt:
        print("\nCerrando conexión...")
    except socket.error as e:
        print(f"Error durante la comunicación con el servidor: {e}")
    finally:
        client_socket.close()
        print("Conexión cerrada.")

if __name__ == "__main__":
    main()