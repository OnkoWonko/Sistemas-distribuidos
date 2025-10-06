import threading
from socket import *

buff = 1024


def servidor(host, port):
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print(f"[{host}] Esperando conexiones en puerto {port}...")

    while True:
        conn, addr = s.accept()
        print(f"[{host}] Conectado desde {addr}")
        hilo = threading.Thread(target=recibir_mensajes, args=(conn, addr))
        hilo.start()

def recibir_mensajes(conn, addr):
    while True:
        try:
            datos = conn.recv(buff).decode("utf-8")
            if not datos or datos == "salir":
                print(f"[{addr[0]}] se desconectó.")
                break
            print(f"\n {datos:>30}:[{addr[0]}]:")
            print(f"[Tú]: ", end="")  # vuelve a mostrar el prompt
        except:
            break
    conn.close()

# ===============================
#  CLIENTE: envía mensajes
# ===============================
def cliente(mi_host, otro_host, port):
    c = socket(AF_INET, SOCK_STREAM)
    try:
        c.connect((otro_host, port))
    except ConnectionRefusedError:
        print(f"[{mi_host}] No se pudo conectar con {otro_host}:{port}")
        return

    print(f"[{mi_host}] Conectado con {otro_host}:{port}")
    while True:
        msg = input(f"[Tú]: ")
        c.send(msg.encode("utf-8"))
        if msg == "salir":
            break
    c.close()
    print("[CLIENTE] Conexión cerrada.")

# ===============================
#  PUNTO DE ENTRADA
# ===============================
if __name__ == "__main__":
    host_local = ("127.0.0.1")
    host_remoto = ("127.0.0.2")
    port = 5000

    # Hilo servidor (escucha)
    hilo_servidor = threading.Thread(target=servidor, args=(host_local, port))
    hilo_servidor.daemon = True
    hilo_servidor.start()

    # Hilo cliente (envía)
    cliente(host_local, host_remoto, port)
