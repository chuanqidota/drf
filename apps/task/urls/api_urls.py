from django.urls import path
from rest_framework.routers import DefaultRouter

from task.api.task import PeriodicTaskViewSet, CrontabViewSet, TaskListView

app_name = 'task'

router = DefaultRouter()
router.register('v1/task', PeriodicTaskViewSet, basename='task')
router.register('v1/cron', CrontabViewSet, basename='cron')
urlpatterns = [
    path('v1/task-list/', TaskListView.as_view(), name='task-list'),
]

urlpatterns += router.urls
