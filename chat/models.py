from django.db import models


class ChatName(models.Model):
    id = models.AutoField(primary_key=True)
    chat_name = models.CharField(max_length=255, blank=False, unique=True)


class Messages(models.Model):
    id = models.AutoField(primary_key=True)
    chat_id = models.ForeignKey(ChatName, on_delete=models.CASCADE, verbose_name='chat id')
    message = models.CharField('chat message', max_length=255, blank=False)
    sender = models.CharField('message sender', max_length=255, blank=False)
    date_time = models.DateTimeField('date time', auto_now=True, unique=True)
