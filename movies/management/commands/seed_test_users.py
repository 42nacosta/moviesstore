# location-feature-branch: Creates a cohort of test users for demo scenarios
# Ensures predictable accounts exist for seeding locations and orders
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Creates deterministic test users for demos (test_user_1 ... test_user_30)'

    def handle(self, *args, **options):
        target_usernames = [f'test_user_{i}' for i in range(1, 31)]
        created = 0
        skipped = 0

        for username in target_usernames:
            if User.objects.filter(username=username).exists():
                skipped += 1
                continue

            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='testpass123'
            )
            user.first_name = 'Test'
            user.last_name = username.split('_')[-1].title()
            user.save()
            created += 1
            self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))

        total_users = User.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSeed completed: {created} created, {skipped} skipped. Total users: {total_users}.'
            )
        )
