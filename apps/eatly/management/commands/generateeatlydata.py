# Python modules
from typing import Any
from random import choice, choices
from django.utils import timezone
from datetime import datetime, timedelta

# Django modules
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models import QuerySet

# Project modules
from apps.eatly.models import Restaurant, User

class Command(BaseCommand):
    help = "Generate tasks data for testing purposes"

    EMAIL_DOMAINS = (
        "example.com",
        "test.com",
        "sample.org",
        "demo.net",
        "mail.com",
        "kbtu.kz"
        "gmail.com"
    )

    NAMES = (
        "Alice",
        "Bob",
        "Charlie",
        "Diana",
        "Eve",
        "Frank",
        "Grace",
        "Heidi",
        "Ivan",
        "Judy"
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

    def __generate_users(self, user_count:int =100) -> None:
        """
        Generating users 
        """
        created_users: list[User] = []
        users_before: int = User.objects.count()
        hashed_password = make_password(password="12345")

        for i in range (user_count):
            name= f"{choice(self.NAMES)} {i+1}"
            email = f" user{i+1}@{choice(self.EMAIL_DOMAINS)}"
            role = "owner"

            created_users.append(
                User(
                    name=name,
                    email=email,
                    hashed_password= hashed_password,
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



    RESTAURANT_NAMES = (
        "Saffron", "Olive", "Spice", "Grill", "Garden", "Bistro", "Table", "Corner",
        "Kitchen", "Taste", "Vibe", "Fusion", "Sky", "Fire", "Salt", "Herb", "Crust", "Fork",
    )

    DESCRIPTIONS = (
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

    IMAGES = (
        "https://picsum.photos/seed/restaurant1/800/600",
        "https://picsum.photos/seed/restaurant2/800/600",
        "https://picsum.photos/seed/restaurant3/800/600",
        "https://picsum.photos/seed/restaurant4/800/600",
        "https://picsum.photos/seed/restaurant5/800/600",
    )

    ADDRESSES_STR = (
        "Abay Ave", "Dostyk St", "Al-Farabi Ave", "Tole Bi St", "Satpaev St",
        "Nazarbayev Ave", "Seifullin Ave", "Timiryazev St", "Kabanbay Batyr St"
    )

    ADDRESSES_NUM = (
        "10", "23A", "47", "52", "77B", "91", "108", "130", "200", "315"
    )
        
    def __generate_restaurant(self, restaurant_count:int = 100) -> None:
        """
        generating restaurants
        """

        owners= list(User.objects.filter(role="owner"))
        created_restaurants = []
        restaurants_before= Restaurant.objects.count()
        for i in range(restaurant_count):
            name: str = " ".join(choices(self.RESTAURANT_NAMES, k=2)).capitalize()
            description = choice(self.DESCRIPTIONS)
            image_url = choice(self.IMAGES)
            address = f"{choice(self.ADDRESSES_STR)}, {choice(self.ADDRESSES_NUM)}"
            address_link = f" https://maps.google.com/?q={address.replace(' ','+')}"
            owner = choice(owners)
            created_restaurants.append(
                Restaurant(
                    name=name,
                    description=description,
                    image_url=image_url,
                    address=address,
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


    def handle(self, *args:tuple[Any, ...], **kwargs:dict[str, Any])-> None:
        """
        Comman for entry point
        """
        start_time: datetime= datetime.now()
        self.__generate_users(user_count=10)
        self.stdout.write(
            "The whole process to generate users took: {} seconds".format(
                (datetime.now() - start_time).total_seconds()
            )
        )

        self.__generate_restaurant(restaurant_count=20)
        self.stdout.write(
            "The whole process to generate restaurants took: {} seconds".format(
                (datetime.now() - start_time).total_seconds()
            )
        )

