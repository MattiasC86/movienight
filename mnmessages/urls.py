from django.conf.urls import url
from . import views
from django.contrib.auth.views import logout


urlpatterns = [
    # /messages
    url(r'^$', views.messages, name='messages'),
    url(r'^sendmessage/$', views.send_message, name='send_message'),
    url(r'^readmessage/$', views.read_message, name='read_message'),

]