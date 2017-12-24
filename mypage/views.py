from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import View

from .forms import UserForm

from .external_http_requests import get_by_title, search_by_title
from .models import Movie, MovieNight
from .models import MovieBacklog


# Public profile
def public_profile(request, username):
    try:
        pubuser = User.objects.get(username=username)
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
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect('mypage:profile')
        else:
            # Return an 'invalid login' error message.
            return render(request, 'mypage/login_form.html', {
                'error_message': 'Username or password incorrect', })
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
            user.set_password(password)
            user.save()

            # returns User objects if credentials are correct
            user = authenticate(username=username, password=password)

            if user is not None:

                if user.is_active:
                    login(request, user)
                    return redirect('mypage:profile')

        return render(request, self.template_name, {'form': form})


# Create your views here.
def index(request):
    #all_albums = Album.objects.all()
    #return render(request, 'mypage/index.html', {'all_albums': all_albums})
    return render(request, 'mypage/index.html')


def profile(request):
    if request.user.is_authenticated:
        try:
            movienight_length = len(MovieNight.objects.filter(creator=request.user))
        except MovieNight.DoesNotExist:
            movienight_length = 0

        try:
            backlog_length = len(MovieBacklog.objects.filter(user=request.user))
        except MovieBacklog.DoesNotExist:
            backlog_length = 0

        return render(request, 'mypage/profile.html', {'backlogLength': backlog_length, 'movienightLength': movienight_length})
    else:
        return redirect('mypage:login')


def lists(request):
    if request.user.is_authenticated:
        return render(request, 'mypage/lists.html')
    else:
        return redirect('mypage:login')


def settings(request):
    return render(request, 'mypage/settings.html')


def movienight(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            title = request.POST.get('eventname', None)
            list_size = request.POST.get('nrmovies', None)
            print(title)
            print(list_size)
            print(request.user)
            new_movienight = MovieNight(title=title, list_size=list_size, creator=request.user)
            new_movienight.save()
            print(new_movienight.pk)
            return redirect(reverse('mypage:movienight_event', kwargs={"pk": new_movienight.pk}))
            # return redirect('/movienightevent/' + title + '/', {'movienight': new_movienight})
        else:
            # TODO: change creator to 'users' or somthing to include all
            active_movienights = MovieNight.objects.filter(creator=request.user)
            return render(request, 'mypage/movienight.html', {'a_movienights': active_movienights})
    else:
        return redirect('mypage:login')





def movienight_event(request, pk):
    selected_movienight = MovieNight.objects.get(pk=pk)
    return render(request, 'mypage/movienightevent.html', {'movienight': selected_movienight})


def backlog(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            if request.POST.get('singleResultBtn'):
                print('YES IT WAS PUSSHH')
                title_input = request.POST.get('titleinput', None)
                movie = get_by_title(title_input)
                # movies = search_by_title(title_input)
                # movies.pop(0)

                try:
                    m_backlog = MovieBacklog.objects.filter(user=request.user)
                except MovieBacklog.DoesNotExist:
                    m_backlog = None

                return render(request, 'mypage/backlog.html',
                              {'movie': movie, 'titleinput': title_input, 'm_backlog': m_backlog})
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
                              {'movies': movies, 'titleinput': title_input, 'm_backlog': m_backlog})
        else:
            # all_albums = Album.objects.all()
            # return render(request, 'mypage/index.html', {'all_albums': all_albums})
            try:
                m_backlog = MovieBacklog.objects.filter(user=request.user)
            except MovieBacklog.DoesNotExist:
                m_backlog = None
            return render(request, 'mypage/backlog.html', {'m_backlog': m_backlog})
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
    title_input = request.POST.get('title')
    result = get_by_title(title_input)
    print(result)
    movie = [result]
    return render(request, 'mypage/index.html', {'movie': movie, 'titleinput': title_input})


def get_movies(request):
    title_input = request.POST.get('title')
    movies = search_by_title(title_input)
    print('movies:')
    print(movies)
    try:
        m_backlog = MovieBacklog.objects.filter(user=request.user)
    except MovieBacklog.DoesNotExist:
        m_backlog = None

    return render(request, 'mypage/backlog.html', {'movies': movies, 'titleinput': title_input, 'm_backlog': m_backlog})
