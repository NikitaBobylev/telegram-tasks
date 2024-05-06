from django.core.management import BaseCommand
from django.conf import settings

import logging

from telegram import (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update, ForceReply

)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PollAnswerHandler,
    PollHandler,
    filters,

)

from core.apps.tasks.entity import Task as TaskEntity
from core.apps.tasks.services.task import TaskModelService

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def _chank_message(message: str) -> list[str]:
    max_message_lenght = 4096
    start_chank = 0
    end_chank = 4096
    res = []

    while message[start_chank: end_chank]:
        res.append(message[start_chank: end_chank])
        start_chank, end_chank = end_chank, end_chank + max_message_lenght

    return res


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")


async def get_tasks_for_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    task_service = TaskModelService()
    tasks = await task_service.get_user_tasks(
        tg_user_id=str(update.effective_user.id)
    )
    message = '\n'.join(f'{i}. {task.text}' for i, task in enumerate(tasks, start=1))

    for chanked_message in _chank_message(message):
        await update.message.reply_text(chanked_message)


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text('Напишите вашу задачу')


class Command(BaseCommand):
    help = 'bot'

    def handle(self, *args, **options):
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))

        application.add_handler(CommandHandler("tsk", get_tasks_for_user))
        application.add_handler(CommandHandler("add", add_task))
        application.add_handler(CommandHandler("delete", help_command))

        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, help_command))
        application.run_polling(allowed_updates=Update.ALL_TYPES)
