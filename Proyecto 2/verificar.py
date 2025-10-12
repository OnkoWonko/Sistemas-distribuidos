from socket import *
import customtkinter as ctk
uwu=""



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