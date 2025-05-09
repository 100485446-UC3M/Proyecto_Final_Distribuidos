// Importamos el header
#include "server.h"

//Definir mutex, variable condicional y variable global de sincronización 'busy'
pthread_mutex_t mutex2;
pthread_cond_t cond;
int busy;
UserList userList = {NULL, PTHREAD_MUTEX_INITIALIZER};

// Función ejecutado por cada hilo para atender petición del cliente
void * SendResponse(void * sc){
    printf("Entramos al hilo");
    int s_local;
    int ret;
    s_local = (* (int *) sc);
    busy = 0;
    ParsedMessage parsedMessage;
    char buffer[256];

    // Recibir la acción a realizar
    if ((ret = parseMessage(s_local, &parsedMessage)) != 0){
        perror("SERVIDOR: un hilo no recibió la acción a realizar");
        pthread_exit(&ret);
    }
    // Procesar la solicitud
    switch (parsedMessage.action) {
        case REGISTER:
            printf("OPERATION %c FROM %s\n", parsedMessage.action, parsedMessage.arguments ? parsedMessage.arguments : "N/A");

            if (parsedMessage.arguments == NULL) {
                perror("SERVIDOR: Argumentos faltantes para REGISTER");
                ret = 2; // Error en la comunicación
                break;
            }

            // Registrar al usuario
            if (is_user_registered(parsedMessage.arguments)) {
                ret = 1; // Usuario ya registrado
            } else if (register_user(parsedMessage.arguments) == 0) {
                ret = 0; // Registro exitoso
            } else {
                ret = 2; // Error en el registro
            }
            break;

    default:
        perror("SERVIDOR: No existe la acción requerida");
        ret = ERROR_COMMUNICATION;
        break;
    }

    // Enviar respuesta al cliente
    send_response:
        snprintf(buffer, sizeof(buffer), "%d", ret);
        if ((ret = sendMessage(s_local, buffer, strlen(buffer) + 1)) != 0) {
            perror("SERVIDOR: Error al enviar el resultado al cliente");
        }
    
        // Liberar recursos
        freeParsedMessage(&parsedMessage);
        close(s_local);
        pthread_exit(&ret);
}


int main(int argc, char * argv[]) {

    if (argc != 3 || strcmp(argv[1], "-p") != 0) {
        printf("Uso: ./servidor -p <port>\n");
        goto cleanup_servidor;
    }

    
    char *endptr;
    long port = strtol(argv[2], &endptr, 10);
    if (*endptr != '\0' || port < 1024 || port > 49151) {
        perror("SERVIDOR: debe usar un puerto registrado\n");
        goto cleanup_servidor;
    }

    struct sockaddr_in server_addr, client_addr;
    socklen_t size;
    int ss, sc;

    // Crear socket del servidor
    if ((ss = socket (AF_INET, SOCK_STREAM, 0) ) < 0) { 
        perror("SERVIDOR: Error en el socket\n");
        goto cleanup_servidor;
    }
    int val = 1;
    if (setsockopt(ss, SOL_SOCKET, SO_REUSEADDR, &val, sizeof(val)) != 0){
        perror("SERVIDOR: Error al configurar el socket\n");
        goto cleanup_servidor;
    }

    // Asignar dirección IP y puerto
    memset((char *)&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    server_addr.sin_addr.s_addr = INADDR_ANY;
    if (bind(ss, (const struct sockaddr *) &server_addr, sizeof(server_addr)) != 0){
        perror("SERVIDOR: Error al asignar dirección al socket\n");
        goto cleanup_servidor;
    }
    initializeUserList();
    // Escuchar conexiones entrantes
    if (listen(ss, SOMAXCONN) != 0){
        perror("SERVIDOR: Error al habilitar el socket para recibir conexiones\n");
        goto cleanup_servidor;
    }
    printf("SERVIDOR: Activo\n");

    // Obtener la IP local
    struct sockaddr_in local_addr;
    socklen_t addr_len = sizeof(local_addr);
    if (getsockname(ss, (struct sockaddr *)&local_addr, &addr_len) == -1) {
        perror("SERVIDOR: Error al obtener la dirección local\n");
        close(ss);
        return -1;
    }
    char local_ip[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &local_addr.sin_addr, local_ip, INET_ADDRSTRLEN);

    // Mostrar mensaje de inicio
    printf("s > init server %s:%d\n", local_ip, port);
    
    // Inicializar variable global de control (busy)
    busy = 1;


    // Crear atributo de pthread DETACHED    
    pthread_attr_t thread_attr;
    pthread_attr_init(&thread_attr);
    pthread_attr_setdetachstate(&thread_attr, PTHREAD_CREATE_DETACHED);   

    size = sizeof(client_addr);

    // Bucle infinito para manejar las solicitudes
    while (1) {
        printf("SERVIDOR: Esperando conexión\n");
        // Aceptar conexión del cliente
        if ((sc = accept(ss, (struct sockaddr *) &client_addr, &size)) < 0){
            perror("SERVIDOR: Error al tratar de aceptar conexión\n");
            goto cleanup_servidor;
        }

        //Crea hilo para manejar la conexión
        pthread_t thread_id;
        if (pthread_create(&thread_id, &thread_attr, SendResponse, (void*) &sc) != 0) {
            perror("SERVIDOR: Error al crear el hilo\n");
            goto cleanup_servidor;
        }

    }
    
    return 0;

    cleanup_servidor:
        // Cerrar el socket del servidor
        close(ss);
        goto cleanup_servidor;
        free_user_list();
        return -1; // Indicar error
}

