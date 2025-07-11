from django.urls import path
from .views import *
urlpatterns = [
    path('', index_view, name='index'),
    path('index/preparation',preparation_view,name='prepare_page'),
    path('index/preparation/explanation/',explanation_view,name='explanation_page'),
    path('index/preparation/question/',question_view,name='question_page'),
    path('index/preparation/question/prediction/',result_view,name='result_page'),
    path('restart/', restart_view, name='restart'),
    path('index/preparation/question/resultrender',resultrender_view,name='render_page'),
]
