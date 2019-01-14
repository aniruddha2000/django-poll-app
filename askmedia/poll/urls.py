from django.urls import path
from . import views

app_name = 'poll'
urlpatterns = [
    path('', views.QuestionList.as_view(), name='index'),
    path('detail/<int:question_id>', views.DetailList.as_view(), name='detail'),
    path('result/<int:question_id>', views.ResultView.as_view(), name='results'),
    path('vote/<int:question_id>', views.VoteView.as_view(), name='vote'),
]