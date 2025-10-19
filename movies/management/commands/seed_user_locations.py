# location-feature-branch: Seed command to populate UserLocation data for testing
# Assigns every user to one of 20 major US cities shared with the profile dropdown
# Idempotent - skips users who already have location data
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from movies.models import UserLocation
from accounts.forms import CITY_DATA


class Command(BaseCommand):
    help = 'Seeds user location data for testing the trending map feature'

    def handle(self, *args, **kwargs):
        # Use comprehensive 20-city catalog shared with profile form
        users = User.objects.all()

        if not users.exists():
            self.stdout.write(self.style.ERROR('No users found in database. Create users first.'))
            return

        created_count = 0
        skipped_count = 0

        # Assign each user to a city (modulo cycling ensures we don't run out of cities)
        for index, user in enumerate(users):
            if hasattr(user, 'userlocation'):
                self.stdout.write(self.style.WARNING(f'UserLocation already exists for {user.username}'))
                skipped_count += 1
                continue

            city_data = CITY_DATA[index % len(CITY_DATA)]

            UserLocation.objects.create(
                user=user,
                city=city_data['city'],
                state_province=city_data['state'],
                country=city_data['country'],
                latitude=city_data['latitude'],
                longitude=city_data['longitude']
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created location for {user.username} in {city_data["city"]}, {city_data["state"]}'
                )
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'\nSeed completed: {created_count} created, {skipped_count} skipped'))
