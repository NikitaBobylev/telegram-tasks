from typing import Iterable
from asgiref.sync import sync_to_async
from django.db.models import F

from core.apps.bot.models import Telegram_User
from core.apps.tasks.entity import Task as TaskEntity
from core.apps.tasks.models import Task


class TaskModelService:
    @sync_to_async
    def get_user_tasks(self, tg_user_id: str) -> Iterable[TaskEntity]:
        tasks = Task.objects.select_related(
            'user'
        ).filter(
            user__telegram_id=tg_user_id
        ).annotate(telegram_user_id=F('user__telegram_id')).order_by(
            'created_at'
        ).values('id', 'text', 'telegram_user_id')

        return (TaskEntity(**task) for task in tasks)

    def create_task(self, task_entity: TaskEntity) -> None:
        user, _ = Telegram_User.objects.get_or_create(
            telegram_id=task_entity.telegram_user_id
        )

        user.tasks.add(
            task_entity.text
        )
