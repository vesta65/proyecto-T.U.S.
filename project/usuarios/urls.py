from django.urls import path
from .views import registro, loginvista, home_view, logout_view
from panel.views import inicio
urlpatterns = [
    path('', home_view, name='home'),
    path('register/', registro, name='registerweb'),
    path('login/', loginvista, name='loginweb'),
    path('logout/', logout_view, name='logout'),
    path('inicio/', inicio, name='inicio'),
    
]
