from django.contrib import admin
from django.urls import path,include

from rest_framework import routers
from django.http import JsonResponse # Apenas para verificar e manter online com bot
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import UserView,RegisterView,LoginView,OngViewset
from denuncias.views import DenunciasViewset
from adocoes.views import AnimalViewset,AdocaoViewset

router = routers.DefaultRouter()
router.register('users', UserView,'usuarios')
router.register('denuncias', DenunciasViewset, basename='denuncias')
router.register('ongs', OngViewset, basename='ongs')
router.register('animais', AnimalViewset, basename='animais')
router.register('adocoes', AdocaoViewset, basename='adocoes')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterView.as_view(), name='Registro'),
    path('login/',LoginView.as_view(), name='Login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='Refresh'),
    path('health/', lambda request: JsonResponse({ # Apenas para verificar e manter online com bot
    'status': 'online'
        })),
    path('', include(router.urls)),
]
