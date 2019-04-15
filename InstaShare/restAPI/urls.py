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
<<<<<<< HEAD
    path('uploadContactMobile/', views.ContactView64.as_view()),
    path('uploadContactMobile/<int:id>/', views.ContactViewMobile.as_view()),
    path('singlephoto/', views.RekognitionView.as_view()),
    path('singlephotoMobile/', views.RekognitionViewMobile.as_view()),
=======
    path('uploadContact64/', views.ContactView64.as_view()),
    path('uploadContact64/<int:id>', views.ContactView64.as_view()),
    path('demo/', views.RekognitionView.as_view()),
    path('demo64/', views.RekognitionViewB64.as_view()),
>>>>>>> 72bb569628ef2cb76b91b0f0d26fb3e645229ae6
    path('batchupload/', views.BatchUploadView.as_view()),
    path('batchuploadMobile/', views.BatchUploadViewMobile.as_view()),
]
