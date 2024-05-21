from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from djangoProject.settings import MEDIA_URL


# Create your models here.
def person_directory_path_of_name(instance, filename):
    print(f'person/{instance.first_name}_{instance.last_name}/{filename}')
    # файл будет загружен в MEDIA_ROOT/person/<name>/<filename>
    return f'person/{instance.first_name}_{instance.last_name}/{filename}'


class CustomUser(AbstractUser):
    is_organizer = models.BooleanField(default=False, verbose_name='Организатор?')
    org_name = models.CharField(verbose_name='Название организации', blank=True, null=True, max_length=255)
    INN = models.CharField(max_length=12, validators=[RegexValidator(r'^\d{10,12}$')], blank=True, null=True,
                           verbose_name='ИНН')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('main:profile_user', kwargs={'id': self.id})

    class Meta:
        verbose_name_plural = 'Участники'
        verbose_name = 'Участник'


class PersonImage(models.Model):
    person = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=f'person_face/', verbose_name='Фото лица')

    class Meta:
        verbose_name_plural = 'Фотографии лиц'
        verbose_name = 'Фотография лица'


class Attendance(models.Model):
    date = models.DateField()
    time_in = models.TimeField()

    class Meta:
        verbose_name_plural = 'Присутствия'
        verbose_name = 'Присутствие'


class Event(models.Model):
    name = models.CharField(max_length=100)
    published = models.DateField(db_index=True, verbose_name='Дата публикации')
    date = models.DateField(db_index=True, verbose_name='Дата мероприятия')
    location = models.CharField(max_length=100)
    org_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    exp_count_guests = models.IntegerField(verbose_name='Максимальное число участников')
    time_start = models.TimeField(verbose_name='Время начала')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:event', kwargs={'id': self.id})

    class Meta:
        verbose_name_plural = 'Мероприятия'
        verbose_name = 'Мероприятие'


class PersonAtt(models.Model):
    guest = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)


class PersonEvent(models.Model):
    person = models.ForeignKey(CustomUser, related_name='events', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name='attendees', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('person', 'event')
