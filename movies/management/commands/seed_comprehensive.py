# location-feature-branch: Orchestrates full dataset seeding for demos
import base64

from django.core.files.base import ContentFile
from django.core.management import BaseCommand, call_command
from django.utils.text import slugify

from django.contrib.auth.models import User

from movies.models import Movie, Review


class Command(BaseCommand):
    help = 'Runs all seed commands to populate a comprehensive demo dataset'

    PLACEHOLDER_IMAGE = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PV7UYwAAAABJRU5ErkJggg=='
    )

    SAMPLE_MOVIES = [
        ('Skyline Pursuit', 18, 'A daring chase across international skylines.'),
        ('Echoes of Tomorrow', 22, 'Time-travel thriller with a twist.'),
        ('Neon District', 16, 'Cyberpunk noir mystery.'),
        ('Harbor Lights', 14, 'Heartfelt drama set on a coastal town.'),
        ('Quantum Hearts', 20, 'Romance meets parallel universes.'),
        ('Shadows Within', 21, 'Psychological thriller with unexpected turns.'),
        ('Aurora Rising', 19, 'Inspirational story about resilience.'),
        ('Galactic Relay', 17, 'Space adventure with ragtag pilots.'),
        ('Velocity Drift', 15, 'Underground racing with high stakes.'),
        ('Crimson Orchard', 18, 'Historical drama with intrigue.'),
        ('Silent Frequencies', 16, 'Musician uncovers secret frequencies.'),
        ('Midnight Canopy', 14, 'Survival tale set in the rainforest.'),
        ('Iron Vanguard', 23, 'Epic wartime saga of unlikely heroes.'),
        ('Arcade Dreams', 12, 'Coming-of-age story in a retro arcade.'),
        ('Sapphire Tides', 20, 'Mystery beneath a luxurious resort.'),
    ]

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Starting comprehensive seed...'))

        call_command('seed_test_users')
        call_command('seed_user_locations')

        self._ensure_movie_catalog()

        call_command('seed_test_orders')
        call_command('seed_movie_ratings')

        self._print_summary()
        self.stdout.write(self.style.SUCCESS('\nComprehensive seed completed successfully.'))

    def _ensure_movie_catalog(self):
        existing_movies = {movie.name for movie in Movie.objects.all()}
        created = 0

        for name, price, description in self.SAMPLE_MOVIES:
            if name in existing_movies:
                continue

            image_name = f'{slugify(name)}.png'
            image_content = ContentFile(self.PLACEHOLDER_IMAGE, name=image_name)
            movie = Movie(
                name=name,
                price=price,
                description=description,
            )
            movie.image.save(image_name, image_content, save=False)
            movie.save()
            created += 1
            self.stdout.write(self.style.SUCCESS(f'Added movie: {name}'))

        self.stdout.write(
            self.style.HTTP_INFO(f'Movie catalog ready with {Movie.objects.count()} entries ({created} new).')
        )

    def _print_summary(self):
        total_users = User.objects.count()
        total_movies = Movie.objects.count()
        total_reviews = Review.objects.count()

        self.stdout.write(
            self.style.NOTICE(
                f'Total users: {total_users} | Movies: {total_movies} | Reviews: {total_reviews}'
            )
        )
