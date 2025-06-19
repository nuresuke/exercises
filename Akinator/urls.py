from django.urls import path
from .views import *
urlpatterns = [
    path('', index_view, name='index'),
    path('index/',preparation_view,name='prepare_page'),
    path('index/preparation',explanation_view,name='explanation_page'),
]