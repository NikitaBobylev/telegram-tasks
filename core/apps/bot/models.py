from django.db import models

from core.apps.common.models import TimedBaseModel


class Telegram_User(TimedBaseModel):
    telegram_id = models.CharField(
        max_length=100,
        verbose_name='Телеграм айди'
    )

    def __str__(self):
        return self.telegram_id

    class Meta:
        verbose_name = 'Телеграм пользователь'
        verbose_name_plural = 'Телеграм пользователи'
