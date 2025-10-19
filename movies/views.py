from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Petition, Vote
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    movie = review.movie
    if movie.reviewCount == 1:
        movie.rating = 0
    elif review.rating != 0:
        movie.rating = ((float(movie.rating) * movie.reviewCount) - float(review.rating)) / (movie.reviewCount - 1)
    movie.reviewCount -= 1
    movie.save()
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '': 
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def create_review(request, id):
    if request.method == 'POST' and (request.POST['comment'] != '' or request.POST['rating'] != 1):
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.rating = request.POST['rating']
        review.movie = movie
        if review.rating != 0:
            movie.rating = (float(review.rating) + float(movie.rating)) / (movie.reviewCount + 1)
        movie.reviewCount += 1
        review.user = request.user
        movie.save()
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie =  Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html',
                  {'template_data': template_data})

def petition(request):
    template_data = {}
    template_data['petition'] = Petition.objects.all()
    return render(request, 'movies/petition.html', {'template_data' : template_data})

@login_required
def create_petition(request):
    if request.method == 'POST' and request.POST['content'] != '':
        petition = Petition()
        petition.content = request.POST['content']
        petition.user = request.user
        petition.save()
        return redirect('movies.petition')
    else:
        return redirect('movies.petition')

@login_required
def upvote_petition(request, petition_id):
    petition = get_object_or_404(Petition, id=petition_id)
    vote, created = Vote.objects.get_or_create(
        petition=petition,
        user=request.user,
        defaults={'value': Vote.UPVOTE}
    )
    if not created:
        # If user already downvoted, switch to upvote; if already upvoted, do nothing
        if vote.value == Vote.UPVOTE:
            vote.value = 0
            vote.save()
        else:
            vote.value = Vote.UPVOTE
            vote.save()
    # Recalculate petition.rating from votes
    agg = petition.votes.aggregate(total=Sum('value'))['total']
    petition.rating = agg or 0
    petition.save()
    return redirect('movies.petition')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')