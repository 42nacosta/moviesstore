from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from movies.models import UserLocation
from .forms import (
    CustomUserCreationForm,
    CustomErrorList,
    UserProfileForm,
    CITY_LOOKUP,
    CITY_CHOICES,
)


@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    return render(request, 'accounts/orders.html',
        {'template_data': template_data})


@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(request, username = request.POST['username'], password = request.POST['password'])
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html',
                {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})
# Create your views here.


# location-feature-branch: Profile view lets users manage their geographic location
@login_required
def profile(request):
    template_data = {'title': 'Profile'}
    user_location = getattr(request.user, 'userlocation', None)

    selected_key = None
    if user_location:
        for key, data in CITY_LOOKUP.items():
            if user_location.city == data['city'] and user_location.state_province == data['state']:
                selected_key = key
                break

    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            city_key = form.cleaned_data['location']
            city_data = CITY_LOOKUP.get(city_key)

            if not city_data:
                messages.error(request, 'Invalid location selected. Please try again.')
            else:
                if user_location:
                    user_location.city = city_data['city']
                    user_location.state_province = city_data['state']
                    user_location.country = city_data['country']
                    user_location.latitude = city_data['latitude']
                    user_location.longitude = city_data['longitude']
                    user_location.save()
                else:
                    UserLocation.objects.create(
                        user=request.user,
                        city=city_data['city'],
                        state_province=city_data['state'],
                        country=city_data['country'],
                        latitude=city_data['latitude'],
                        longitude=city_data['longitude'],
                    )

                messages.success(request, 'Your location has been updated.')
                return redirect('accounts.profile')
    else:
        initial_key = selected_key or CITY_CHOICES[0][0]
        form = UserProfileForm(initial={'location': initial_key})

    template_data['form'] = form
    template_data['current_location'] = user_location
    template_data['current_location_label'] = (
        f"{user_location.city}, {user_location.state_province}" if user_location else None
    )

    return render(request, 'accounts/profile.html', {'template_data': template_data})
