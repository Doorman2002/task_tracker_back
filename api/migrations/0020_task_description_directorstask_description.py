from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_arrival'),
    ]

    operations = [
        migrations.AddField(
            model_name='directorstask',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]