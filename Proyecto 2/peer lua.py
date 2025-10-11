import customtkinter as ctk
import socket
import threading
import time

MI_NOMBRE = "Lua"  
MI_IP = "127.0.0.4"     
PORT = 5003           
BUFF = 1024
REINTENTO = 5
MAX_INTENTOS = 3


PEERS = {
    "Emiliano": ("127.0.0.1", 5000),
    "Samuel": ("127.0.0.2", 5001),
    "Chris": ("127.0.0.3", 5002)
}

connections = {}   
chat_windows = {}   
connections_lock = threading.Lock()


# Funciones de conexión

def servidor(chat_update_callback):
    """Servidor que acepta conexiones entrantes"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((MI_IP, PORT))
    server_socket.listen(5)
    print(f"[Servidor] Escuchando en {MI_IP}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(
            target=handshake_inicial,
            args=(conn, chat_update_callback),
            daemon=True
        ).start()


def handshake_inicial(conn, chat_update_callback):
    """Intercambia nombres al iniciar conexión"""
    try:
        
        nombre_peer = conn.recv(BUFF).decode()
        if not nombre_peer:
            conn.close()
            return

    
        conn.send(MI_NOMBRE.encode())

        with connections_lock:
            connections[nombre_peer] = conn

        chat_update_callback(nombre_peer, f"[Sistema] {nombre_peer} se ha conectado.\n")
        threading.Thread(
            target=recibir_mensajes,
            args=(conn, nombre_peer, chat_update_callback),
            daemon=True
        ).start()

    except Exception as e:
        print(f"[Error Handshake] {e}")
        conn.close()


def recibir_mensajes(conn, remitente, chat_update_callback):
    """Recibe mensajes y los muestra en el chat correspondiente"""
    try:
        while True:
            data = conn.recv(BUFF)
            if not data:
                break
            mensaje = data.decode()
            chat_update_callback(remitente, f"[{remitente}]: {mensaje}\n")
    except Exception as e:
        print(f"[Error Recibir] {e}")
    finally:
        with connections_lock:
            if remitente in connections:
                del connections[remitente]
        conn.close()
        chat_update_callback(remitente, f"[Sistema] {remitente} se ha desconectado.\n")


def conectar_peer(nombre, chat_update_callback):
    """Intenta conectarse a un peer con reintentos limitados"""
    with connections_lock:
        if nombre in connections:
            return connections[nombre]

    peer_ip, peer_port = PEERS[nombre]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    for _ in range(MAX_INTENTOS):
        try:
            sock.connect((peer_ip, peer_port))

          
            sock.send(MI_NOMBRE.encode())
            nombre_peer = sock.recv(BUFF).decode()

            with connections_lock:
                connections[nombre_peer] = sock

            chat_update_callback(nombre_peer, f"[Sistema] Conectado a {peer_ip}:{peer_port}\n")

            threading.Thread(
                target=recibir_mensajes,
                args=(sock, nombre_peer, chat_update_callback),
                daemon=True
            ).start()
            return sock
        except ConnectionRefusedError:
            chat_update_callback(nombre, f"[Sistema] {nombre} no disponible, reintentando en {REINTENTO}s...\n")
            time.sleep(REINTENTO)
        except Exception as e:
            chat_update_callback(nombre, f"[Error Conexión] {e}\n")
            break

    chat_update_callback(nombre, f"[Sistema] No se pudo conectar a {nombre}.\n")
    return None


def enviar_mensaje(nombre, entry, chat_box):
    """Envía mensaje al peer"""
    msg = entry.get()
    if not msg:
        return

    with connections_lock:
        sock = connections.get(nombre)

    if not sock:
        sock = conectar_peer(nombre, actualizar_chat)

    if not sock:
        chat_box_insert(chat_box, f"[Sistema] No se pudo enviar mensaje a {nombre}.\n")
        return

    try:
        sock.send(msg.encode())
        chat_box_insert(chat_box, f"[Tú]: {msg}\n")
        entry.delete(0, "end")
    except Exception as e:
        chat_box_insert(chat_box, f"[Error] {e}\n")


# =====================
# INTERFAZ
# =====================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.title("Chat P2P de Lua")
root.geometry("900x600")

main_frame = ctk.CTkFrame(root, corner_radius=0)
main_frame.pack(fill="both", expand=True)

left_panel = ctk.CTkFrame(main_frame, width=250, corner_radius=0)
left_panel.pack(side="left", fill="y")

contacts_label = ctk.CTkLabel(left_panel, text="Contactos", font=("Arial", 18, "bold"))
contacts_label.pack(pady=10)

chat_container = ctk.CTkFrame(main_frame, corner_radius=0)
chat_container.pack(side="right", fill="both", expand=True)

def chat_box_insert(chat_box, mensaje):
    """Inserta texto en el chat (solo lectura habilitada)"""
    chat_box.configure(state="normal")
    chat_box.insert("end", mensaje)
    chat_box.configure(state="disabled")
    chat_box.see("end")

def mostrar_chat(nombre):
    for n, (frame, _) in chat_windows.items():
        frame.pack_forget()

    if nombre in chat_windows:
        chat_windows[nombre][0].pack(fill="both", expand=True)
    else:
        crear_chat(nombre)

def crear_chat(nombre):
    chat_frame = ctk.CTkFrame(chat_container, corner_radius=0)
    chat_frame.pack(fill="both", expand=True)

    header = ctk.CTkFrame(chat_frame, height=50)
    header.pack(fill="x")
    chat_name = ctk.CTkLabel(header, text=f"Chat - {nombre}", font=("Arial", 16, "bold"))
    chat_name.pack(side="left", padx=10, pady=10)

    chat_area = ctk.CTkTextbox(chat_frame, state="disabled", wrap="word")
    chat_area.pack(fill="both", expand=True, padx=10, pady=10)

    bottom_bar = ctk.CTkFrame(chat_frame, height=60)
    bottom_bar.pack(fill="x", pady=5)

    message_entry = ctk.CTkEntry(bottom_bar, placeholder_text="Escribe un mensaje...", width=500)
    message_entry.pack(side="left", padx=10, pady=10)

    send_button = ctk.CTkButton(
        bottom_bar, text="Enviar",
        command=lambda: enviar_mensaje(nombre, message_entry, chat_area),
        width=100, fg_color="#1f6aa5"
    )
    send_button.pack(side="right", padx=10)

    chat_windows[nombre] = (chat_frame, chat_area)

def actualizar_chat(nombre, mensaje):
    if nombre not in chat_windows:
        crear_chat(nombre)
    chat_area = chat_windows[nombre][1]
    chat_box_insert(chat_area, mensaje)

for nombre in PEERS.keys():
    contact_btn = ctk.CTkButton(
        left_panel,
        text=nombre,
        width=200,
        height=50,
        corner_radius=10,
        fg_color="#2a2a2a",
        hover_color="#1f6aa5",
        command=lambda n=nombre: mostrar_chat(n)
    )
    contact_btn.pack(pady=5)

threading.Thread(target=servidor, args=(actualizar_chat,), daemon=True).start()

root.mainloop()
