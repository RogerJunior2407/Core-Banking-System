
from django.urls import path
from .views import TransferListCreateView

urlpatterns = [
    path('', TransferListCreateView.as_view(), name='transfer-list-create'),
]