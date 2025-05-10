import zeep

def main():
    # URL del WSDL del servicio
    wsdl = 'http://127.0.0.1:5000/?wsdl'

    # Crear el cliente SOAP
    client = zeep.Client(wsdl=wsdl)

    # Llamar al método get_datetime
    current_datetime = client.service.get_datetime()
    print(f"Fecha y hora actual: {current_datetime}")

if __name__ == '__main__':
    main()