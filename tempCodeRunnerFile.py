import customtkinter as ctk
from PIL import Image

# Configuración base
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
chat_area = ctk.CTkTextbox(chat_panel, state="disabled", wrap="word")
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
send_button = ctk.CTkButton(bottom_bar, text="Enviar", width=100, fg_color="#1f6aa5")
send_button.pack(side="right", padx=10)

root.mainloop()
