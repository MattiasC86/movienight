from django.conf.urls import url
from . import views
from django.contrib.auth.views import logout


urlpatterns = [
    # /
    url(r'^$', views.index, name='index'),

    # user account management
    url(r'^register/$', views.UserFormView.as_view(), name='register'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
    url(r'^settings/$', views.settings, name='settings'),

    # public user profile
    url(r'^user/(?P<username>[-\w]+)/$', views.public_profile, name='public_profile'),

    # /mycouch/backlog
    url(r'^mycouch/backlog/$', views.backlog, name='backlog'),
    url(r'^mycouch/backlog/add/$', views.add_backlog, name='add_backlog'),
    url(r'^mycouch/[0-9]+/delete/$', views.delete_backlog, name='delete_backlog'),

    # moviesearches, TODO dont use them all!
    url(r'addmultichoice/', views.add_backlog_multichoice),
    url(r'getmovies/', views.get_movies),
    url(r'^search', views.submit, name='submit'),
    url(r'^getmovie/', views.get_movie),

    # movie/<movie_pk>
    url(r'^mycouch/(?P<movie_pk>[0-9]+)/$', views.detail, name='detail'),

    # /mycouch || profile
    url(r'^mycouch/profile/$', views.profile, name='profile'),

    # /mycouch/lists
    url(r'^mycouch/lists/', views.lists, name='lists'),

    # /mycouch/movienight
    url(r'^mycouch/movienight/', views.movienight, name='movienight'),
    url(r'^movienightevent/(?P<pk>[0-9]+)/$', views.movienight_event, name='movienight_event'),
    url(r'^movienightevent/(?P<pk>[0-9]+)/settings/$', views.movienight_event, name='movienight_event_settings'),
    url(r'^movienightevent/(?P<pk>[0-9]+)/inviteuser/$', views.movienight_event, name='movienight_event_invite_user'),
    url(r'^movienightevent/(?P<pk>[0-9]+)/get_vote_results/$', views.movienight_event_get_vote_results, name='movienight_event_get_vote_results'),
    # delete movienight
    url(r'^movienightevent/(?P<pk>[0-9]+)/delete$', views.delete_movienight, name='delete_movienight'),

    # movielist
    url(r'^movienightevent/(?P<pk>[0-9]+)/(?P<username>\w+)/$', views.movienight_list, name='movienight_list'),
    url(r'^movienightevent/(?P<pk>[0-9]+)/(?P<username>\w+)/get_movie/$', views.get_movie, name='get_movie'),
    # vote page
    url(r'^movienightevent/(?P<pk>[0-9]+)/vote/(?P<username>\w+)/$', views.movienight_list_vote, name='movienight_list_vote'),
    url(r'^movienightevent/(?P<pk>[0-9]+)/vote/(?P<username>\w+)/savevote/$', views.movienight_list_vote, name='movienight_list_vote'),


    url(r'^movienightevent/(?P<pk>[0-9]+)/(?P<username>\w+)/add/$', views.movienight_list_add, name='add_list'),
    url(r'^movienightevent/(?P<pk>[0-9]+)/(?P<username>\w+)/delete/$', views.delete_backlog, name='delete_backlog'),




    # /music/<album_id>/
    # url(r'^(?P<album_id>[0-9]+)/$', views.detail, name='detail'),

    # /music/<album_id>/favorite/
    # url(r'^(?P<album_id>[0-9]+)/favorite/$', views.favorite, name='favorite'),

]