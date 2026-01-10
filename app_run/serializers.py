from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Run


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
    type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type']

    def get_type(self, obj):
        if obj.is_staff or obj.is_superuser:
            return 'coach'
        else:
            return 'athlete'

