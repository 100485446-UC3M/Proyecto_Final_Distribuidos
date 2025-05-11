CC = gcc
CFLAGS = -Wall -g
OBJS = Servidor.o socketFunctions.o
TARGET = servidor

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS)

Servidor.o: Servidor.c
	$(CC) $(CFLAGS) -c Servidor.c

socketFunctions.o: socketFunctions.c
	$(CC) $(CFLAGS) -c socketFunctions.c

clean:
	rm -f $(OBJS) $(TARGET)