# location-feature-branch: Seed command to generate test orders for trending map demo
# Creates 2-5 orders per user (who has location data), each with 2-6 random movies
# Generates richer purchase patterns to visualize geographic popularity across cities
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from movies.models import Movie
from cart.models import Order, Item
import random


class Command(BaseCommand):
    help = 'Seeds test orders with items for users with locations'

    def handle(self, *args, **kwargs):
        users_with_locations = User.objects.filter(userlocation__isnull=False)

        if not users_with_locations.exists():
            self.stdout.write(self.style.ERROR('No users with locations found. Run seed_user_locations first.'))
            return

        movies = list(Movie.objects.all())

        if not movies:
            self.stdout.write(self.style.ERROR('No movies found. Please add movies first.'))
            return

        orders_created = 0
        items_created = 0

        # Each user with location gets 2-5 orders containing random movies
        for user in users_with_locations:
            num_orders = random.randint(2, 5)

            for _ in range(num_orders):
                order = Order.objects.create(user=user, total=0)
                orders_created += 1

                max_items = min(6, len(movies))
                min_items = 1 if len(movies) == 1 else 2
                num_items = random.randint(min_items, max_items)
                selected_movies = random.sample(movies, num_items)

                order_total = 0
                for movie in selected_movies:
                    quantity = random.randint(1, 5)
                    Item.objects.create(
                        order=order,
                        movie=movie,
                        price=movie.price,
                        quantity=quantity
                    )
                    order_total += movie.price * quantity
                    items_created += 1

                order.total = order_total
                order.save()

                self.stdout.write(
                    f'Created order #{order.id} for {user.username} with {num_items} items (total: ${order_total})'
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSeed completed: {orders_created} orders created with {items_created} items total')
        )
