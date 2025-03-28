import pytest
from django.urls import reverse, resolve
from django.test import Client
from SafeTagAPI.views.practitioner_views import PractitionerAsyncViews, PractitionerViewSet, AddressViewSet
from SafeTagAPI.views.review_views import ReviewViewSet
from SafeTagAPI.views.user_views import UserCreateView

# SafeTag/test_urls.py

@pytest.fixture
def client():
    return Client()

@pytest.mark.django_db
def test_admin_url(client):
    url = reverse('admin:index')
    assert resolve(url).func.__name__ == 'index'


@pytest.mark.django_db
def test_user_viewset_url(client):
    url = reverse('register')
    assert resolve(url).func.cls == UserCreateView

@pytest.mark.django_db
def test_practitioner_address_viewset_url(client):
    url = reverse('address-list')
    assert resolve(url).func.cls == AddressViewSet

@pytest.mark.django_db
def test_review_viewset_url(client):
    url = reverse('review-list')
    assert resolve(url).func.cls == ReviewViewSet

@pytest.mark.django_db
def test_practitioner_async_list_response(client):
    response = client.get(reverse('practitioners'))
    assert response.status_code == 200