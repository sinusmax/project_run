from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Run(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)

    # Задача №6. Добавляем в модель доп. поле 'status'
    STATUS_CHOICES = {
        'init': 'Забег инициализирован',
        'in_progress': 'Забег начат',
        'finished': 'Забег закончен',
    }
    status = models.CharField(choices=STATUS_CHOICES, max_length=50, default='init')