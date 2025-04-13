import os
import re
import cv2
import pytesseract
import asyncio
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

# Configurar Tesseract OCR (ajusta la ruta si es necesario)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Token del bot de Telegram
TOKEN = "XXXXXXXX"

# Diccionario para almacenar los datos temporales de actualización
user_data = {}

# Definir estados para la conversación
WAITING_FOR_UPDATE = 1

# Ruta de la imagen base
IMAGE_PATH = r'C:\Users\yerhe\Downloads\Lous-Kitchen-Python\formato-images\formato-br00014.jpg'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("¡Hola! Envíame una imagen con el formato o escribe ACT-BR00014 para actualizar valores.")

async def handle_text(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    text = update.message.text
    
    if text == "ACT-BR00014":
        await context.bot.send_message(chat_id=user_id, text="Por favor, envíame los datos de actualización en este formato:\n\nF300107-11.54\nF500612-11\nZ100720-11\nWATER-1111")
        return WAITING_FOR_UPDATE
    return ConversationHandler.END

async def receive_update(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    text = update.message.text
    
    if user_id not in user_data:
        user_data[user_id] = {}
    
    updates = {}
    for line in text.split('\n'):
        match = re.match(r"(\w+)-(\d+\.?\d*)", line)
        if match:
            key, value = match.groups()
            updates[key] = value
    
    user_data[user_id]['updates'] = updates
    await context.bot.send_message(chat_id=user_id, text=f"Datos recibidos. Procesando la imagen...")
    print(f"[DEBUG] Datos de actualización almacenados: {updates}")
    
    await process_and_send_image(user_id, context)
    return ConversationHandler.END

async def process_and_send_image(user_id, context: CallbackContext):
    if not os.path.exists(IMAGE_PATH):
        await context.bot.send_message(chat_id=user_id, text="No se encontró la imagen base para actualizar.")
        return
    
    print(f"[DEBUG] Cargando imagen desde: {IMAGE_PATH}")
    image = Image.open(IMAGE_PATH)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 40)  # Fuente más grande para claridad
    
    updates = user_data.get(user_id, {}).get('updates', {})
    updated = False
    y_offset = 100  # Posición inicial para escribir los datos en la imagen
    
    for key, value in updates.items():
        draw.text((50, y_offset), f"{key}: {value}", fill=(255, 0, 0), font=font)  # Texto en rojo para resaltar cambios
        y_offset += 50  # Espaciado entre líneas
        updated = True
    
    if not updated:
        await context.bot.send_message(chat_id=user_id, text="No se encontraron valores para actualizar en la imagen.")
        return
    
    new_file_path = f"C:\\Users\\yerhe\\Downloads\\Lous-Kitchen-Python\\formato-images\\updated_{user_id}.jpg"
    image.save(new_file_path)
    
    print(f"[DEBUG] Imagen procesada y guardada en {new_file_path}")
    
    with open(new_file_path, 'rb') as photo_file:
        await context.bot.send_photo(chat_id=user_id, photo=photo_file)
    
    await context.bot.send_message(chat_id=user_id, text="Imagen actualizada enviada.")
    os.remove(new_file_path)
    del user_data[user_id]

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
        states={
            WAITING_FOR_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_update)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
    
    if not asyncio.get_event_loop().is_running():
        asyncio.run(application.run_polling())
    else:
        application.run_polling()

if __name__ == '__main__':
    main()




    #--------------------------------------------------------------------------------------------------------------------


# 📌 Función para manejar el mensaje "OPTIONS"
@bot.message_handler(func=lambda message: message.text.strip().upper() == "OPTIONS")
def send_options(message):
    """ Muestra las opciones principales al usuario con botones. """
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Pumping"), KeyboardButton("Tumbling"), KeyboardButton("Brine"))
    
    bot.send_message(message.chat.id, "🔘 *Selecciona una opción:*", reply_markup=markup, parse_mode="MarkdownV2")

# 📌 Función para manejar selecciones de opciones
@bot.message_handler(func=lambda message: message.text.strip().upper() in ["PUMPING", "TUMBLING", "BRINE"])
def handle_main_selection(message):
    """ Muestra subopciones según la opción seleccionada. """
    selection = message.text.strip().upper()

    if selection == "PUMPING":
        suboptions = ["High Pressure", "Low Pressure", "Automated"]
    elif selection == "TUMBLING":
        suboptions = ["Slow Tumbling", "Fast Tumbling", "Marination"]
    elif selection == "BRINE":
        suboptions = ["Standard Brine", "High Concentration", "Low Concentration"]

    # Crear botones con las subopciones
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for sub in suboptions:
        markup.add(KeyboardButton(sub))

    bot.send_message(message.chat.id, f"🔘 *Seleccionaste {selection}.*\nAhora elige una subcategoría:", reply_markup=markup, parse_mode="MarkdownV2")


#--------------------------------------------------------------------------------------------------------------------


🛠 *Welcome to Lous Bot.*\nClick To Option:
