import customtkinter as ctk
import socket
import threading
import time
from PIL import Image


# =====================
# CONFIGURACIÓN
# =====================
MI_IP = "127.0.0.1"
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


# RECONEXIÓN AUTOMÁTICA

def conectar_peer(sock, mi_ip, peer_ip, chat_box):
    while True:
        try:
            sock.bind((mi_ip, 0))  
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


# SERVIDOR

def servidor_recibir(chat_box):
    conn, addr = server_socket.accept()
    threading.Thread(target=recibir_mensajes, args=(conn, chat_box), daemon=True).start()


# INTERFAZ GRÁFICA

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.title("Chat tipo WhatsApp (Diseño)")
root.geometry("900x600")

# ====== MARCO PRINCIPAL ======
main_frame = ctk.CTkFrame(root, corner_radius=0)
main_frame.pack(fill="both", expand=True)

# ====== PANEL IZQUIERDO: CONTACTOS ======
left_panel = ctk.CTkFrame(main_frame, width=250, corner_radius=0)
left_panel.pack(side="left", fill="y")

# Título
contacts_label = ctk.CTkLabel(left_panel, text="Contactos", font=("Arial", 18, "bold"))
contacts_label.pack(pady=10)

# Lista de contactos
contacts = ["Samuel", "Lucía", "Carlos"]
for name in contacts:
    contact_btn = ctk.CTkButton(
        left_panel,
        text=name,
        width=200,
        height=50,
        corner_radius=10,
        fg_color="#2a2a2a",
        hover_color="#1f6aa5"
    )
    contact_btn.pack(pady=5)

# ====== PANEL DERECHO: CHAT ======
chat_panel = ctk.CTkFrame(main_frame, corner_radius=0)
chat_panel.pack(side="right", fill="both", expand=True)

# Encabezado del chat
chat_header = ctk.CTkFrame(chat_panel, height=50)
chat_header.pack(fill="x")

chat_name = ctk.CTkLabel(chat_header, text="Chat - Samuel", font=("Arial", 16, "bold"))
chat_name.pack(side="left", padx=10, pady=10)

# Área de mensajes
chat_area = ctk.CTkTextbox(chat_panel, state="normal", wrap="word")
chat_area.pack(fill="both", expand=True, padx=10, pady=10)

# Barra inferior para enviar mensaje
bottom_bar = ctk.CTkFrame(chat_panel, height=60)
bottom_bar.pack(fill="x", pady=5)

# Campo de texto
message_entry = ctk.CTkEntry(bottom_bar, placeholder_text="Escribe un mensaje...", width=500)
message_entry.pack(side="left", padx=10, pady=10)

# Botón para enviar imagen
img_icon = ctk.CTkButton(bottom_bar, text="📷", width=40, fg_color="#2a2a2a", hover_color="#1f6aa5")
img_icon.pack(side="left", padx=5)

# Botón para enviar mensaje
send_button = ctk.CTkButton(bottom_bar, text="Enviar", command=lambda: enviar_mensaje(message_entry, chat_area, client_socket),width=100, fg_color="#1f6aa5")
send_button.pack(side="right", padx=10)



# HILOS PARA SERVIDOR Y CONEXIÓN

threading.Thread(target=servidor_recibir, args=(chat_area,), daemon=True).start()
threading.Thread(target=conectar_peer, args=(client_socket, MI_IP, PEER_IP, chat_area), daemon=True).start()

root.mainloop()
