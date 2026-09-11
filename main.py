import os

from dotenv import load_dotenv
from telegram import Update         # type: ignore
from telegram.ext import (          # type: ignore
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from graph.graph import customer_graph


load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "Hello! How can I help you?"
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = update.message.text

    print(f"Customer: {message}")

    result = customer_graph.invoke(
    {
        "message": message,  # type: ignore
        
    },
    config={
        "configurable": {
            "thread_id": str(update.effective_user.id)
        }
    }
)

    print("LangGraph result:", result)

    intent = result.get("intent", "GENERAL")

    print(f"Intent: {intent}")

    response = result.get(
        "response",
        "Sorry, I couldn't generate a response."
    )

    await update.message.reply_text(response)


def main():

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()