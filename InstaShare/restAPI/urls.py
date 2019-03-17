from django.urls import path, include
from django.conf.urls import url, include
from rest_framework import routers
from restAPI import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'restAPI'

urlpatterns = [
    #Authentication and User Handling
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('register/', views.CreateUserView.as_view()),
    path('uploadContact/', views.ContactView.as_view()),
]
