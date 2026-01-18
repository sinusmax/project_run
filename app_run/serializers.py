from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Run, AthleteInfo, Challenge, Position


# Задача №4. Создаем сериалайзер, который будем вкладывать в RunSerializer
class UserRunSerializer(serializers.ModelSerializer): # это будет вложенный сериалайзер для Run
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name']


class RunSerializer(serializers.ModelSerializer):
    # добавляем вложенный сериалайзер.
    # athlete_data - это требуемое имя поля для вывода,
    # а source='athlete' - это реальное поле модели Run
    athlete_data = UserRunSerializer(source='athlete', read_only = True)

    class Meta:
        model = Run
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField() # задаем вычисляемое полк

    # добавим еще одно вычисляемое поле для вывода кол-ва завершенных забегов атлета
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'date_joined',
            'username',
            'last_name',
            'first_name',
            'type', # этого поля изначально нет в модели, оно выше определено как вычисляемое
            'runs_finished', # еще одно вычисляемое поле
        ]

    def get_type(self, obj): # а это метод, который вычисляет значение поля 'type'
        if obj.is_staff or obj.is_superuser:
            return 'coach'
        else:
            return 'athlete'

    def get_runs_finished(self, obj): # метод для вычисления runs_finished
        # получается, в obj мы получим объект конкретного юзера
        # потом вытащим queryset со всеми завершенными забегами
        qs_runs = obj.run_set.filter(status = 'finished')
        # и вернем их количество
        return qs_runs.count()


# Задача №9. Создаем сериалайзер для модели AthleteInfo
class AthleteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AthleteInfo
        fields = ['goals', 'weight', 'user_id']


# Задача №10. Создаем сериалайзер для модели Challenge
class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ['full_name', 'athlete']


# Задача №11. Создаем сериалайзер для модели Position
class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['pk', 'run', 'latitude', 'longitude']

    def validate_latitude(self, value): # валидация поля (validate_<имя поля>)
        if value >= 90 or value <= -90:
            raise serializers.ValidationError('Широта должна быть в диапазоне между -90 и 90 градусов')
        return value

    def validate_longitude(self, value):
        if value >= 180 or value <= -180:
            raise serializers.ValidationError('Долгота должна быть в диапазоне между -180 и 180 градусов')
        return value

    def validate(self, data): # вызывается автоматом после валидации всех отдельных полей
        # попробуем прям здесь валидировать статус забега
        status_run = Run.objects.filter(pk = data['run']).first()
        if status_run != 'in progress':
            raise serializers.ValidationError('Забег должен быть в статусе "in progress"')
        return data

