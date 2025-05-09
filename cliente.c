#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define BUFFER_SIZE 1024

void error_exit(const char *message) {
    perror(message);
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Uso: %s <IP del servidor> <puerto> <acción>\n", argv[0]);
        fprintf(stderr, "Ejemplo: %s 127.0.0.1 8080 LIST_USERS\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    const char *server_ip = argv[1];
    int server_port = atoi(argv[2]);
    const char *action = argv[3];

    // Crear el socket
    int client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket < 0) {
        error_exit("Error al crear el socket");
    }

    // Configurar la dirección del servidor
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(server_port);

    if (inet_pton(AF_INET, server_ip, &server_addr.sin_addr) <= 0) {
        error_exit("Dirección IP inválida");
    }

    // Conectar al servidor
    if (connect(client_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        error_exit("Error al conectar al servidor");
    }

    printf("Conectado al servidor %s:%d\n", server_ip, server_port);

    // Enviar la acción al servidor
    if (send(client_socket, action, strlen(action) + 1, 0) < 0) {
        error_exit("Error al enviar la acción al servidor");
    }

    // Recibir el código de respuesta del servidor
    char response_code;
    if (recv(client_socket, &response_code, 1, 0) <= 0) {
        error_exit("Error al recibir el código de respuesta del servidor");
    }

    printf("Código de respuesta del servidor: %d\n", response_code);

    // Si el código es 0, recibir la lista de usuarios conectados
    if (response_code == 0) {
        char buffer[BUFFER_SIZE];
        memset(buffer, 0, sizeof(buffer));

        if (recv(client_socket, buffer, sizeof(buffer), 0) <= 0) {
            error_exit("Error al recibir la lista de usuarios del servidor");
        }

        printf("Lista de usuarios conectados:\n%s\n", buffer);
    }

    // Cerrar el socket
    close(client_socket);
    printf("Conexión cerrada.\n");

    return 0;
}