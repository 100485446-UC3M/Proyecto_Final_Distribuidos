#ifndef SERVER_H
#define SERVER_H

//Definir las librerías que serán utilizadas
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <pthread.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <netdb.h>
#include <limits.h>
#include <float.h>
#include <ctype.h>

// Estructura para almacenar la acción y los argumentos
typedef struct {
    char action;
    char *arguments;
} ParsedMessage;

// Inicialización de función de lectura
ssize_t readLine(int socket, char *buffer, size_t n);

// Estructura para almacenar usuario registrados
typedef struct UserNode {
    char username[256];           // Nombre del usuario
    struct UserNode *next;        // Puntero al siguiente nodo
} UserNode;

// Lista de usuarios
typedef struct {
    UserNode *head;               // Puntero al primer nodo
    pthread_mutex_t mutex;        // Mutex para proteger la lista
} UserList;

// Declarar la lista global de usuarios
extern UserList userList;


// Declaraciones de funciones
void initializeUserList();
int is_user_registered(const char *username);
int register_user(const char *username);
void free_user_list();
int sendMessage(int socket, char *buffer, int len);
int recvMessage(int socket, char *buffer, int len);
ssize_t readLine(int socket, char *buffer, size_t n);
int parseMessage(int socket, ParsedMessage *parsedMessage);
void freeParsedMessage(ParsedMessage *parsedMessage);

//Definir constantes globales que se van a utilizar con frecuencia
#define REGISTER '0'
#define ERROR_TUPLAS -1
#define ERROR_COMMUNICATION -2

#endif // SERVER_H