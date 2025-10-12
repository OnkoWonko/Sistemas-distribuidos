from socket import *
import customtkinter as ctk
uwu=""

PEERS = {
    "Emiliano": ("127.0.0.1",5000),
    "Samuel": ("127.0.0.2", 5001),
    "Chris": ("127.0.0.3", 5002),
    "Lua": ("127.0.0.4", 5003)
}



def verificar_cliente(ekisde,mi_ip):
    host ='127.0.0.5'
    port = 5005
    buff = 1024
    address = (host, port)
    mensaje = [host, port]

    mySocket = socket(AF_INET, SOCK_STREAM)
    mySocket.connect(address)
    print('Conectando al servidor...')
    print('socket definido...')
    mensaje=mi_ip

    print("Dame un mensaje para enviar: ")
    mySocket.send(mensaje.encode("utf-8"))
    print("Se fue el mensaje")
    respuesta = mySocket.recv(buff).decode("utf-8")
    print("El servidor Respondio:", respuesta)
    print("Cerrando conexión...")
    mySocket.close()
    ekisde=respuesta
    print(ekisde)
    return ekisde

def obtener_peers_sin(nombre):
    return {n: datos for n, datos in PEERS.items() if n != nombre}

