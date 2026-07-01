# ===============================================
# AI Telegram Bot with Groq Integration
# Author: Rpx
# GitHub: https://github.com/Rp-ics/Telegram-AI-Bot/
# License: MIT
# Multilingual support added (IT/EN/RU)
# Advanced notes management
# ===============================================

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from groq import Groq

# === GROQ CONFIGURATION ===
API_KEY = "" # USE GROQ API → https://console.groq.com/keys
models = [
    'gemma2-9b-it',              # Google
    'llama-3.3-70b-versatile',   # Meta
    'llama-3.1-8b-instant',      # Meta
    'llama3-70b-8192',           # Meta
    'llama3-8b-8192',            # Meta
    'whisper-large-v3',          # OpenAI
    'whisper-large-v3-turbo',    # OpenAI
    'distil-whisper-large-v3-en' # HuggingFace
]
DEFAULT_MODEL = models[3] # this one is default model → llama3-70b-8192

# === TELEGRAM BOT CONFIGURATION ===
TOKEN = "" # use telegram bot API → https://core.telegram.org/api

# === GLOBAL OBJECTS ===
groq_client = Groq(api_key=API_KEY)
user_history = {}  # {user_id: [{"role": "system", "content": "..."}, ...]}
user_model = {}    # {user_id: model_name}
user_notes = {}    # {user_id: ["note1", "note2", ...]}
user_lang = {}     # {user_id: "it"|"en"|"ru"}

# === TRANSLATIONS ===
translations = {
    "it": {
        "start": "👋 Ciao! Sono un assistente AI avanzato.\nUsa /help per vedere i comandi disponibili.",
        "help": """
🔧 Lista comandi disponibili:

/start → Avvia il bot  
/help → Mostra questa guida  
/model → Mostra i modelli disponibili  
/setmodel [num] → Imposta un modello  
/add_note [testo] → Salva una nota personale  
/notes → Visualizza le tue note  
/edit_note [num] [testo] → Modifica una nota  
/delete_note [num] → Cancella una nota  
/clear_notes → Cancella tutte le note  
/lang → Mostra le lingue disponibili  
/setlang [it/en/ru] → Cambia lingua  
📸 Invia una foto → Ricevi una risposta automatica  

Scrivi liberamente per parlare con l'AI!
""",
        "lang_list": "🌐 Lingue disponibili:\nit - Italiano\nen - English\nru - Русский",
        "lang_set": "✅ Lingua impostata su: `{}`",
        "invalid_lang": "❌ Usa: /setlang [it/en/ru]",
        "no_notes": "📋 Nessuna nota trovata.",
        "note_added": "📌 Nota aggiunta!",
        "note_edited": "✏️ Nota modificata!",
        "note_deleted": "🗑️ Nota eliminata!",
        "clear_notes": "🗑️ Tutte le note sono state cancellate.",
        "photo_received": "📸 Ho ricevuto una foto! Al momento non posso analizzarla.",
        "model_set": "✅ Modello impostato su: `{}`",
        "invalid_model": "⚠️ Numero modello non valido.",
        "notes_list": "📝 Le tue note:\n{}",
        "invalid_index": "❌ Indice non valido."
    },
    
    "en": {
        "start": "👋 Hi! I'm an advanced AI assistant.\nUse /help to see available commands.",
        "help": """
🔧 Available Commands:

/start → Start the bot  
/help → Show this guide  
/model → Show available models  
/setmodel [num] → Set a model  
/add_note [text] → Save a personal note  
/notes → View your notes  
/edit_note [num] [text] → Edit a note  
/delete_note [num] → Delete a note  
/clear_notes → Clear all notes  
/lang → Show available languages  
/setlang [it/en/ru] → Change language  
📸 Send a photo → Receive automatic reply  

Write freely to chat with the AI!
""",
        "lang_list": "🌐 Available Languages:\nit - Italian\nen - English\nru - Russian",
        "lang_set": "✅ Language set to: `{}`",
        "invalid_lang": "❌ Use: /setlang [it/en/ru]",
        "no_notes": "📋 No notes found.",
        "note_added": "📌 Note added!",
        "note_edited": "✏️ Note edited!",
        "note_deleted": "🗑️ Note deleted!",
        "clear_notes": "🗑️ All notes cleared.",
        "photo_received": "📸 Photo received! Can't analyze it yet.",
        "model_set": "✅ Model set to: `{}`",
        "invalid_model": "⚠️ Invalid model number.",
        "notes_list": "📝 Your notes:\n{}",
        "invalid_index": "❌ Invalid index."
    },
    "ru": {
        "start": "👋 Привет! Я продвинутый ИИ-ассистент.\nВведите /help, чтобы увидеть доступные команды.",
        "help": """
🔧 Доступные команды:

/start → Запустить бота  
/help → Показать справку  
/model → Показать доступные модели  
/setmodel [num] → Выбрать модель  
/add_note [текст] → Сохранить заметку  
/notes → Посмотреть заметки  
/edit_note [номер] [текст] → Изменить заметку  
/delete_note [номер] → Удалить заметку  
/clear_notes → Очистить все заметки  
/lang → Показать доступные языки  
/setlang [it/en/ru] → Сменить язык  
📸 Отправь фото → Получи ответ автоматически  

Пиши свободно, и я отвечу тебе!
""",
        "lang_list": "🌐 Доступные языки:\nit - Итальянский\nen - Английский\nru - Русский",
        "lang_set": "✅ Язык установлен на: `{}`",
        "invalid_lang": "❌ Используйте: /setlang [it/en/ru]",
        "no_notes": "📋 Заметок нет.",
        "note_added": "📌 Заметка добавлена!",
        "note_edited": "✏️ Заметка изменена!",
        "note_deleted": "🗑️ Заметка удалена!",
        "clear_notes": "🗑️ Все заметки удалены.",
        "photo_received": "📸 Фото получено! Анализ временно недоступен.",
        "model_set": "✅ Модель установлена: `{}`",
        "invalid_model": "⚠️ Неверный номер модели.",
        "notes_list": "📝 Ваши заметки:\n{}",
        "invalid_index": "❌ Неверный индекс."
    }
}

# === UTILITIES ===
def ask_groq(client, history, model):
    try:
        response = client.chat.completions.create(model=model, messages=history)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return translations["en"]["note_deleted"].get("default", f"Errore: {str(e)}")

# === COMMAND HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_lang:
        user_lang[user_id] = "en"  # Default language is English
    lang = user_lang[user_id]
    await update.message.reply_text(translations[lang]["start"])

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_lang.get(update.effective_user.id, "en")
    await update.message.reply_text(translations[lang]["help"])

async def show_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_lang.get(update.effective_user.id, "en")
    list_models = "\n".join(f"{i}. {model}" for i, model in enumerate(models))
    await update.message.reply_text(f"📦 Models:\n{list_models}")

async def set_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_lang.get(update.effective_user.id, "en")
    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text(translations[lang]["invalid_model"])
    index = int(context.args[0])
    if not 0 <= index < len(models):
        return await update.message.reply_text(translations[lang]["invalid_model"])
    user_id = update.effective_user.id
    selected_model = models[index]
    user_model[user_id] = selected_model
    await update.message.reply_text(translations[lang]["model_set"].format(selected_model))

async def add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_lang.get(update.effective_user.id, "en")
    if not context.args:
        return await update.message.reply_text(translations[lang]["note_added"])
    user_id = update.effective_user.id
    note = " ".join(context.args)
    user_notes.setdefault(user_id, []).append(note)
    await update.message.reply_text(translations[lang]["note_added"])

async def view_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_lang.get(update.effective_user.id, "en")
    user_id = update.effective_user.id
    notes = user_notes.get(user_id, [])
    if not notes:
        return await update.message.reply_text(translations[lang]["no_notes"])
    formatted_notes = "\n".join(f"{i+1}. {note}" for i, note in enumerate(notes))
    await update.message.reply_text(translations[lang]["notes_list"].format(formatted_notes))

async def edit_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_lang.get(update.effective_user.id, "en")
    if not context.args or len(context.args) < 2 or not context.args[0].isdigit():
        return await update.message.reply_text(
            translations[lang]["invalid_index"]
        )
    user_id = update.effective_user.id
    index = int(context.args[0]) - 1
    new_text = " ".join(context.args[1:])
    notes = user_notes.get(user_id, [])
    if not (0 <= index < len(notes)):
        return await update.message.reply_text(translations[lang]["invalid_index"])
    notes[index] = new_text
    await update.message.reply_text(translations[lang]["note_edited"])

async def delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_lang.get(update.effective_user.id, "en")
    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text(translations[lang]["invalid_index"])
    user_id = update.effective_user.id
    index = int(context.args[0]) - 1
    notes = user_notes.get(user_id, [])
    if not (0 <= index < len(notes)):
        return await update.message.reply_text(translations[lang]["invalid_index"])
    del notes[index]
    await update.message.reply_text(translations[lang]["note_deleted"])

async def clear_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_lang.get(update.effective_user.id, "en")
    user_id = update.effective_user.id
    user_notes[user_id] = []
    await update.message.reply_text(translations[lang]["clear_notes"])

async def show_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_lang.get(update.effective_user.id, "en")
    await update.message.reply_text(translations[lang]["lang_list"])

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_lang.get(update.effective_user.id, "en")
    if not context.args or context.args[0] not in ["it", "en", "ru"]:
        return await update.message.reply_text(translations[lang]["invalid_lang"])
    user_id = update.effective_user.id
    user_lang[user_id] = context.args[0]
    await update.message.reply_text(translations[context.args[0]]["lang_set"].format(context.args[0]))

# === MESSAGE HANDLERS ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text
    lang = user_lang.get(user_id, "en")

    if user_id not in user_history:
        user_history[user_id] = [{"role": "system", "content": "You are a helpful assistant."}]

    user_history[user_id].append({"role": "user", "content": message_text})

    if len(user_history[user_id]) > 20:
        user_history[user_id] = [user_history[user_id][0]] + user_history[user_id][-19:]

    current_model = user_model.get(user_id, DEFAULT_MODEL)
    reply = ask_groq(groq_client, user_history[user_id], current_model)
    user_history[user_id].append({"role": "assistant", "content": reply})
    await update.message.reply_text(reply)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_lang.get(update.effective_user.id, "en")
    await update.message.reply_text(translations[lang]["photo_received"])

# === MAIN ===
app = ApplicationBuilder().token(TOKEN).build()

# Register command handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("model", show_models))
app.add_handler(CommandHandler("setmodel", set_model))
app.add_handler(CommandHandler("addnote", add_note))
app.add_handler(CommandHandler("notes", view_notes))
app.add_handler(CommandHandler("editnote", edit_note))
app.add_handler(CommandHandler("deletenote", delete_note))
app.add_handler(CommandHandler("clearnotes", clear_notes))
app.add_handler(CommandHandler("lang", show_languages))
app.add_handler(CommandHandler("setlang", set_language))

# Register message handlers
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("running...")
app.run_polling()
