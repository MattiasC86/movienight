from django.conf.urls import url
from . import views
from django.contrib.auth.views import logout


urlpatterns = [
    # /messages
    url(r'^$', views.messages, name='messages'),

]