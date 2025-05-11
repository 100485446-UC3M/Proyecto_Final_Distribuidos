Primero debemos establecer el servidor.
Para ello, ejecute en una misma sesión de la terminal los siguientes comandos:
1. make
2. ./server -p <puerto del servidor>

Por otro lado, ya sea en la misma máquina que el servidor u otra, podemos crear
tantos clientes como queramos. 
Para ello, primero debemos ejecutar el servicio web en una sesión de la terminal:
3. python3 webService.py

En otra sesión de la terminal dentro de la misma máquina que el servidor web,
creamos un cliente de la siguiente manera: 
4. python3 client.py -s <ip del servidor> -p <puerto del servidor>
