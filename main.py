import asyncio
import os
import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    JobQueue
)

# Import persistence functions, handlers, constants, and globals from script1.
from script1 import (
    load_data,
    save_data,
    get_today_str,
    extract_post_id,
    schedule_deletion,
    delete_later,
    split_message,
    create_url_buttons,
    create_custom_url_buttons,
    send_stored_message,
    start_cmd,
    betch,
    process_first_post,
    process_last_post,
    handle_parameter_link,
    check_required_channels,
    forward_to_channel,
    broadcast_handler,
    setting_cmd,
    export_data,
    admin_user_details,
    website_handler,
    button_handler,
    handle_website_update,
    subscription_listener,
    plan,
    pay_command,
    users_command,
    help_command,
    check_expired_subscriptions,
    list_links,
    FIRST_POST,
    ADMIN_ID,
    LAST_POST,
    SUBS_CHANNEL,
    LIMITED_SUBS_CHANNEL,
    UPGRADE_CHANNEL,
    BROADCAST_CHANNEL,
    pending_deletes  # Global list of pending delete tasks
)

# Import the long‑running web server function.
from web_server import start_web_server

# Set up logging.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load persistent data from MongoDB.
load_data()

async def run_bot() -> None:
    # Get bot token from the environment variable.
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

    # Build the application using ApplicationBuilder.
    app = ApplicationBuilder().token(bot_token).concurrent_updates(True).build()

    # Ensure a JobQueue is available.
    if app.job_queue is None:
        job_queue = JobQueue()
        await job_queue.start()
        app.job_queue = job_queue

    # Set up ConversationHandler for batch creation.
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('betch', betch)],
        states={
            FIRST_POST: [MessageHandler(filters.FORWARDED & filters.Chat(ADMIN_ID), process_first_post)],
            LAST_POST: [MessageHandler(filters.FORWARDED & filters.Chat(ADMIN_ID), process_last_post)]
        },
        fallbacks=[]
    )
    app.add_handler(conv_handler)

    # Register other command and message handlers.
    app.add_handler(CommandHandler('start', start_cmd))
    app.add_handler(CommandHandler('links', list_links))
    app.add_handler(CommandHandler('website', website_handler))
    app.add_handler(CommandHandler('setting', setting_cmd))
    app.add_handler(CommandHandler('export', export_data))
    app.add_handler(CommandHandler('plan', plan))
    app.add_handler(CommandHandler('pay', pay_command))
    app.add_handler(CommandHandler('users', users_command))
    app.add_handler(CommandHandler('user', admin_user_details))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_website_update))
    app.add_handler(MessageHandler(filters.ALL & filters.ChatType.PRIVATE, forward_to_channel), group=99)
    app.add_handler(MessageHandler(filters.Chat(SUBS_CHANNEL) |
                                   filters.Chat(LIMITED_SUBS_CHANNEL) |
                                   filters.Chat(UPGRADE_CHANNEL),
                                   subscription_listener))
    app.add_handler(MessageHandler(filters.Chat(BROADCAST_CHANNEL), broadcast_handler))

    # Schedule jobs on the job queue.
    async def reschedule_pending_deletions(context):
        for entry in list(pending_deletes):
            asyncio.create_task(schedule_deletion(context, entry))
    app.job_queue.run_once(reschedule_pending_deletions, when=1)
    app.job_queue.run_repeating(check_expired_subscriptions, interval=60, first=10)

    # Start the bot polling loop (this call blocks until the bot is stopped).
    await app.run_polling()

async def main() -> None:
    # Run both the bot and the web server concurrently.
    await asyncio.gather(
        run_bot(),
        start_web_server()
    )

if __name__ == '__main__':
    asyncio.run(main())
