from django.urls import path
from .views import AnalyzeTasksView, SuggestTasksView
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='tasks/index.html'), name='index'),
    path('api/tasks/analyze/', AnalyzeTasksView.as_view(), name='analyze_tasks'),
    path('api/tasks/suggest/', SuggestTasksView.as_view(), name='suggest_tasks'),
]
