import customtkinter as ctk
import socket
import threading
import time
import base64
import io
from PIL import Image, ImageTk
from tkinter import filedialog
import verificar

# ==========================
# CONFIGURACIÓN GENERAL
# ==========================
MI_NOMBRE = "Emiliano"
MI_IP = "127.0.0.1"
PORT = 5000
BUFF = 1024*1024*5
REINTENTO = 5
MAX_INTENTOS = 3
verificador=""
objeto =verificar
PEERS = {
    
}

verificador=objeto.verificar_cliente(verificador,MI_IP)
print(verificador)
verificador=verificador.strip()
print("VERIFICADOR ",verificador)
PEERS=objeto.obtener_peers_sin(MI_NOMBRE)

connections = {}
connections_lock = threading.Lock()
chat_windows = {}

# ==========================
# FUNCIONES DE CONEXIÓN
# ==========================
def servidor(chat_update_callback):
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
    try:
        nombre_peer = conn.recv(BUFF).decode()
        if not nombre_peer:
            conn.close()
            return
        conn.send(MI_NOMBRE.encode())

        with connections_lock:
            connections[nombre_peer] = conn

        chat_update_callback(nombre_peer, f"[Sistema] {nombre_peer} se ha conectado.", "text")

        threading.Thread(
            target=recibir_mensajes,
            args=(conn, nombre_peer, chat_update_callback),
            daemon=True
        ).start()
    except Exception as e:
        print(f"[Error Handshake] {e}")
        conn.close()

def recibir_mensajes(conn, remitente, chat_update_callback):
    try:
        while True:
            data = conn.recv(65536)  # Permitir mensajes grandes (imágenes)
            if not data:
                break
            mensaje = data.decode(errors="ignore")

            # Diferenciar texto e imagen
            if mensaje.startswith("IMG|"):
                b64_data = mensaje.replace("IMG|", "")
                chat_update_callback(remitente, b64_data, "image")
            else:
                chat_update_callback(remitente, mensaje, "text")

    except Exception as e:
        print(f"[Error Recibir] {e}")
    finally:
        with connections_lock:
            if remitente in connections:
                del connections[remitente]
        conn.close()
        chat_update_callback(remitente, f"[Sistema] {remitente} se ha desconectado.", "text")

def conectar_peer(nombre, chat_update_callback):
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

            chat_update_callback(nombre_peer, f"[Sistema] Conectado a {peer_ip}:{peer_port}", "text")

            threading.Thread(
                target=recibir_mensajes,
                args=(sock, nombre_peer, chat_update_callback),
                daemon=True
            ).start()
            return sock
        except ConnectionRefusedError:
            chat_update_callback(nombre, f"[Sistema] {nombre} no disponible, reintentando...", "text")
            time.sleep(REINTENTO)
        except Exception as e:
            chat_update_callback(nombre, f"[Error Conexión] {e}", "text")
            break

    chat_update_callback(nombre, f"[Sistema] No se pudo conectar a {nombre}.", "text")
    return None

def enviar_mensaje(nombre, entry, chat_frame, tipo="text"):
    with connections_lock:
        sock = connections.get(nombre)

    if not sock:
        sock = conectar_peer(nombre, actualizar_chat)

    if not sock:
        mostrar_mensaje(chat_frame, f"[Sistema] No se pudo enviar mensaje a {nombre}.", "text")
        return

    if tipo == "text":
        msg = entry.get()
        if not msg:
            return
        try:
            sock.send(msg.encode())
            mostrar_mensaje(chat_frame, f"[Tú]: {msg}", "text")
            entry.delete(0, "end")
        except Exception as e:
            mostrar_mensaje(chat_frame, f"[Error] {e}", "text")

    elif tipo == "image":
        try:
            filepath = filedialog.askopenfilename(
                title="Seleccionar imagen",
                filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.gif")]
            )
            if not filepath:
                return

            with open(filepath, "rb") as f:
                img_bytes = f.read()

            b64_data = base64.b64encode(img_bytes).decode()
            mensaje = "IMG|" + b64_data
            sock.send(mensaje.encode())

            mostrar_mensaje(chat_frame, filepath, "local_image")

        except Exception as e:
            mostrar_mensaje(chat_frame, f"[Error al enviar imagen] {e}", "text")

# ==========================
# INTERFAZ
# ==========================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.title(f"Chat P2P - {MI_NOMBRE}")
root.geometry("900x600")

main_frame = ctk.CTkFrame(root)
main_frame.pack(fill="both", expand=True)

# Panel izquierdo
left_panel = ctk.CTkFrame(main_frame, width=250)
left_panel.pack(side="left", fill="y")

ctk.CTkLabel(left_panel, text="Contactos", font=("Arial", 18, "bold")).pack(pady=10)

# Contenedor del chat
chat_container = ctk.CTkFrame(main_frame)
chat_container.pack(side="right", fill="both", expand=True)

def mostrar_mensaje(chat_frame, contenido, tipo):
    """Muestra texto o imagen en el chat."""
    if tipo == "text":
        label = ctk.CTkLabel(chat_frame, text=contenido, wraplength=500, anchor="w", justify="left")
        label.pack(anchor="w", padx=10, pady=2)
    elif tipo == "image":
        try:
            img_bytes = base64.b64decode(contenido)
            image = Image.open(io.BytesIO(img_bytes))
            image.thumbnail((250, 250))
            photo = ImageTk.PhotoImage(image)
            lbl = ctk.CTkLabel(chat_frame, image=photo, text="")
            lbl.image = photo
            lbl.pack(anchor="w", padx=10, pady=5)
        except Exception as e:
            ctk.CTkLabel(chat_frame, text=f"[Error imagen] {e}").pack(anchor="w", padx=10)
    elif tipo == "local_image":
        try:
            image = Image.open(contenido)
            image.thumbnail((250, 250))
            photo = ImageTk.PhotoImage(image)
            lbl = ctk.CTkLabel(chat_frame, image=photo, text="")
            lbl.image = photo
            lbl.pack(anchor="e", padx=10, pady=5)
        except Exception as e:
            ctk.CTkLabel(chat_frame, text=f"[Error imagen local] {e}").pack(anchor="e", padx=10)

def actualizar_chat(nombre, mensaje, tipo):
    if nombre not in chat_windows:
        crear_chat(nombre)
    chat_frame = chat_windows[nombre][1]
    mostrar_mensaje(chat_frame, mensaje, tipo)

def mostrar_chat(nombre):
    for n, (frame, _) in chat_windows.items():
        frame.pack_forget()
    if nombre in chat_windows:
        chat_windows[nombre][0].pack(fill="both", expand=True)
    else:
        crear_chat(nombre)

def crear_chat(nombre):
    chat_frame = ctk.CTkScrollableFrame(chat_container)
    chat_frame.pack(fill="both", expand=True)

    bottom_bar = ctk.CTkFrame(chat_frame)
    bottom_bar.pack(fill="x", pady=5)

    entry = ctk.CTkEntry(bottom_bar, placeholder_text="Escribe un mensaje...", width=400)
    entry.pack(side="left", padx=10, pady=5)

    send_btn = ctk.CTkButton(bottom_bar, text="Enviar", command=lambda: enviar_mensaje(nombre, entry, chat_frame, "text"))
    send_btn.pack(side="left", padx=5)

    img_btn = ctk.CTkButton(bottom_bar, text="📷", width=40, command=lambda: enviar_mensaje(nombre, entry, chat_frame, "image"))
    img_btn.pack(side="left", padx=5)

    chat_windows[nombre] = (chat_frame, chat_frame)

# Botones de contactos
for nombre in PEERS.keys():
    ctk.CTkButton(
        left_panel,
        text=nombre,
        width=200,
        height=50,
        corner_radius=10,
        fg_color="#2a2a2a",
        hover_color="#1f6aa5",
        command=lambda n=nombre: mostrar_chat(n)
    ).pack(pady=5)

def mostrar_alerta(titulo, mensaje):
    alerta = ctk.CTkToplevel()
    alerta.title(titulo)
    alerta.geometry("300x150")
    alerta.grab_set()

    label = ctk.CTkLabel(alerta, text=mensaje, wraplength=250, font=("Arial", 13))
    label.pack(pady=20)

    def cerrar_todo():
        alerta.destroy()
        root.destroy()

    btn = ctk.CTkButton(alerta, text="Aceptar", command=cerrar_todo)
    btn.pack(pady=10)
    alerta.mainloop()

# Iniciar servidor
threading.Thread(target=servidor, args=(actualizar_chat,), daemon=True).start()

if verificador=="T":
    root.mainloop()   
else:
    mostrar_alerta("Acceso Denegado", "No tienes permiso para usar esta aplicación.")
