from urllib import request
from django.shortcuts import render
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.views.generic.edit import FormView
from django.conf import settings

from .models import *
from .forms import *


# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return render(request, 'main/index.html')
    else:
        return redirect('main:profile_user', username=request.user.username)


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'main/register_user.html'
    success_url = reverse_lazy('main:login_user')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('main:index')


class RegisterOrganizer(CreateView):
    form_class = OrganizerRegistrationForm
    template_name = 'main/register_organizer.html'
    success_url = reverse_lazy('main:login_organization')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

    def form_valid(self, form):
        organizer = form.save()
        login(self.request, organizer)
        return redirect('main:index')


class Login(LoginView):
    form_class = LoginForm
    template_name = 'main/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

    def get_success_url(self):
        return reverse_lazy('main:profile_user')


@login_required
def logout_user(request):
    logout(request)
    return redirect('main:index')


@login_required
def profile(request, username):
    return render(request, 'main/profile.html',
                  {'user': CustomUser.objects.get(pk=request.user.pk)})


class EventListView(ListView):
    model = Event
    queryset = Event.objects.all().order_by('published')
    context_object_name = 'events'
    template_name = 'main/events/events.html'
    paginate_by = 6


def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    is_registered = PersonEvent.objects.filter(person=request.user, event=event).exists()
    context = {'event': event,
               'user': CustomUser.objects.get(pk=request.user.pk),
               'is_registered': is_registered}
    return render(request, 'main/events/event.html', context)


@login_required
def upload_photos(request):
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        files = request.FILES.getlist('images')
        if form.is_valid():
            for f in files:
                PersonImage.objects.create(person=request.user, image=f)
            return redirect('main:profile_user', username=request.user.username)
    else:
        form = PhotoUploadForm()
    return render(request, 'main/upload_photos.html', {'form': form})


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Проверка, что текущий пользователь является организатором и организатором этого мероприятия
    if not request.user.is_organizer or event.org_user != request.user:
        return redirect('event_list')

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('main:event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)

    return render(request, 'main/events/edit_event.html', {'form': form, 'event': event})


@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Проверка, не зарегистрирован ли пользователь уже на мероприятие
    if PersonEvent.objects.filter(person=request.user, event=event).exists():
        return redirect('mian:event_detail', event_id=event.id)

    # Проверка на количество участников
    if event.attendees.count() >= event.exp_count_guests:
        return redirect('main:event_detail', event_id=event.id)

    PersonEvent.objects.create(person=request.user, event=event)
    return redirect('main:event_detail', event_id=event.id)

