from typing import Iterable

from django.core.management import BaseCommand
from django.conf import settings

import logging

from telegram import (
    ReplyKeyboardRemove,
    Update

)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,

)

from core.apps.tasks.entity import Task as TaskEntity
from core.apps.tasks.services.task import TaskModelService

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

ADD_TASK = 0


def _chank_message(message: str) -> list[str]:
    max_message_lenght = 4096
    start_chank = 0
    end_chank = 4096
    res = []

    while message[start_chank: end_chank]:
        res.append(message[start_chank: end_chank])
        start_chank, end_chank = end_chank, end_chank + max_message_lenght

    return res


async def _generate_tasks_responses(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                    tasks: Iterable[TaskEntity]) -> None:
    message = '\n'.join(f'{i}. {task.text}' for i, task in enumerate(tasks, start=1))

    for chanked_message in _chank_message(message):
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=chanked_message,
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = ("Этот бот предназначен для создания ваших задач."
        "\n\nИспользуте: \n/tsk - для получения задач  \n/add - для создания задач")

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=message,
    )
    return ConversationHandler.END


async def get_tasks_for_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    task_service = TaskModelService()
    tasks: Iterable[TaskEntity] = await task_service.get_user_tasks(
        tg_user_id=str(update.effective_user.id)
    )

    if not tasks:
        await update.effective_message.reply_text('У вас пока нет задач')
        return
    await _generate_tasks_responses(update=update, context=context, tasks=tasks)
    return ConversationHandler.END


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.effective_message.reply_text(
        'Напишите вашу задачу. \nЧтобы отменить используйте /cancel'
    )
    return ADD_TASK


async def create_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    task_service = TaskModelService()
    task = TaskEntity(
        telegram_user_id=str(update.effective_user.id),
        text=update.effective_message.text,
    )
    new_tasks: Iterable[TaskEntity] = await task_service.create_task(
        task_entity=task
    )

    await _generate_tasks_responses(update=update, context=context, tasks=new_tasks)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.effective_message.reply_text(
        "Используте: \n/tsk - для получения задач  \n/add - для создания задач"
    )

    return ConversationHandler.END


class Command(BaseCommand):
    help = 'bot'

    def handle(self, *args, **options):
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

        start_handler = CommandHandler("start", help_command)

        help_handler = CommandHandler("help", help_command)

        tsk_hadler = CommandHandler("tsk", get_tasks_for_user)

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("add", add_task)],
            states={
                ADD_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_task)]
            },
            fallbacks=[CommandHandler("cancel", cancel), tsk_hadler, help_handler, start_handler],
        )

        application.add_handler(conv_handler)
        application.add_handler(start_handler)
        application.add_handler(help_handler)
        application.add_handler(tsk_hadler)

        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, help_command))
        application.run_polling(allowed_updates=Update.ALL_TYPES)
