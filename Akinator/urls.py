from django.urls import path
from .views import *
urlpatterns = [
    path('', index_view, name='index'),
    path('index/preparation',preparation_view,name='prepare_page'),
    path('index/preparation/explanation/',explanation_view,name='explanation_page'),
    path('index/preparation/question/',question_view,name='question_page'),
    path('index/preparation/question/prediction',prediction_view,name='prediction_page'),
]  