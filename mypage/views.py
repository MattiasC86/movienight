import json
from datetime import time, datetime

from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

import pytz
from django.contrib.auth.models import User
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import View

from .forms import UserForm

from .external_http_requests import get_by_title, search_by_title
from .models import Movie, MovieNight, MovieNightList, MovieBacklog, Vote, ChatMessage, BlogPost
from mnmessages.models import Message


# Base polling
def base_polling(request):
    unread_messages = Message.objects.filter(recipient=request.user, read=False, shown_to_recipient=True)
    return HttpResponse(len(unread_messages.all()))


# Public profile
def public_profile(request, username):
    try:
        pubuser = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        return HttpResponse('User not found!')

    try:
        movienight_length = len(MovieNight.objects.filter(creator=pubuser))
    except MovieNight.DoesNotExist:
        movienight_length = 0

    try:
        backlog_length = len(MovieBacklog.objects.filter(user=pubuser))
    except MovieBacklog.DoesNotExist:
        backlog_length = 0

    return render(request, 'mypage/public_profile.html', {'pubuser': pubuser, 'backlogLength': backlog_length, 'movienightLength': movienight_length})


# Movie details
def detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    return render(request, 'mypage/detail.html', {'movie': movie})


# Registration
def login_view(request):
    if request.method == "POST":
        print(request.POST['username'])
        print(request.POST['password'])
        username = request.POST['username']
        password = request.POST['password']

        try:
            username_exists = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            username_exists = None

        if not username_exists:
            print("USERNAME FREE")
            # Return an 'invalid login' error message.
            return render(request, 'mypage/login_form.html', {
                'error_message': 'Username or password incorrect', })
        else:
            print("USERNAME EXISTS")
            user = authenticate(request, username=username_exists.username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a success page.
                return redirect('mypage:profile')
    else:
        return render(request, 'mypage/login_form.html')


# Registration
class UserFormView(View):
    form_class = UserForm
    template_name = 'mypage/registration_form.html'

    # display blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # process form data
    def post(self, request):
        form = self.form_class(request.POST)

        # if valid form - save user locally, not db yet
        if form.is_valid():

            user = form.save(commit=False)

            # cleaned (normalized) data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                username_exists = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                username_exists = None

            if username_exists:
                messages.warning(request, 'Username already taken.')
            else:
                user.set_password(password)
                user.save()

                # returns User objects if credentials are correct
                user = authenticate(username=username, password=password)

                if user is not None:

                    if user.is_active:
                        login(request, user)
                        return redirect('mypage:profile')

        return render(request, self.template_name, {'form': form})


def index(request):
    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(recipient=request.user, read=False, shown_to_recipient=True)
        return render(request, 'mypage/index.html', {'unread': unread_messages})
    return render(request, 'mypage/index.html',)


def profile(request):
    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(recipient=request.user, read=False, shown_to_recipient=True)

        active_movienights = MovieNight.objects.filter(users=request.user, active=True)
        backlog = MovieBacklog.objects.filter(user=request.user)
        blog_posts = BlogPost.objects.filter(user=request.user).order_by('-date')

        if request.method == 'POST':
            if request.POST['action'] == 'post_blog':
                new_blog_post = BlogPost(user=request.user, title=request.POST['title'], content=request.POST['content'])
                new_blog_post.save()
                new_blog_post_json = {'pk': new_blog_post.pk, 'user': new_blog_post.user.username, 'title': new_blog_post.title,
                                      'content': new_blog_post.content, 'date': timezone.localtime(new_blog_post.date).strftime("%Y-%m-%d %H:%M")}
                return JsonResponse(new_blog_post_json, safe=False)
            if request.POST['action'] == 'delete_blog':
                blog_pk = request.POST['blog_post_pk']
                blog_to_delete = BlogPost.objects.get(pk=blog_pk)
                blog_to_delete.delete()
                return HttpResponse("postDeleted")
        return render(request, 'mypage/profile.html', {'backlog': backlog, 'active_movienights': active_movienights,
                                                       'unread': unread_messages, 'blog_posts': blog_posts})
    else:
        return redirect('mypage:login')


def lists(request):
    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(recipient=request.user, read=False, shown_to_recipient=True)
        return render(request, 'mypage/lists.html', {'unread': unread_messages})
    else:
        return redirect('mypage:login')


def settings(request):
    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(recipient=request.user, read=False, shown_to_recipient=True)
        return render(request, 'mypage/settings.html', {'unread': unread_messages})
    else:
        return redirect('mypage:login')


def movienight(request):
    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(recipient=request.user, read=False, shown_to_recipient=True)
        if request.method == 'POST':
            if request.POST.get('action'):
                if request.POST['action'] == 'make_inactive':
                    movienight_active_to_inactive = MovieNight.objects.get(pk=request.POST['movienight_pk'])
                    movienight_active_to_inactive.active = False
                    movienight_active_to_inactive.save()
            else:
                title = request.POST.get('eventname', None)
                list_size = request.POST.get('nrmovies', None)
                new_movienight = MovieNight(title=title, list_size=list_size, creator=request.user)
                new_movienight.save()
                new_movienight.users.add(request.user)
                return redirect(reverse('mypage:movienight_event', kwargs={"pk": new_movienight.pk}))
        else:
            created_movienights = MovieNight.objects.filter(creator=request.user).order_by('-creation_date')
            participant_movienights = MovieNight.objects.filter(users=request.user).exclude(creator=request.user).order_by('-creation_date')
            invited_movinights = MovieNight.objects.filter(invited_users=request.user).order_by('-creation_date')
            return render(request, 'mypage/movienight.html', {'created_movienights': created_movienights, 'participant_movienights': participant_movienights,
                                                              'invited_movinights': invited_movinights, 'unread': unread_messages})
    else:
        return redirect('mypage:login')


def movienight_event(request, pk):
    selected_movienight = MovieNight.objects.get(pk=pk)
    if request.user in selected_movienight.users.all() or request.user in selected_movienight.invited_users.all() \
            or request.user in selected_movienight.declined_users.all():
        unread_messages = Message.objects.filter(recipient=request.user, read=False, shown_to_recipient=True)
        saved_chat = ChatMessage.objects.filter(movienight=selected_movienight)
        try:
            movie_lists = MovieNightList.objects.filter(movienight=selected_movienight)
        except MovieNightList.DoesNotExist:
            movie_list = None

        for x in movie_lists:
            if not x.users_voted:
                x.users_voted = None

        if request.method == 'POST':
            # New chat message
            if request.POST['action'] == 'check':

                if int(request.POST['nr_messages']) == len(saved_chat.all()):
                    return HttpResponse("No change")
                else:
                    chat_messages_return = []
                    for c in saved_chat.all():
                        chat_messages_return.append({'author': c.author.username,
                                                     'timestamp': timezone.localtime(c.timestamp).strftime("%Y-%m-%d %H:%M"),
                                                     'text': c.text})
                    return JsonResponse(chat_messages_return, safe=False)

            elif request.POST['action'] == 'save_chat_message':
                print("AJAX HERE!")
                print(request.POST['text'])
                new_chat_message = ChatMessage(author=request.user, text=request.POST['text'], movienight=selected_movienight)
                new_chat_message.save()
                datevar = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M")
                print("DATETIME:")
                print(datevar)
                return JsonResponse(datevar, safe=False)
            # Event settings
            elif request.POST['action'] == 'settings':
                selected_movienight.description = request.POST.get('description')
                selected_movienight.string_date = request.POST.get('date')
                selected_movienight.string_time = request.POST.get('time')
                selected_movienight.date = selected_movienight.string_date + "T" + selected_movienight.string_time
                selected_movienight.location = request.POST.get('location')
                selected_movienight.decoration_url = request.POST.get('decoration')
                if selected_movienight.editable:
                    selected_movienight.list_size = request.POST.get('nrmovies')
                selected_movienight.save()
                return redirect('/movienightevent/' + pk)
            # TODO: Kolla om man verkligen ska köra filter, eller kanske ist get när bara ett av nåt ska hämtas
            # TODO: Bör skickas från typ "MovieNight" som sender, eller liknande
            # TODO: Skicka tillbaka meddelande om user är invited redan
            # Invite user
            elif request.POST['action'] == 'invite_user':
                selected_username = request.POST.get('user')
                try:
                    selected_user = User.objects.get(username__iexact=selected_username)
                except User.DoesNotExist:
                    selected_user = None

                if not selected_user:
                    return JsonResponse({'error': 'userDoesNotExist'})
                elif selected_user in selected_movienight.invited_users.all():
                    return JsonResponse({'error': 'userAlreadyInvited'})
                elif selected_user in selected_movienight.users.all():
                    return JsonResponse({'error': 'userAlreadyParticipant'})
                else:
                    # TODO: send back msg to user
                    selected_movienight.invited_users.add(selected_user)
                    selected_movienight.save()
                    new_message = Message(sender=request.user, recipient=selected_user, title="Invitation to MovieNight event!", message="You have been invited to the Movie event " +
                                      selected_movienight.title + "!\n\nGo to your MovieNight page to see the event. Inside the event you can learn more about it " +
                                                                  "and either accept or reject the invitation.")
                    new_message.save()
                return redirect('/movienightevent/' + pk)
            elif request.POST['action'] == 'accept_invitation':
                if request.user in selected_movienight.invited_users.all():
                    selected_movienight.invited_users.remove(request.user)
                if request.user not in selected_movienight.users.all():
                    selected_movienight.users.add(request.user)
                return HttpResponse("Invited user is now a participant")
            elif request.POST['action'] == 'decline_invitation':
                if request.user in selected_movienight.invited_users.all():
                    selected_movienight.invited_users.remove(request.user)
                if request.user not in selected_movienight.declined_users.all():
                    selected_movienight.declined_users.add(request.user)
                return HttpResponse("Invited user declined invitation")
            elif request.POST['action'] == 'result_viewable':
                selected_movienight.result_viewable = True
                selected_movienight.save()
                return HttpResponse("Result btn is now viewable")
            elif request.POST['action'] == 'change_phase':
                if selected_movienight.current_phase < 3:
                    selected_movienight.current_phase = selected_movienight.current_phase + 1
                    selected_movienight.save()
                    return HttpResponse(selected_movienight.current_phase)
                else:
                    return HttpResponse(3)
            elif request.POST['action'] == 'nominations_done':
                try:
                    list = MovieNightList.objects.get(user=request.user, movienight=selected_movienight)
                except MovieNightList.DoesNotExist:
                    list = None

                if list:
                    list.marked_done = True
                    list.save()
                    return HttpResponse("Success")
                else:
                    return HttpResponse("Fail")
            elif request.POST['action'] == 'nominations_undone':
                try:
                    list = MovieNightList.objects.get(user=request.user, movienight=selected_movienight)
                except MovieNightList.DoesNotExist:
                    list = None

                if list:
                    list.marked_done = False
                    list.save()
                    return HttpResponse("Success")
                else:
                    return HttpResponse("Fail")

        usable_date = timezone.localtime(selected_movienight.date).strftime("%Y-%m-%d")
        usable_time = timezone.localtime(selected_movienight.date).strftime("%H:%M")
        display_date = usable_date + " " + usable_time
        return render(request, 'mypage/movienightevent.html', {'movienight': selected_movienight,
                                                               "usable_date": usable_date, "usable_time": usable_time,
                                                               "display_date": display_date, "movie_lists": movie_lists,
                                                               "chat": saved_chat, 'unread': unread_messages})


def movienight_event_get_vote_results(request, pk):
    selected_movienight = MovieNight.objects.get(pk=pk)
    all_votes = Vote.objects.filter(movie_night=selected_movienight)
    all_lists = MovieNightList.objects.filter(movienight=selected_movienight)

    nominated_movies = []
    sorted_points = []
    final_results = []

    # Make list with pairs of movie/nominated_by
    for l in all_lists.all():
        for m in l.movies.all():
            nominated_movies.append({'nominated_by': l.user.username, 'movie': m})

    # Make list with all points for movies
    x_counter = 0
    for nom_mov in nominated_movies:
        sorted_points.append(0)
        for vote in all_votes.all():
            if vote.movie.pk == nom_mov['movie'].pk:
                sorted_points[x_counter] += vote.points
        x_counter += 1

    # Create final results list to be returned
    i = 0
    for x in nominated_movies:
        movie = nominated_movies[i]['movie']
        movie_json = {'pk': movie.pk, 'title': movie.title,'year': movie.release_year, 'director': movie.director,
                     'plot': movie.plot, 'poster':movie.poster}
        final_results.append({'movie': movie_json, 'points': sorted_points[i], 'nominated_by': x['nominated_by']})
        i += 1

    final_results.sort(key=lambda x: x['points'], reverse=True)

    if request.user not in selected_movienight.result_viewed_users.all():
        selected_movienight.result_viewed_users.add(request.user)
        selected_movienight.save()

    return JsonResponse(final_results, safe=False)


def delete_movienight(request, pk):
    selected_movienight = MovieNight.objects.get(pk=pk)
    selected_movienight.delete()
    return redirect('mypage:movienight')


def movienight_list(request, pk, username):
    selected_movienight = MovieNight.objects.get(pk=pk)
    if request.user in selected_movienight.users.all():
        if username == request.user.username:
            unread_messages = Message.objects.filter(recipient=request.user, read=False, shown_to_recipient=True)
            selected_user = User.objects.get(username=username)
            try:
                movie_list = MovieNightList.objects.get(user=selected_user, movienight=selected_movienight)
            except MovieNightList.DoesNotExist:
                movie_list = None

            if request.method == 'POST':
                if request.POST.get('movieToDelete'):
                    moviepk = request.POST.get('movieToDelete', None)
                    movielistpk = request.POST.get('movieList', None)

                    try:
                        movie = Movie.objects.get(pk=moviepk)
                    except Movie.DoesNotExist:
                        movie = None

                    try:
                        movie_list = MovieNightList.objects.get(pk=movielistpk)
                    except MovieNightList.DoesNotExist:
                        movie_list = None

                    if movie:
                        print('movie exists. Will now delete.')
                        movie_list.movies.remove(movie)
                    # TODO else: Send msg back to client

            print("RENDER MOVIENIGHT LIST")
            return render(request, 'mypage/movienight_list.html', {'movienight': selected_movienight, 'user': selected_user,
                                                                   'list': movie_list, 'unread': unread_messages})


def movienight_list_vote(request, pk, username):
    selected_movienight = MovieNight.objects.get(pk=pk)
    if request.user in selected_movienight.users.all():
        unread_messages = Message.objects.filter(recipient=request.user, read=False, shown_to_recipient=True)
        selected_user = User.objects.get(username=username)
        try:
            movie_list = MovieNightList.objects.get(user=selected_user, movienight=selected_movienight)
        except MovieNightList.DoesNotExist:
            movie_list = None
        try:
            previous_vote = Vote.objects.filter(movie_list=movie_list, user=request.user)
        except Vote.DoesNotExist:
            previous_vote = None

        print(previous_vote)

        if request.method == 'POST':
            print("vote submit!")


            # TODO: Send msg back to user
            if previous_vote:
                print("Already voted!")
            else:
                data = json.loads(request.POST.get('votes'))
                print("------DATA-------------")
                print(data)
                for x in data:
                    selected_movie = Movie.objects.get(pk=x['movie_pk'])
                    new_vote = Vote(user=request.user, movie_night=selected_movienight, movie_list=movie_list,
                                    movie=selected_movie, points=x['points'])
                    new_vote.save()
                    print("New vote saved!")
                    movie_list.save()
                movie_list.users_voted.add(request.user)
                movie_list.editable = False
                movie_list.save()
                return HttpResponse("saved")

        return render(request, 'mypage/movie_list_voting.html', {'movienight': selected_movienight,
                                                                 'list_user': selected_user, 'list': movie_list,
                                                                 'voted': previous_vote, 'unread': unread_messages})


def movienight_list_add(request, pk, username):
    selected_movienight = MovieNight.objects.get(pk=pk)
    if request.user in selected_movienight.users.all():
        title = request.POST.get('title', None)
        director = request.POST.get('director', None)
        year = request.POST.get('year', None)
        poster = request.POST.get('poster', None)
        plot = request.POST.get('plot', None)

        print("title:" + title)

        # If movie is not in database, save it
        try:
            movie_duplicate = Movie.objects.get(title=title, release_year=year)
        except Movie.DoesNotExist:
            movie_duplicate = None

        if not movie_duplicate:
            # save as new movie
            movie_new = Movie(title=title, director=director, release_year=year, poster=poster, plot=plot)
            movie_new.save()

        # Check if user already has a movielist
        try:
            movie_list = MovieNightList.objects.get(user=request.user, movienight=selected_movienight)
        except MovieNightList.DoesNotExist:
            movie_list = None

        new_list_movie = Movie.objects.get(title=title)

        # If movie list does not exist, create one
        if movie_list:
            # If movie not in list, add it
            if new_list_movie in movie_list.movies.all():
                print("Movie already in list!")
            else:
                movie_list.movies.add(new_list_movie)
                movie_list.save()
        else:
            movie_list = MovieNightList(user=request.user, movienight=selected_movienight)
            movie_list.save()
            movie_list.movies.add(new_list_movie)
            selected_movienight.editable = False
            selected_movienight.save()

        # TODO: Should sent json back to not having to reload page
        #return JsonResponse(new_list_movie, safe=False)
        return render(request, 'mypage/movienight_list.html',
                      {'movienight': selected_movienight, 'user': request.user, 'list': movie_list})


def backlog(request):
    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(recipient=request.user, read=False, shown_to_recipient=True)
        if request.method == 'POST':
            if request.POST.get('singleResultBtn'):
                title_input = request.POST.get('titleinput', None)
                movie = get_by_title(title_input)
                # movies = search_by_title(title_input)
                # movies.pop(0)

                try:
                    m_backlog = MovieBacklog.objects.filter(user=request.user)
                except MovieBacklog.DoesNotExist:
                    m_backlog = None

                return render(request, 'mypage/backlog.html',
                              {'movie': movie, 'titleinput': title_input, 'm_backlog': m_backlog, 'unread': unread_messages})
            elif request.POST.get('multipleResultsBtn'):
                title_input = request.POST.get('titleinput', None)
                movies = search_by_title(title_input)
                # movies = search_by_title(title_input)
                # movies.pop(0)

                try:
                    m_backlog = MovieBacklog.objects.filter(user=request.user)
                except MovieBacklog.DoesNotExist:
                    m_backlog = None

                return render(request, 'mypage/backlog.html',
                              {'movies': movies, 'titleinput': title_input, 'm_backlog': m_backlog, 'unread': unread_messages})
        else:
            # all_albums = Album.objects.all()
            # return render(request, 'mypage/index.html', {'all_albums': all_albums})
            try:
                m_backlog = MovieBacklog.objects.filter(user=request.user)
            except MovieBacklog.DoesNotExist:
                m_backlog = None
            return render(request, 'mypage/backlog.html', {'m_backlog': m_backlog, 'unread': unread_messages})
    else:
        return redirect('mypage:login')


def add_backlog(request):
    title = request.POST.get('title', None)
    director = request.POST.get('director', None)
    year = request.POST.get('year', None)
    poster = request.POST.get('poster', None)
    plot = request.POST.get('plot', None)

    try:
        movie_duplicate = Movie.objects.get(title=title, release_year=year)
    except Movie.DoesNotExist:
        movie_duplicate = None

    if movie_duplicate:
        # save duplicate to backlog
        print('duplicate found!')
    else:
        # save as new movie
        movie_new = Movie(title=title, director=director, release_year=year, poster=poster, plot=plot)
        movie_new.save()

    backlog_new = MovieBacklog(movie=Movie.objects.get(title=title), user=request.user)

    try:
        backlog_duplicate = MovieBacklog.objects.get(movie=backlog_new.movie, user=backlog_new.user)
    except MovieBacklog.DoesNotExist:
        backlog_duplicate = None

    if backlog_duplicate:
        print('backlog already exists!')
    else:
        backlog_new.save()
    # TODO: Send httprequest back, this one isnt rendering anyway, ajax is in template file...
    return render(request, 'mypage/movienight.html')
    # return redirect(request, '/mycouch/lists/')


def add_backlog_multichoice(request):
    title_search = request.POST.get('title', None)

    movie = get_by_title(title_search)

    title = movie['Title']
    director = movie['Director']
    year = movie['Year']
    poster = movie['Poster']
    plot = movie['Plot']

    try:
        movie_duplicate = Movie.objects.get(title=title, release_year=year)
    except Movie.DoesNotExist:
        movie_duplicate = None

    if movie_duplicate:
        # save duplicate to backlog
        print('duplicate found!')
    else:
        # save as new movie
        movie_new = Movie(title=title, director=director, release_year=year, poster=poster, plot=plot)
        movie_new.save()

    backlog_new = MovieBacklog(movie=Movie.objects.get(title=title), user=request.user)

    try:
        backlog_duplicate = MovieBacklog.objects.get(movie=backlog_new.movie, user=backlog_new.user)
    except MovieBacklog.DoesNotExist:
        backlog_duplicate = None

    if backlog_duplicate:
        print('backlog already exists!')
    else:
        backlog_new.save()
    # TODO: Send httprequest back, this one isnt rendering anyway, ajax is in template file...
    return render(request, 'mypage/movienight.html')
    # return redirect(request, '/mycouch/lists/')


def delete_backlog(request):
    moviepk = request.POST.get('backlogToDelete', None)

    try:
        movie = Movie.objects.get(pk=moviepk)
    except Movie.DoesNotExist:
        movie = None

    if movie:
        print('movie exists. Will now delete.')
        MovieBacklog.objects.get(movie=movie, user=request.user).delete()
    # TODO else: Send msg back to client

    # TODO: Send httprequest back, this one isnt rendering anyway, ajax is in template file...
    return render(request, 'mypage/movienight.html')


# TODO make GET instead
def submit(request):
    title_input = request.POST.get('titleinput', None)
    movie = get_by_title(title_input)
    # movies = search_by_title(title_input)
    # movies.pop(0)
    return render(request, 'mypage/mycouch.html', {'movie': movie, 'titleinput': title_input})


def get_movie(request):
    print("views.get_movie() running")
    title_input = request.POST.get('title')
    result = get_by_title(title_input)
    print(result)
    return JsonResponse(result)


def save_movie(request):
    user = request.user
    if request.POST['type'] == 'backlog':
        print('Save moviepk ' + request.POST['contextual']['movie_pk'] + ' to ' + user.username + ' backlog')


def get_movie2(request):
    title = request.POST.get('title')
    year = request.POST.get('year')

    # Check if movie is in db
    try:
        movie_in_db = Movie.objects.get(title=title, release_year=year)
    except Movie.DoesNotExist:
        movie_in_db = None

    # If in db, return it
    if movie_in_db:
        return_movie = {'title': movie_in_db.title, 'year': movie_in_db.release_year, 'director': movie_in_db.director,
                    'poster': movie_in_db.poster, 'plot': movie_in_db.plot, 'pk': movie_in_db.pk}
    else:
        return_movie = get_by_title(title)

    return JsonResponse(return_movie)


def save_movie_to_list(request):
    option = request.POST.get('option')
    movie_pk = request.POST.get('movie_pk')
    try:
        movie = Movie.objects.get(pk=movie_pk)
    except Movie.DoesNotExist:
        movie = None
        print("--- MOVIE WITH PK " + movie_pk + " DOES NOT EXIST IN DATABASE ---")

        if option == 'backlog':
            print("Save to backlog")
            new_moviebacklog = MovieBacklog(movie=movie, user=request.user)
            new_moviebacklog.save()

        elif option == 'movienight_list':
            print("Save to movienight_list")
            movienight_pk = request.POST.get('movienight_pk')
            movienight = MovieNight.objects.get(pk=movienight_pk)

            # Check movienight list does not exist, create one
            try:
                movienight_list = MovieNightList.objects.get(user=request.user, movienight=movienight)
            except MovieNightList.DoesNotExist:
                movienight_list = None
            if not movienight_list:
                movienight_list = MovieNightList(user=request.user, movienight=movienight)
                movienight_list.save()

            movienight_list.movies.add(movie)
            movienight_list.save()

        elif option == 'custom_list':
            print("Save to custom list")
            # TODO: custom_list_pk = request.POST.get('custom_list_pk')
            # TODO: movie_pks = request.post.GET('movie_pks')
            # TODO: movies = []
            # TODO: for pk in movie_pks:
            # TODO:     movies.push(Movie.objects.get(pk=pk)
            # TODO: try:
            # TODO:     custom_list = CustomList.objects.get(pk=custom_list_pk)
            # TODO: except custom_list.DoesNotExist:
            # TODO:     custom_list = None
            # TODO: for m in movies:
            # TODO:     custom_list.movies.add(m)
            # TODO:
            # TODO: DELETE ABOVE IF ADDING JUST ONE MOVIE TO CREATED LIST. DO BELOW INSTEAD
            # TODO: custom_list_pk = request.POST.get('custom_list_pk')
            # TODO: custom_list = CustomList.objects.get(pk=custom_list_pk)
            # TODO: custom_list.movies.add(movie)
            # TODO: custom_list.save()


def get_movies(request):
    title_input = request.POST.get('title')
    movies = search_by_title(title_input)

    return JsonResponse(movies, safe=False)
