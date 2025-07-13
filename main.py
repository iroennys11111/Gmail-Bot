import random
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup
)
from pyrogram.enums import ParseMode
from flask import Flask, request
import threading
import time
import requests
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración del bot
API_ID = 14681595
API_HASH = "a86730aab5c59953c424abb4396d32d5"
BOT_TOKEN = "7983103020:AAHKsv6zTBPE0bcGYKO2EGyiKQXk8y38gwQ"

# Configuración para mantener el bot activo
PING_INTERVAL = 300  # 5 minutos
PING_URL = "https://gmail-bot-nooe.onrender.com"  # Cambia esto por tu URL de Render

# Mini servidor web mejorado para Render
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "🤖 Bot Generador de Emails Activo | Última verificación: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 200

@web_app.route('/ping')
def ping():
    return "pong", 200

def run_web_server():
    web_app.run(host='0.0.0.0', port=10000)

def keep_alive():
    """Función para mantener activo el servicio en Render"""
    while True:
        try:
            logger.info("Enviando ping para mantener activo el servicio...")
            response = requests.get(f"{PING_URL}/ping")
            logger.info(f"Respuesta del ping: {response.status_code}")
        except Exception as e:
            logger.error(f"Error al enviar ping: {e}")
        time.sleep(PING_INTERVAL)

# Inicializar el cliente de Pyrogram
bot = Client(
    "email_generator_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=4,  # Más workers para mejor manejo de callbacks
    in_memory=True  # Para evitar problemas con sesiones en Render
)

# Estados de conversación
USER_STATES = {}

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

@bot.on_message(filters.command("start"))
async def start_handler(client, message):
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

# ... (el resto de tus handlers permanecen igual, mantén todo el código original de los handlers)

def run_bot():
    """Función mejorada para iniciar el bot con manejo de errores y reconexión"""
    while True:
        try:
            logger.info("🚀 Iniciando bot...")
            bot.start()
            logger.info("Bot iniciado correctamente")
            # Mantener el bot corriendo
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Deteniendo bot por interrupción del usuario")
            bot.stop()
            break
        except Exception as e:
            logger.error(f"Error en el bot: {str(e)}")
            logger.info("⚡ Reconectando en 10 segundos...")
            time.sleep(10)
            continue

if __name__ == "__main__":
    # Iniciar servidor web en hilo separado
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # Iniciar el keep-alive en otro hilo
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    
    # Iniciar el bot con manejo de reconexión
    run_bot()
