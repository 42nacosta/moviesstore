from django.urls import path
from . import views

# location-feature-branch: Added two routes - trending map page and JSON API endpoint
urlpatterns = [
    path('', views.index, name='movies.index'),
    path('<int:id>/', views.show, name='movies.show'),
    path('petition/', views.petition, name='movies.petition'),
    path('petition/create/', views.create_petition, name='movies.create_petition'),
    path('petition/<int:petition_id>/upvote/', views.upvote_petition, name='movies.upvote_petition'),
    path('<int:id>/review/create/', views.create_review, name='movies.create_review'),
    path('<int:id>/review/<int:review_id>/edit/', views.edit_review, name='movies.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/', views.delete_review, name='movies.delete_review'),
    path('trending-map/', views.trending_map, name='movies.trending_map'),  # location-feature-branch
    path('api/trending-data/', views.trending_data_api, name='movies.trending_data_api'),  # location-feature-branch
]