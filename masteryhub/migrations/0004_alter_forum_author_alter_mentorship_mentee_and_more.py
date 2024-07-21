# Generated by Django 5.0.6 on 2024-07-21 04:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("masteryhub", "0003_feedback"),
    ]

    operations = [
        migrations.AlterField(
            model_name="forum",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="masteryhub.profile"
            ),
        ),
        migrations.AlterField(
            model_name="mentorship",
            name="mentee",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mentorships_as_mentee",
                to="masteryhub.profile",
            ),
        ),
        migrations.AlterField(
            model_name="mentorship",
            name="mentor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mentorships_as_mentor",
                to="masteryhub.profile",
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="masteryhub.profile"
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="reviewer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="masteryhub.profile"
            ),
        ),
        migrations.AlterField(
            model_name="session",
            name="host",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sessions_hosted",
                to="masteryhub.profile",
            ),
        ),
        migrations.AlterField(
            model_name="session",
            name="participants",
            field=models.ManyToManyField(
                blank=True,
                related_name="sessions_participated",
                to="masteryhub.profile",
            ),
        ),
    ]
