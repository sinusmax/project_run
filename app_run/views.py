from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view # чтобы использовать декоратор
from rest_framework.filters import SearchFilter
from rest_framework.response import Response # чтобы использовать Response от DRF
from django.conf import settings # чтобы использовать переменные из settings
from rest_framework.views import APIView

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
    queryset = Run.objects.all().select_related('athlete')
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

    # Задание №5. Добавляем поиск по имени и фамилии
    # /api/users/?search=Иван
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name']

    def get_queryset(self):
        qs = self.queryset # наверное, можно и не вводить лишнюю переменную qs, а использовать прям queryset
        type_user = self.request.query_params.get('type', None) # .query_params. вместо .GET.
        if type_user == 'coach':
            qs = qs.filter(is_staff = True)
        if type_user == 'athlete':
            qs = qs.filter(is_staff = False)
        return qs


# Задача №6. Меняем статус с помощью вьюхи на базе APIView
class StartRunAPIView(APIView):
    def post(self,request, run_id): # Вначале делал GET, но проверка ругается, что надо POST
        # run = Run.objects.get(id=run_id)
        run = get_object_or_404(Run, id=run_id)
        if run.status != 'init':
            return Response({'message': 'Забег уже идет или закончен'}, status=status.HTTP_400_BAD_REQUEST)
        run.status = 'in_progress'
        run.save()
        serializer = RunSerializer(run)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StopRunAPIView(APIView):
    def post(self,request, run_id): # Вначале делал GET, но проверка ругается, что надо POST
        run = get_object_or_404(Run, id=run_id)
        if run.status != 'in_progress':
            return Response({'message': 'Забег еще не начат или уже закончен'}, status=status.HTTP_400_BAD_REQUEST)
        run.status = 'finished'
        run.save()
        serializer = RunSerializer(run)
        return Response(serializer.data, status=status.HTTP_200_OK)