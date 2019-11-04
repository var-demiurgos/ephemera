from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from . import views
app_name='ephemeral'
urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('search/', views.Search.as_view(), name='search'),
    path('mylist/', views.MyList.as_view(), name='mylist'),
    path('mylist/edit/<int:pk>', views.EditMyList.as_view(), name='mylist_edit'),
    path('mylist/delete/<int:pk>', views.DeleteMyList.as_view(), name='mylist_delete'),
]