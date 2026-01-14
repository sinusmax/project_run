from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import api_view # чтобы использовать декоратор
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response # чтобы использовать Response от DRF
from django.conf import settings # чтобы использовать переменные из settings
from rest_framework.views import APIView

from app_run.models import Run, AthleteInfo, Challenge
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer, ChallengeSerializer


# Задача №7. Создаем класс для пагинации
class RunAndUserPagination(PageNumberPagination):
    # page_size = 10 # Количество объектов на странице по умолчанию (не обязательный параметр)
    page_size_query_param = 'size' # Разрешаем изменять количество объектов через query параметр size в url
    # max_page_size = 100 # Ограничиваем максимальное количество объектов на странице

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
    В задании №7 добавляем фильтрацию, сортировку и пагинацию
    """
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer

    # класс для фильтрации - DjangoFilterBackend (должен быть импортирован)
    # класс для сортировки - DjangoFilterBackend (должен быть импортирован)
    # filter_backends - это атрибут класса ModelViewSet
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    # Поля, по которым будет происходить фильтрация
    filterset_fields = ['status', 'athlete']
    # Поля, по которым будет происходить сортировка (/api/runs/?ordering=created_at. Или -created_at)
    ordering_fields = ['created_at']

    # устанавливаем класс пагинации
    pagination_class = RunAndUserPagination

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Задание №3.
    Отдаем по АПИ список атлетов и тренеров с фильтрацией по типу пользователя.
    Суперадмина не отдаем никогда.
    Фильтр передается в GET-запросе в параметре ?type=coach|athlete
    (запрос в данном случае идет на /api/users)
    В задании №7 добавляем сортировку и пагинацию
    """
    queryset = User.objects.filter(is_superuser = False) # сразу исключаем суперадминов
    serializer_class = UserSerializer

    # Задание №5. Добавляем поиск по имени и фамилии
    # /api/users/?search=Иван
    filter_backends = [SearchFilter, OrderingFilter] #сюда добавил фильтр для сортировки
    search_fields = ['first_name', 'last_name']

    def get_queryset(self):
        qs = self.queryset # наверное, можно и не вводить лишнюю переменную qs, а использовать прям queryset
        type_user = self.request.query_params.get('type', None) # .query_params. вместо .GET.
        if type_user == 'coach':
            qs = qs.filter(is_staff = True)
        if type_user == 'athlete':
            qs = qs.filter(is_staff = False)
        return qs

    # добавляем сортировку по полю date_joined (/api/users/?ordering=data_joined. Или -data_joined)
    ordering_fields = ['date_joined']

    # устанавливаем класс пагинации
    pagination_class = RunAndUserPagination


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

        # Задача №10. Считаем кол-во завершенных забегов для челленджа
        finished_runs_count = Run.objects.filter(athlete=run.athlete, status='finished').count()
        # print(f'Это был {finished_runs_count}-й забег')
        if finished_runs_count == 10:
            # и создаем запись в модели Challenge
            Challenge.objects.create(full_name=f'Сделай {finished_runs_count} забегов!', athlete=run.athlete)
            # print(f'Бинго! Челлендж завершен! ({finished_runs_count}-й забег)')

        serializer = RunSerializer(run)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Задача №9. Вьюха для отдачи инфы из AthleteInfo (на базе APIView)
class AthleteInfoAPIView(APIView):

    def get(self,request,user_id):
        # есть ли вообще юзер с таким id в модели User ?
        user = get_object_or_404(User, id=user_id)

        athlete_info, created = AthleteInfo.objects.get_or_create(user_id=user)
        serializer = AthleteInfoSerializer(athlete_info)

        return Response(serializer.data, status=status.HTTP_200_OK)
        # на случай, если надо отдавать разные статусы отдавались
        # if created:
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # else:
        #     return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self,request,user_id):
        user = get_object_or_404(User, id=user_id)
        weight_is_not_valid = not request.data['weight'].isdigit() \
                          or int(request.data['weight']) >= 900 \
                          or int(request.data['weight']) < 1
        if weight_is_not_valid:
            return Response({'message': 'Указан недопустимый вес'}, status=status.HTTP_400_BAD_REQUEST)
        athlete_info, created = AthleteInfo.objects.update_or_create(
            user_id=user,
            defaults={
                'goals': request.data['goals'],
                'weight': request.data['weight'],
            }
        )
        serializer = AthleteInfoSerializer(athlete_info)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Задача №10. Вьюха для возврата данных из модели Challenge. Пробуем через APIView
class ChallengeAPIView(APIView):

    def get(self,request):
        athlete = self.request.query_params.get('athlete', None) # чтобы можно было отдать по конкретному атлету
        challenges = Challenge.objects.all()

        if athlete:
            challenges = challenges.filter(athlete=athlete)

        serializer = ChallengeSerializer(challenges, many=True) # many=True!!! Без этого была ошибка!
        return Response(serializer.data, status=status.HTTP_200_OK)


