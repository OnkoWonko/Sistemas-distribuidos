from socket import *

PEERS =["127.0.0.1","127.0.0.2","127.0.0.3","127.0.0.4"]




def client():
    host ='127.0.0.2'
    port = 5000
    buff = 1024
    address = (host, port)

    mySocket = socket(AF_INET, SOCK_STREAM)
    mySocket.connect(address)
    print('Conectando al servidor...')
    print('socket definido...')
    if PEERS["Samuel"]==address:
        print("PRUEBA ",PEERS["Samuel"][0])
    while mensaje != "salir":
        print("Dame un mensaje para enviar: ")
        mensaje = input("-->")
        mySocket.send(mensaje.encode("utf-8"))
        print("Se fue el mensaje")
        respuesta = mySocket.recv(buff).decode("utf-8")
        print("El servidor Respondio:", respuesta)
    mySocket.close()

def Main():
    i=0
    host = '127.0.0.5'
    port = 5005
    buff = 1024
    address = (host, port)

    mySocket = socket(AF_INET, SOCK_STREAM)
    print('socket definido...')
    print("PRUEBA ",PEERS[0][0])
    
    mySocket.bind(address)
    mySocket.listen(5)

    while True:
        print('Servidor Esperando')
        conn, addr = mySocket.accept()      
        print('Se conectó desde: ' + str(addr))
        datos = conn.recv(buff).decode("utf-8")
        print("Datos recibidos de:", datos)
        


        while i<PEERS.__len__():
            if PEERS[i]==datos:
                print("El cliente está autorizado")
                mensaje="T"
                conn.send(mensaje.encode("utf-8"))
            else:
                print("El cliente no está autorizado")
            i+=1
        
        conn.close()
        print("Cerrando la conexión ...")
        i=0
        if datos == "salir":
            print("El cliente ha cerrado la conexión.")
            break
        


if __name__ == '__main__':
    Main()
    print("Terminando el servicio")
