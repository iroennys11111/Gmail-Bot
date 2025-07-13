import random
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup
)
from pyrogram.enums import ParseMode

# Configuración del bot
API_ID = 14681595
API_HASH = "a86730aab5c59953c424abb4396d32d5"
BOT_TOKEN = "7983103020:AAHKsv6zTBPE0bcGYKO2EGyiKQXk8y38gwQ"

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
    # Mostrar información del usuario
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
    
    # Configurar estado del usuario
    USER_STATES[message.from_user.id] = {
        "state": "main_menu",
        "first_name": message.from_user.first_name
    }
    
    # Enviar mensaje de bienvenida con teclado
    await message.reply_text(
        f"🤖 <b>Bienvenido al Generador de Emails Alternativos</b>\n\n"
        f"{user_info}\n\n"
        "Selecciona una opción del menú:",
        reply_markup=crear_menu_principal(),
        parse_mode=ParseMode.HTML
    )

# --- MANEJADORES DE MENSAJES ---
@app.on_message(filters.text)
async def handle_text_messages(client, message):
    """Manejador de mensajes de texto"""
    user_id = message.from_user.id
    user_state = USER_STATES.get(user_id, {}).get("state")
    
    if message.text == "📧 Generar Email Alternativo":
        USER_STATES[user_id]["state"] = "waiting_email"
        await message.reply_text(
            "📩 Por favor, envía tu email principal (ejemplo: usuario@gmail.com)",
            reply_markup=ReplyKeyboardMarkup([["🔙 Volver"]], resize_keyboard=True)
        )
    
    elif message.text == "ℹ️ Mi Información":
        user = USER_STATES.get(user_id, {})
        await message.reply_text(
            f"👤 <b>Información de Usuario</b>\n\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            f"👤 <b>Nombre:</b> {user.get('first_name', 'No disponible')}\n"
            f"📧 <b>Email registrado:</b> {user.get('email', 'No proporcionado')}\n\n"
            f"📅 <b>Última actividad:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            parse_mode=ParseMode.HTML,
            reply_markup=crear_menu_principal()
        )
    
    elif message.text == "🆘 Ayuda":
        await message.reply_text(
            "ℹ️ <b>Ayuda del Bot</b>\n\n"
            "Este bot te permite generar emails alternativos a partir de tu email principal.\n\n"
            "<b>Opciones disponibles:</b>\n"
            "- 🔢 Números: Añade números aleatorios\n"
            "- 📅 Fecha: Añade la fecha actual\n"
            "- 📝 Palabra: Añade una palabra aleatoria\n"
            "- ✏️ Personalizado: Añade tu propio sufijo\n"
            "- 🎲 1000 Emails: Genera un archivo con 1000 emails\n\n"
            "Usa los botones para navegar por el menú.",
            parse_mode=ParseMode.HTML,
            reply_markup=crear_menu_principal()
        )
    
    elif message.text == "🔙 Volver" or message.text == "🔙 Volver al Menú Principal":
        USER_STATES[user_id]["state"] = "main_menu"
        await message.reply_text(
            "🏠 <b>Menú Principal</b>",
            reply_markup=crear_menu_principal(),
            parse_mode=ParseMode.HTML
        )
    
    elif user_state == "waiting_email":
        if '@' not in message.text:
            await message.reply_text("❌ Email no válido. Debe contener '@'. Intenta nuevamente.")
            return
        
        USER_STATES[user_id] = {
            "state": "waiting_option",
            "email": message.text,
            "first_name": message.from_user.first_name
        }
        
        await message.reply_text(
            f"📧 Email principal: <code>{message.text}</code>\n\n"
            "Selecciona cómo quieres generar tu email alternativo:",
            reply_markup=crear_menu_generacion(),
            parse_mode=ParseMode.HTML
        )
    
    elif user_state == "waiting_suffix":
        email_principal = USER_STATES[user_id]["email"]
        usuario, dominio = email_principal.split('@', 1)
        email_alternativo = f"{usuario}+{message.text}@{dominio}"
        
        await message.reply_text(
            f"✅ <b>Email alternativo generado:</b>\n\n<code>{email_alternativo}</code>\n\n"
            "Puedes copiarlo o generar otro.",
            parse_mode=ParseMode.HTML,
            reply_markup=crear_menu_principal()
        )
        
        USER_STATES[user_id]["state"] = "main_menu"

# --- MANEJADORES DE CALLBACKS ---
@app.on_callback_query()
async def handle_callbacks(client, callback_query):
    """Manejador de callbacks de botones inline"""
    user_id = callback_query.from_user.id
    user_data = USER_STATES.get(user_id, {})
    email_principal = user_data.get("email")
    opcion = callback_query.data
    
    if opcion == "volver":
        await callback_query.message.edit_text(
            "🏠 <b>Menú Principal</b>",
            reply_markup=None
        )
        await callback_query.message.reply_text(
            "Selecciona una opción:",
            reply_markup=crear_menu_principal(),
            parse_mode=ParseMode.HTML
        )
        await callback_query.answer()
        return
    
    if not email_principal:
        await callback_query.answer("❌ Error: No tengo tu email. Usa /start para comenzar.")
        return
    
    if opcion == "personalizado":
        USER_STATES[user_id]["state"] = "waiting_suffix"
        await callback_query.message.edit_text(
            f"📧 Email principal: <code>{email_principal}</code>\n\n"
            "Por favor, envía el sufijo que deseas añadir (sin el signo +):",
            parse_mode=ParseMode.HTML
        )
        await callback_query.answer()
        return
    
    if opcion == "masivo":
        await callback_query.message.edit_text("⏳ Generando 1000 emails alternativos...")
        
        # Generar los emails
        emails = []
        for i in range(1, 1001):
            email = generar_email_alternativo(email_principal, "masivo", i)
            emails.append(email)
        
        # Guardar en archivo
        filename = f"emails_alternativos_{user_id}.txt"
        with open(filename, "w") as f:
            f.write("\n".join(emails))
        
        # Enviar archivo al usuario
        await client.send_document(
            chat_id=user_id,
            document=filename,
            caption=(
                f"📁 <b>1000 emails alternativos generados</b>\n\n"
                f"🔹 Email base: <code>{email_principal}</code>\n"
                f"🔹 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                "Puedes usar /start para generar más."
            ),
            parse_mode=ParseMode.HTML
        )
        
        # Mostrar algunos ejemplos
        sample = "\n".join(emails[:5])
        await callback_query.message.reply_text(
            f"🔍 <b>Algunos ejemplos:</b>\n\n<code>{sample}</code>\n\n"
            "Todos los emails han sido guardados en el archivo adjunto.",
            parse_mode=ParseMode.HTML,
            reply_markup=crear_menu_principal()
        )
        
        USER_STATES[user_id]["state"] = "main_menu"
        await callback_query.answer()
        return
    
    # Generar un solo email alternativo
    email_alternativo = generar_email_alternativo(email_principal, opcion)
    
    if email_alternativo:
        await callback_query.message.edit_text(
            f"✅ <b>Email alternativo generado:</b>\n\n<code>{email_alternativo}</code>\n\n"
            "Puedes copiarlo o generar otro.",
            parse_mode=ParseMode.HTML
        )
        await callback_query.message.reply_text(
            "¿Qué deseas hacer ahora?",
            reply_markup=crear_menu_principal()
        )
    else:
        await callback_query.message.edit_text("❌ Error al generar el email alternativo.")
    
    USER_STATES[user_id]["state"] = "main_menu"
    await callback_query.answer()

# --- INICIO DEL BOT ---
if __name__ == "__main__":
    print("🤖 Bot de generación de emails alternativos iniciado...")
    app.run()
