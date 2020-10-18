from django.urls import path
from core.views import MainView
app_name = "core"
urlpatterns = [
    path("", MainView.as_view(), name="main")
]
