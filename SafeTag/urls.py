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
from rest_framework import routers

from SafeTagAPI.views.practitioner_views import PractitionerAsyncViews, PractitionerAddressViewSet, PractitionerViewSet
from SafeTagAPI.views.review_views import ReviewViewSet
from SafeTagAPI.views.user_views import UserViewSet

from django.http import JsonResponse
from django.urls import path

async def simple_async_view(request):
    print("Simple async view called")
    return JsonResponse({'message': 'Async view working'})



router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r'practitioner', PractitionerViewSet, basename='practitioner')
router.register(r'addresses', PractitionerAddressViewSet, basename='address')
router.register(r"reviews", ReviewViewSet)

urlpatterns = [
    path("admin", admin.site.urls),
    path('simple-async/', simple_async_view),
    path('practitioner/async-list/', PractitionerAsyncViews.as_view())
]
urlpatterns += router.urls
