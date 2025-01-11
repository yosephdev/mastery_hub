from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile
from django.db import transaction


@receiver(post_save, sender=User, dispatch_uid="user_profile_handler")
def create_or_update_profile(sender, instance, created, **kwargs):
    """Create or update user profile"""
    try:
        with transaction.atomic():
            profile, created = Profile.objects.get_or_create(
                user=instance,
                defaults={
                    'bio': '',
                    'skills': '',
                    'goals': '',
                    'experience': '',
                    'achievements': '',
                    'mentorship_areas': '',
                    'availability': '',
                    'preferred_mentoring_method': '',
                    'is_available': True
                }
            )
            if not created:
                profile.save()
    except Exception as e:
        print(f"Profile creation failed for {instance.username}: {e}")


def connect_signals():
    """Connect signals safely"""
    post_save.connect(
        create_or_update_profile,
        sender=User,
        dispatch_uid='create_user_profile'
    )
