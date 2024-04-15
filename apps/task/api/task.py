from celery import current_app
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from rest_framework import status
from rest_framework.response import Response

from common.view.login_view import LoginModelViewSet, LoginApiView
from task.serializer import PeriodicTaskSerializer, CrontabScheduleSerializer


class PeriodicTaskViewSet(LoginModelViewSet):
    queryset = PeriodicTask.objects.all()
    serializer_class = PeriodicTaskSerializer
    search_fields = ("name", "task",)
    tags = ["任务"]
    operation_id = "任务"


class CrontabViewSet(LoginModelViewSet):
    filter_fields = ("minute", 'hour', "day_of_week", "day_of_month", "month_of_year")
    search_fields = filter_fields
    ordering_fields = ("minute",)
    queryset = CrontabSchedule.objects.all()
    serializer_class = CrontabScheduleSerializer
    tags = ['任务']
    panda_op_id = '时间'


class TaskListView(LoginApiView):
    tags = ['任务']
    panda_op_id = '任务列表'

    def get(self, request):
        current_app.loader.import_default_modules()
        tasks = list(sorted(name for name in current_app.tasks
                            if not name.startswith('celery.')))
        return Response(tasks, status=status.HTTP_200_OK)
