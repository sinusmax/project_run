from django.contrib import admin
from app_run.models import Run, AthleteInfo, Challenge, Position

# Register your models here.
admin.site.register(Run)
admin.site.register([AthleteInfo, Challenge, Position])
