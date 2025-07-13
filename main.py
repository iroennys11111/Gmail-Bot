import random
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup
)
from pyrogram.enums import ParseMode
from flask import Flask
import threading

# Configuración del bot (variables originales mantenidas)
API_ID = 14681595
API_HASH = "a86730aab5c59953c424abb4396d32d5"
BOT_TOKEN = "7983103020:AAHKsv6zTBPE0bcGYKO2EGyiKQXk8y38gwQ"

# Mini servidor web para Render
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "🤖 Bot Generador de Emails Alternativos está activo", 200

def run_web_server():
    web_app.run(host='0.0.0.0', port=10000)

# Inicializar el cliente de Pyrogram
app = Client(
    "email_generator_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Estados de conversación
USER_STATES = {}

# --- FUNCIONES AUXILIARES ---
def generar_email_alternativo(email_principal, opcion, contador=None):
    """Genera un email alternativo según la opción seleccionada"""
    if '@' not in email_principal:
        return None
    
    usuario, dominio = email_principal.split('@', 1)
    
    if opcion == "numeros":
        return f"{usuario}+{random.randint(1000, 9999)}@{dominio}"
    elif opcion == "fecha":
        fecha = datetime.now().strftime("%d%m%y")
        return f"{usuario}+{fecha}@{dominio}"
    elif opcion == "palabra":
        palabras = ['temp', 'news', 'shop', 'service', 'web', 'app', 'work']
        return f"{usuario}+{random.choice(palabras)}@{dominio}"
    elif opcion == "masivo":
        metodos = [
            lambda: f"{usuario}+{random.randint(1000, 9999)}@{dominio}",
            lambda: f"{usuario}+{datetime.now().strftime('%d%m%y')}_{random.randint(10, 99)}@{dominio}",
            lambda: f"{usuario}.{random.choice(['temp','mail','alt','gen'])}{contador}@{dominio}",
            lambda: f"{usuario}_{random.choice(['shop','web','app','service'])}{random.randint(1, 9)}@{dominio}"
        ]
        return random.choice(metodos)()
    else:
        return None

def crear_menu_principal():
    """Crea el teclado principal con botones"""
    return ReplyKeyboardMarkup(
        [
            ["📧 Generar Email Alternativo"],
            ["ℹ️ Mi Información", "🆘 Ayuda"],
            ["🔙 Volver al Menú Principal"]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def crear_menu_generacion():
    """Crea el menú de opciones de generación"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔢 Números", callback_data="numeros"),
            InlineKeyboardButton("📅 Fecha", callback_data="fecha")
        ],
        [
            InlineKeyboardButton("📝 Palabra", callback_data="palabra"),
            InlineKeyboardButton("✏️ Personalizado", callback_data="personalizado")
        ],
        [
            InlineKeyboardButton("🎲 1000 Emails", callback_data="masivo"),
            InlineKeyboardButton("🔙 Volver", callback_data="volver")
        ]
    ])

# --- MANEJADORES DE COMANDOS ---
@app.on_message(filters.command("start"))
async def start(client, message):
    """Manejador del comando /start"""
    user_info = (
        f"👤 <b>Información de Usuario</b>\n\n"
        f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n"
        f"👤 <b>Nombre:</b> {message.from_user.first_name}\n"
    )
    
    if message.from_user.last_name:
        user_info += f"👥 <b>Apellido:</b> {message.from_user.last_name}\n"
    
    if message.from_user.username:
        user_info += f"📛 <b>Username:</b> @{message.from_user.username}\n"
    
    user_info += f"\n📅 <b>Fecha de registro:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    
    USER_STATES[message.from_user.id] = {
        "state": "main_menu",
        "first_name": message.from_user.first_name
    }
    
    await message.reply_text(
        f"🤖 <b>Bienvenido al Generador de Emails Alternativos</b>\n\n"
        f"{user_info}\n\n"
        "Selecciona una opción del menú:",
        reply_markup=crear_menu_principal(),
        parse_mode=ParseMode.HTML
    )

# [Resto de tus manejadores de mensajes y callbacks...]
# [Mantén todo el código original de handle_text_messages y handle_callbacks]

# --- INICIO DE LA APLICACIÓN ---
if __name__ == "__main__":
    # Iniciar servidor web en segundo plano
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()
    
    print("🤖 Bot y servidor web iniciados...")
    app.run()
