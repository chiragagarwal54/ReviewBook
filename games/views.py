from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from games.models import GameReview, Game
from games.forms import GiveReviewForm, UpdateReviewForm
from accounts.models import Account
from base import views
from movies.models import MovieReview, Movie
from games.models import GameReview, Game
from series.models import EpisodeReview, Series, Episode
def give_game_review(request, game_id):

    context = {}

    user = request.user
    game = get_object_or_404(Game, id=game_id)
    if not user.is_authenticated:
        return redirect('accounts:must_authenticate')

    review = GameReview.objects.filter(game_id=game_id, author=request.user)
    if len(review)==0:
        form = GiveReviewForm(request.POST or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.game = game
            obj.author = user
            obj.save()
            form = GiveReviewForm()
            return redirect('games:review_detail', obj.slug)

        context['form']=form

        return render(request, 'give_game_review.html', context)
    else:
        return redirect('games:review_detail', review[0].slug)

def select_game(request):
    games = Game.objects.all()
    context ={'games':games}

    return render(request, 'select_game.html', context)

def index(request):
    game_list= Game.objects.order_by('-name')
    context = {'game_list':game_list}
    return render(request,'games/gamelist.html',context)

def details(request,game_id):
    game= get_object_or_404(Game,pk=game_id)
    return render(request,'games/details.html',{'game':game})

def review_detail(request, slug):
    context = {}
    review = get_object_or_404(GameReview, slug=slug)
    context['review']=review

    return render(request, 'games/review_detail.html', context)

def edit_review(request, slug):

    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect('accounts:must_authenticate')

    review = get_object_or_404(GameReview, slug=slug)
    if request.POST:
        form = UpdateReviewForm(request.POST or None, instance=review)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.update()
            context['success_message'] = "Updated"
            review = obj
            query = ""
            if request.GET:
              query = request.GET['q']

            context = get_queryset(str(query))
            context['query'] = str(query)
            return render(request,'home.html', context)
    form = UpdateReviewForm(
            initial = {
                    "title": review.title,
                    "body": review.body,
                    "rating": review.rating,
                } 
    )

    context['form'] = form
    return render(request, 'games/edit_review.html', context)

def get_queryset(query=None):
    queryset = {}
    queries = query.split(" ")
    if query:
        for q in queries:
            movies = Movie.objects.filter(
                    Q(name__icontains=q),
            ).distinct()
            games = Game.objects.filter(
                    Q(name__icontains=q),
            ).distinct()
            series = Series.objects.filter(
                    Q(name__icontains=q),
            ).distinct()
            episodes = Episode.objects.filter(
                    Q(episode_name__icontains=q),
            ).distinct()
            users = Account.objects.filter(
                    Q(first_name__icontains=q),
            ).distinct()

            queryset['movies'] = movies
            queryset['games'] = games
            queryset['series'] = series
            queryset['episodes'] = episodes
            queryset['users'] = users
    else:
        moviereview = MovieReview.objects.order_by('-date_published')
        gamereview = GameReview.objects.order_by('-date_published')
        episodereview = EpisodeReview.objects.order_by('-date_published')

        queryset['moviereview'] = moviereview
        queryset['gamereview'] = gamereview
        queryset['episodereview'] = episodereview

    return queryset
