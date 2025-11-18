from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import User, Company, AdminProfile, DriverProfile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_company_for_owner(sender, instance, created, **kwargs):
    """
    Create Company when COMPANY_OWNER user is created.

    This signal automatically creates a Company instance for users
    with the COMPANY_OWNER role upon user creation.
    """
    if created and instance.role == User.Role.COMPANY_OWNER:
        try:
            with transaction.atomic():
                Company.objects.get_or_create(
                    owner=instance,
                    defaults={
                        "name": f"{instance.first_name} {instance.last_name}'s Company",
                        "email": instance.email,
                        "phone_number": instance.phone_number,
                    },
                )
                logger.info(
                    f"Company created for user {instance.id} ({instance.email})"
                )
        except Exception as e:
            logger.error(f"Error creating company for user {instance.id}: {e}")


@receiver(post_save, sender=User)
def create_driver_profile(sender, instance, created, **kwargs):
    """
    Create DriverProfile for all driver types and company owners.

    This signal creates a DriverProfile for users with roles:
    - COMPANY_OWNER
    - INDIVIDUAL_DRIVER
    - COMPANY_DRIVER
    """
    if created:
        driver_roles = [
            User.Role.COMPANY_OWNER,
            User.Role.INDIVIDUAL_DRIVER,
            User.Role.COMPANY_DRIVER,
        ]

        if instance.role in driver_roles:
            try:
                with transaction.atomic():
                    DriverProfile.objects.get_or_create(user=instance)
                    logger.info(
                        f"DriverProfile created for user {instance.id} ({instance.email})"
                    )
            except Exception as e:
                logger.error(
                    f"Error creating driver profile for user {instance.id}: {e}"
                )


@receiver(post_save, sender=User)
def create_admin_profile(sender, instance, created, **kwargs):
    """
    Create basic AdminProfile for admin users.

    This signal creates a basic AdminProfile instance for users
    with the ADMIN role.
    """
    if created and instance.role == User.Role.ADMIN:
        try:
            with transaction.atomic():
                AdminProfile.objects.get_or_create(user=instance)
                logger.info(
                    f"AdminProfile created for admin user {instance.id} ({instance.email})"
                )
        except Exception as e:
            logger.error(f"Error creating profile for admin user {instance.id}: {e}")


@receiver(post_save, sender=User)
def handle_role_change(sender, instance, created, **kwargs):
    """
    Handle profile updates when user role changes.

    This signal ensures that users have the appropriate profile type
    when their role is changed after initial creation.
    """
    if not created:  # Only run on updates, not creation
        try:
            with transaction.atomic():
                # Check if the user has the appropriate profile for their role
                driver_roles = [
                    User.Role.COMPANY_OWNER,
                    User.Role.INDIVIDUAL_DRIVER,
                    User.Role.COMPANY_DRIVER,
                ]

                if instance.role in driver_roles:
                    # These roles need DriverProfile
                    if not hasattr(instance, "driver_profile"):
                        DriverProfile.objects.create(user=instance)
                        logger.info(
                            f"DriverProfile created for role change: user {instance.id}"
                        )

                    # Create Company if user became a COMPANY_OWNER
                    if instance.role == User.Role.COMPANY_OWNER:
                        if not hasattr(instance, "owned_company"):
                            Company.objects.create(
                                owner=instance,
                                name=f"{instance.first_name} {instance.last_name}'s Company",
                                email=instance.email,
                                phone_number=instance.phone_number,
                            )
                            logger.info(
                                f"Company created for role change: user {instance.id}"
                            )

                elif instance.role == User.Role.ADMIN:
                    # Admins need basic Profile
                    if not hasattr(instance, "profile"):
                        Profile.objects.create(user=instance)
                        logger.info(
                            f"Profile created for role change: user {instance.id}"
                        )
        except Exception as e:
            logger.error(f"Error handling role change for user {instance.id}: {e}")
