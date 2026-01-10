from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import api_view # чтобы использовать декоратор
from rest_framework.response import Response # чтобы использовать Response от DRF
from django.conf import settings # чтобы использовать переменные из settings

from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializer


# Create your views here.
@api_view(['GET'])
def company_details_view(request):
    """
    Задание №1.
    Отдаем название, слоган и адрес компании по АПИ
    для отображения на главной странице сайта
    (запрос в данном случае идет на /api/company_details)
    """
    details = {
        'company_name': settings.MY_COMPANY_NAME, # используются переменные из settings/base.py
        'slogan': settings.MY_COMPANY_SLOGAN,
        'contacts': settings.MY_COMPANY_ADDRESS,
    }
    return Response(details)


class RunViewSet(viewsets.ModelViewSet):
    """
    Задание №2.
    Отдаем по АПИ список забегов с комментариями.
    Данные берем из БД.
    Забег добавляется POST-запросом с указанием коммента и id-атлета
    (запрос в данном случае идет на /api/runs)
    В задании №4 во вложенном сериализаторе добавлен вывод поля "athlete_data"
    """
    queryset = Run.objects.all()
    serializer_class = RunSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Задание №3.
    Отдаем по АПИ список атлетов и тренеров с фильтрацией по типу пользователя.
    Суперадмина не отдаем никогда.
    Фильтр передается в GET-запросе в параметре ?type=coach|athlete
    (запрос в данном случае идет на /api/users)
    """
    queryset = User.objects.filter(is_superuser = False) # сразу исключаем суперадминов
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = self.queryset # наверное, можно и не вводить лишнюю переменную qs, а использовать прям queryset
        type_user = self.request.query_params.get('type', None) # .query_params. вместо .GET.
        if type_user == 'coach':
            qs = qs.filter(is_staff = True)
        if type_user == 'athlete':
            qs = qs.filter(is_staff = False)
        return qs

