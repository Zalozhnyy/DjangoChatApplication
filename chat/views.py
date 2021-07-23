import json

from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse


def index(request):
    return redirect('/login/')


def user_exist(request, username):
    out = {
        'exist': User.objects.filter(username=username).exists(),
        'user_name': username
    }
    # print(f'User exist func |  {username} is {out["exist"]}')
    return JsonResponse(out)


@login_required
def room(request, room_name):
    return render(request, 'chatroom.html', {
        'room_name': room_name
    })


@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'section': 'dashboard'})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            return render(request, 'register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'register.html', {'user_form': user_form})
