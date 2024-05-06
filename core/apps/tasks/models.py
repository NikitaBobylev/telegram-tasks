from core.apps.common.models import TimedBaseModel
from django.db import models


class Task(TimedBaseModel):
    text = models.TextField(
        verbose_name='Текст'
    )

    user = models.ForeignKey(
        to='bot.Telegram_User',
        related_name='tasks',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Таск'
        verbose_name_plural = 'Таски'
