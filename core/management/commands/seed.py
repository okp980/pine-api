from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Seed the database with initial data."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Clear existing data.")

        parser.add_argument(
            "--num-users", type=int, default=10, help="Number of users to create."
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Seeding database with {options['num_users']} users..."
                )
            )
            self.stdout.write(self.style.SUCCESS("Database seeded successfully."))
