import customtkinter as ctk
import socket
import threading
import time

# =====================
# CONFIGURACIÓN
# =====================
MI_IP = "127.0.0.3"
PEER_IP = "127.0.0.2"
PORT = 5000
BUFF = 1024
REINTENTO = 5  # segundos para reintentar conexión

# =====================
# SOCKETS
# =====================
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((MI_IP, PORT))
server_socket.listen(1)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# =====================
# FUNCIONES
# =====================
def recibir_mensajes(sock, chat_box):
    while True:
        try:
            data = sock.recv(BUFF).decode()
            if not data:
                break
            chat_box.insert("end", f"[{PEER_IP}]: {data}\n")
            chat_box.see("end")
        except:
            break

def enviar_mensaje(entry, chat_box, sock):
    msg = entry.get()
    if msg:
        try:
            sock.send(msg.encode())
            chat_box.insert("end", f"[Tú]: {msg}\n")
            chat_box.see("end")
            entry.delete(0, "end")
        except:
            chat_box.insert("end", "[Sistema] No conectado al peer.\n")
            chat_box.see("end")

# =====================
# RECONEXIÓN AUTOMÁTICA
# =====================
def conectar_peer(sock, mi_ip, peer_ip, chat_box):
    while True:
        try:
            sock.bind((mi_ip, 0))  # puerto automático
        except OSError:
            pass  # ya estaba vinculado
        try:
            sock.connect((peer_ip, PORT))
            chat_box.insert("end", f"[Sistema] Conectado a {peer_ip}:{PORT}\n")
            chat_box.see("end")
            break
        except ConnectionRefusedError:
            chat_box.insert("end", f"[Sistema] Peer no disponible, reintentando en {REINTENTO}s...\n")
            chat_box.see("end")
            time.sleep(REINTENTO)

# =====================
# SERVIDOR
# =====================
def servidor_recibir(chat_box):
    conn, addr = server_socket.accept()
    threading.Thread(target=recibir_mensajes, args=(conn, chat_box), daemon=True).start()

# =====================
# INTERFAZ GRÁFICA
# =====================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Chat P2P")
app.geometry("400x400")

chat_box = ctk.CTkTextbox(app, width=360, height=250)
chat_box.pack(pady=10)

entry = ctk.CTkEntry(app, width=250)
entry.pack(side="left", padx=5, pady=10)

btn = ctk.CTkButton(app, text="Enviar", command=lambda: enviar_mensaje(entry, chat_box, client_socket))
btn.pack(side="left", padx=5)

# =====================
# HILOS PARA SERVIDOR Y CONEXIÓN
# =====================
threading.Thread(target=servidor_recibir, args=(chat_box,), daemon=True).start()
threading.Thread(target=conectar_peer, args=(client_socket, MI_IP, PEER_IP, chat_box), daemon=True).start()

app.mainloop()
