from django.contrib import admin
from core.apps.bot.models import Telegram_User

@admin.register(Telegram_User)
class Telegram_User_Admin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id')
