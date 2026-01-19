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

    # Задача №12. Добавляем в модель поле 'distance'
    distance = models.FloatField(blank=True, null=True)


# для задачи №9 создаем модель AthleteInfo (OneToOne к User)
class AthleteInfo(models.Model):
    goals = models.TextField(blank=True, null=True)
    weight = models.PositiveSmallIntegerField(blank=True, null=True) # поле должно быть > 0 и < 900
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)


# для задачи №10 создаем модель Challenge
class Challenge(models.Model):
    full_name = models.CharField(max_length=100) # это будет название челленджа
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)


# для задачи №11 создаем модель Position
class Position(models.Model):
    latitude = models.DecimalField(max_digits=6, decimal_places=4) # широта (от -90.0 до +90.0 градусов вкл.)
    longitude = models.DecimalField(max_digits=7, decimal_places=4) # долгота (от -180.0 до +180.0 градусов вкл.)
    created_at = models.DateTimeField(auto_now_add=True) # кажется, что это тоже должно пригодиться
    run = models.ForeignKey(Run, on_delete=models.CASCADE)

