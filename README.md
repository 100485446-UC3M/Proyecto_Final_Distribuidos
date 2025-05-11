Para lograr correr el código es necesario llevar a cabo este proceso:

En una sesión de la terminal:
1. make
2. ./server -p <puerto del servidor>

En otra sesión de la terminal (y en la misma maquina que el cliente):

3. python3 webService.py

En otra sesión de la terminal, se puede ejecutar tantas veces como se quiera desde la misma o distintas máquinas: 

4. python3 client.py -s <ip del servidor> -p <puerto del servidor>
