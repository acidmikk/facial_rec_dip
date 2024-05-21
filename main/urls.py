from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import *

app_name = 'main'

urlpatterns = [
    path('user/', include([
        path('registration/', RegisterUser.as_view(), name='registration_user'),
        path('login/', Login.as_view(), name='login_user'),
        path('upload-photos/',  upload_photos, name='upload_photos'),
    ])),
    path('organaizer/', include([
        path('registration/', RegisterOrganizer.as_view(), name='registration_organization'),
        path('login/', Login.as_view(), name='login_organization'),
    ])),
    path('logout/', logout_user, name='logout_user'),
    path('<str:username>', profile, name='profile_user'),
    path('change-password/', auth_views.PasswordChangeView.as_view(
        template_name='main/change_password.html', success_url=reverse_lazy('password_change_done')),
         name='change_password'),
    path('change-password-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='main/password_change_done.html'), name='password_change_done'),
    path('events/', include([
        path('', EventListView.as_view(), name='event_list'),
        path('<int:event_id>/edit/', edit_event, name='edit_event'),
        path('<int:event_id>/register/', register_for_event, name='register_for_event'),
        path('<int:event_id>/', event_detail, name='event_detail'),
    ])),
    path('', index, name='index'),
]
