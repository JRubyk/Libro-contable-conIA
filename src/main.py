import asyncio
from telegram.ext import Application

from src.config import BOT_TOKEN
from src.storage.schema import init_db, seed_defaults
from src.bot.handlers import build_handlers
from src.bot.backlog import process_backlog

async def runner() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("Falta BOT_TOKEN. En PowerShell: $env:BOT_TOKEN='TU_TOKEN'")

    init_db()
    seed_defaults()

    app = Application.builder().token(BOT_TOKEN).build()
    for h in build_handlers():
        app.add_handler(h)

    # Inicializa y procesa backlog ANTES de quedar escuchando en vivo
    await app.initialize()

    processed = await process_backlog(app, limit=500)
    if processed:
        print(f"📥 Backlog procesado: {processed} updates")

    await app.start()
    print("🤖 Bot corriendo... Ctrl+C para detener")
    await app.updater.start_polling()

    # Mantener vivo
    await asyncio.Event().wait()


def main() -> None:
    asyncio.run(runner())


if __name__ == "__main__":
    main()
