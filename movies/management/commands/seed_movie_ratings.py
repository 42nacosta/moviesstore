# location-feature-branch: Populates review ratings and generates supplemental feedback
import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from movies.models import Movie, Review


class Command(BaseCommand):
    help = 'Assigns random ratings to reviews and generates additional review data for demos'

    SAMPLE_COMMENTS = [
        'Loved the plot twists!',
        'Solid watch with great performances.',
        'Fun, but the pacing felt slow in parts.',
        'A must-see for fans of the genre.',
        'Beautiful cinematography and soundtrack.',
        'The ending left me wanting more.',
        'Not my favorite, but still enjoyable.',
        'Outstanding cast and direction.',
        'Could watch this again and again.',
        'Good concept, execution was just okay.',
    ]

    def handle(self, *args, **options):
        users = list(User.objects.all())
        movies = list(Movie.objects.all())

        if not users or not movies:
            self.stdout.write(self.style.ERROR('Users and movies are required before seeding reviews.'))
            return

        self._assign_existing_ratings()
        self._create_additional_reviews(movies, users)

        self.stdout.write(self.style.SUCCESS('Review ratings seeding completed successfully.'))

    def _assign_existing_ratings(self):
        updated = 0
        for review in Review.objects.all():
            review.rating = random.randint(1, 5)
            review.save(update_fields=['rating'])
            updated += 1
        self.stdout.write(self.style.SUCCESS(f'Updated ratings for {updated} existing reviews.'))

    def _create_additional_reviews(self, movies, users):
        created_reviews = 0
        for movie in movies:
            existing_user_ids = set(
                Review.objects.filter(movie=movie).values_list('user_id', flat=True)
            )
            target_new_reviews = random.randint(1, 3)

            random.shuffle(users)
            new_reviews = 0

            for user in users:
                if new_reviews >= target_new_reviews:
                    break

                if user.id in existing_user_ids:
                    continue

                Review.objects.create(
                    movie=movie,
                    user=user,
                    comment=random.choice(self.SAMPLE_COMMENTS),
                    rating=random.randint(1, 5),
                )
                new_reviews += 1
                created_reviews += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created_reviews} new reviews.'))
