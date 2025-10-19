from collections import OrderedDict
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Petition, Vote, UserLocation
from django.db.models import Sum, Avg, Count
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from cart.models import Item
# Create your views here.
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
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
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
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

# location-feature-branch: Trending map page view - renders template with Google Maps API key
def trending_map(request):
    template_data = {
        'title': 'Local Popularity Map',
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'movies/trending_map.html', {'template_data': template_data})

# location-feature-branch: JSON API returning trending movie data aggregated by location
# Groups purchases by city/state and attaches movie stats including average review rating
def trending_data_api(request):
    # Pre-calculate review statistics per movie for rating display
    review_stats = (
        Review.objects
        .values('movie_id')
        .annotate(avg_rating=Avg('rating'), total_reviews=Count('rating'))
    )
    review_lookup = {
        entry['movie_id']: entry for entry in review_stats
    }

    # Aggregate purchase counts per movie within each city
    city_movie_data = (
        Item.objects
        .select_related('order__user__userlocation', 'movie')
        .filter(order__user__userlocation__isnull=False)
        .values(
            'order__user__userlocation__latitude',
            'order__user__userlocation__longitude',
            'order__user__userlocation__city',
            'order__user__userlocation__state_province',
            'order__user__userlocation__country',
            'movie__name',
            'movie__id',
            'movie__price'
        )
        .annotate(purchase_count=Sum('quantity'))
        .order_by(
            'order__user__userlocation__city',
            '-purchase_count',
            'movie__name'
        )
    )

    # OrderedDict preserves query ordering for deterministic movie lists
    city_lookup = OrderedDict()
    for item in city_movie_data:
        city_name = item['order__user__userlocation__city']
        latitude = item['order__user__userlocation__latitude']
        longitude = item['order__user__userlocation__longitude']

        # Skip entries without essential location metadata
        if not city_name or latitude is None or longitude is None:
            continue

        state = item['order__user__userlocation__state_province']
        country = item['order__user__userlocation__country']
        city_key = (city_name, state, country)

        if city_key not in city_lookup:
            city_lookup[city_key] = {
                'city': city_name,
                'state': state,
                'country': country,
                'lat': float(latitude),
                'lng': float(longitude),
                'movies': []
            }

        review_data = review_lookup.get(item['movie__id'], {'avg_rating': None, 'total_reviews': 0})
        avg_rating = review_data.get('avg_rating')
        total_reviews = review_data.get('total_reviews', 0)

        city_lookup[city_key]['movies'].append({
            'id': item['movie__id'],
            'name': item['movie__name'],
            'purchase_count': item['purchase_count'],
            'price': item['movie__price'],
            'avg_rating': float(avg_rating) if avg_rating is not None else 0.0,
            'total_reviews': total_reviews,
        })

    return JsonResponse(list(city_lookup.values()), safe=False)
