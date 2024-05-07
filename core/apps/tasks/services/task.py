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

        return tuple(TaskEntity(**task) for task in tasks)

    @sync_to_async
    def create_task(self, task_entity: TaskEntity) -> Iterable[TaskEntity]:
        user, _ = Telegram_User.objects.prefetch_related('tasks').get_or_create(
            telegram_id=task_entity.telegram_user_id
        )

        Task.objects.create(
            text=task_entity.text,
            user_id=user.id
        )
        tasks = user.tasks.all().annotate(telegram_user_id=F('user__telegram_id')).order_by(
            'created_at'
        ).values('id', 'text', 'telegram_user_id')
        return tuple(TaskEntity(**task) for task in tasks)
