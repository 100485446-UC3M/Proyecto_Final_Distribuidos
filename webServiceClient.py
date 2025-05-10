import zeep

class client:
    # ... código existente ...

    @staticmethod
    def get_datetime():
        # Consumir el servicio web para obtener la fecha y hora
        wsdl = 'http://127.0.0.1:5000/?wsdl'
        client = zeep.Client(wsdl=wsdl)
        return client.service.get_datetime()

    @staticmethod
    def register(user):
        if client._state == client.State.UNREGISTERED and user:
            datetime_str = client.get_datetime()  # Obtener la fecha y hora
            msg = protocol.register(client._server, client._port, user, datetime_str)
            print(msg)
            if msg == "REGISTER OK":
                client._state = client.State.REGISTERED
        else:
            print("Error: No se puede registrar en el estado actual.")

    # Modifica las demás operaciones (unregister, connect, etc.) de manera similar