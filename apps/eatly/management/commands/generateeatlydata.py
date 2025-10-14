# Python modules
from typing import Any, List, Dict, Tuple, Optional
from random import choice, choices
from datetime import datetime

# Django modules
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

# Project modules
from apps.eatly.models import Restaurant, User


class Command(BaseCommand):
    """Generate users and restaurant data for testing purposes."""

    help = "Generate users and restaurants data for testing."

    EMAIL_DOMAINS: Tuple[str, ...] = (
        "example.com",
        "test.com",
        "sample.org",
        "demo.net",
        "mail.com",
        "kbtu.kz",
        "gmail.com",
    )

    NAMES: Tuple[str, ...] = (
        "Alice",
        "Bob",
        "Charlie",
        "Diana",
        "Eve",
        "Frank",
        "Grace",
        "Heidi",
        "Ivan",
        "Judy",
        "Oliver",
        "Jacob",
        "Lucas",
        "Michael",
        "Alexander",
        "Ethan",
        "Daniel",
        "Matthew",
        "Aiden",
        "Henry",
        "Joseph",
        "Jackson",
        "Samuel",
        "Sebastian",
        "David",
        "Carter",
        "Wyatt",
        "Jayden",
        "John",
        "Owen",
        "Dylan",
    )

    RESTAURANT_NAMES: Tuple[str, ...] = (
        "Saffron", "Olive", "Spice", "Grill", "Garden", "Bistro", "Table",
        "Corner", "Kitchen", "Taste", "Vibe", "Fusion", "Sky", "Fire", "Salt",
        "Herb", "Crust", "Fork",
    )

    DESCRIPTIONS: Tuple[str, ...] = (
        "Cozy place with a modern twist.",
        "Authentic dishes prepared with love.",
        "Perfect for family dinners and friends.",
        "Fresh ingredients and great service.",
        "Traditional taste with a new flavor.",
        "Your go-to spot for casual dining.",
        "Comfort food done right.",
        "Elegant ambiance and fine dining experience.",
        "Street food inspired modern cuisine.",
        "For those who love good taste and good mood.",
    )

    IMAGES: Tuple[str, ...] = (
        "https://picsum.photos/seed/restaurant1/800/600",
        "https://picsum.photos/seed/restaurant2/800/600",
        "https://picsum.photos/seed/restaurant3/800/600",
        "https://picsum.photos/seed/restaurant4/800/600",
        "https://picsum.photos/seed/restaurant5/800/600",
    )

    ADDRESSES_STR: Tuple[str, ...] = (
        "Abay Ave", "Dostyk St", "Al-Farabi Ave", "Tole Bi St", "Satpaev St",
        "Nazarbayev Ave", "Seifullin Ave", "Timiryazev St", "Kabanbay Batyr St",
    )

    ADDRESSES_NUM: Tuple[str, ...] = (
        "10", "23A", "47", "52", "77B", "91", "108", "130", "200", "315",
    )

    def __generate_users(self, user_count: int = 100) -> None:
        """Generate test users."""
        created_users: List[User] = []
        users_before: int = User.objects.count()
        hashed_password: str = make_password(password="12345")

        for i in range(user_count):
            name: str = f"{choice(self.NAMES)} {i + 1}"
            email: str = f"user{i + 1}@{choice(self.EMAIL_DOMAINS)}"
            role: str = "customer"

            created_users.append(
                User(
                    name=name,
                    email=email,
                    hashed_password=hashed_password,
                    role=role,
                    created_at=timezone.now(),
                    updated_at=timezone.now(),
                )
            )

        User.objects.bulk_create(created_users, ignore_conflicts=True)
        users_after: int = User.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {users_after - users_before} users."
            )
        )

    def __generate_restaurants(self, restaurant_count: int = 100) -> None:
        """Generate test restaurants."""
        owners: List[User] = list(User.objects.filter(role="owner"))
        created_restaurants: List[Restaurant] = []
        restaurants_before: int = Restaurant.objects.count()

        for _ in range(restaurant_count):
            name: str = " ".join(choices(self.RESTAURANT_NAMES, k=2)).capitalize()
            description: str = choice(self.DESCRIPTIONS)
            image_url: str = choice(self.IMAGES)
            address: str = (
                f"{choice(self.ADDRESSES_STR)}, {choice(self.ADDRESSES_NUM)}"
            )
            address_link: str = (
                f"https://maps.google.com/?q={address.replace(' ', '+')}"
            )
            owner: Optional[User] = choice(owners) if owners else None

            created_restaurants.append(
                Restaurant(
                    name=name,
                    description=description,
                    image_url=image_url,
                    address=address,
                    address_link=address_link,
                    owner=owner,
                    created_at=timezone.now(),
                    updated_at=timezone.now(),
                )
            )

        Restaurant.objects.bulk_create(created_restaurants, ignore_conflicts=True)
        restaurants_after: int = Restaurant.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {restaurants_after - restaurants_before} restaurants."
            )
        )

    def handle(
        self,
        *args: Tuple[Any, ...],
        **kwargs: Dict[str, Any],
    ) -> None:
        """Entry point for command execution."""
        start_time: datetime = datetime.now()

        self.__generate_users(user_count=100)
        self.stdout.write(
            f"Generated users in "
            f"{(datetime.now() - start_time).total_seconds()} seconds."
        )

        self.__generate_restaurants(restaurant_count=100)
        self.stdout.write(
            f"Generated restaurants in "
            f"{(datetime.now() - start_time).total_seconds()} seconds."
        )
