"""
URL configuration for SafeTag project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from SafeTagAPI.serializers.user_serializer import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer
from SafeTagAPI.views.practitioner_views import PractitionerAsyncViews, AddressViewSet, PractitionerViewSet
from SafeTagAPI.views.review_views import ReviewViewSet
from SafeTagAPI.views.user_views import UserCreateView


async def simple_async_view(request):
    print("Simple async view called")
    return JsonResponse({'message': 'Async view working'})



router = routers.DefaultRouter()
router.register(r'practitioner', PractitionerViewSet, basename='practitioner')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r"reviews", ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("admin", admin.site.urls),
    path('register/', UserCreateView.as_view(), name='register'),
    path('practitioner/async-list/', PractitionerAsyncViews.as_view(),name="practitioner_async_list"),
    path('api/token/', TokenObtainPairView.as_view(serializer_class=CustomTokenObtainPairSerializer), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(serializer_class=CustomTokenRefreshSerializer), name='token_refresh'),
]
urlpatterns += router.urls
