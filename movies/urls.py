from django.urls import path
from django.contrib import admin
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='movies.index'),
    path('<int:id>/', views.show, name='movies.show'),
    path('petition/', views.petition, name='movies.petition'),
    path('petition/create/', views.create_petition, name='movies.create_petition'),
    path('petition/<int:petition_id>/upvote/', views.upvote_petition, name='movies.upvote_petition'),
    path('<int:id>/review/create/', views.create_review, name='movies.create_review'),
    path('<int:id>/review/<int:review_id>/edit/', views.edit_review, name='movies.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/', views.delete_review, name='movies.delete_review'),
]