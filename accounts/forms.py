from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe


# location-feature-branch: Centralized city catalog for profile selection and geo data
CITY_DATA = [
    {'key': 'new_york_ny', 'city': 'New York', 'state': 'NY', 'country': 'US', 'latitude': 40.7128, 'longitude': -74.0060},
    {'key': 'los_angeles_ca', 'city': 'Los Angeles', 'state': 'CA', 'country': 'US', 'latitude': 34.0522, 'longitude': -118.2437},
    {'key': 'chicago_il', 'city': 'Chicago', 'state': 'IL', 'country': 'US', 'latitude': 41.8781, 'longitude': -87.6298},
    {'key': 'houston_tx', 'city': 'Houston', 'state': 'TX', 'country': 'US', 'latitude': 29.7604, 'longitude': -95.3698},
    {'key': 'phoenix_az', 'city': 'Phoenix', 'state': 'AZ', 'country': 'US', 'latitude': 33.4484, 'longitude': -112.0740},
    {'key': 'philadelphia_pa', 'city': 'Philadelphia', 'state': 'PA', 'country': 'US', 'latitude': 39.9526, 'longitude': -75.1652},
    {'key': 'san_antonio_tx', 'city': 'San Antonio', 'state': 'TX', 'country': 'US', 'latitude': 29.4241, 'longitude': -98.4936},
    {'key': 'san_diego_ca', 'city': 'San Diego', 'state': 'CA', 'country': 'US', 'latitude': 32.7157, 'longitude': -117.1611},
    {'key': 'dallas_tx', 'city': 'Dallas', 'state': 'TX', 'country': 'US', 'latitude': 32.7767, 'longitude': -96.7970},
    {'key': 'san_jose_ca', 'city': 'San Jose', 'state': 'CA', 'country': 'US', 'latitude': 37.3382, 'longitude': -121.8863},
    {'key': 'austin_tx', 'city': 'Austin', 'state': 'TX', 'country': 'US', 'latitude': 30.2672, 'longitude': -97.7431},
    {'key': 'jacksonville_fl', 'city': 'Jacksonville', 'state': 'FL', 'country': 'US', 'latitude': 30.3322, 'longitude': -81.6557},
    {'key': 'fort_worth_tx', 'city': 'Fort Worth', 'state': 'TX', 'country': 'US', 'latitude': 32.7555, 'longitude': -97.3308},
    {'key': 'columbus_oh', 'city': 'Columbus', 'state': 'OH', 'country': 'US', 'latitude': 39.9612, 'longitude': -82.9988},
    {'key': 'seattle_wa', 'city': 'Seattle', 'state': 'WA', 'country': 'US', 'latitude': 47.6062, 'longitude': -122.3321},
    {'key': 'denver_co', 'city': 'Denver', 'state': 'CO', 'country': 'US', 'latitude': 39.7392, 'longitude': -104.9903},
    {'key': 'boston_ma', 'city': 'Boston', 'state': 'MA', 'country': 'US', 'latitude': 42.3601, 'longitude': -71.0589},
    {'key': 'miami_fl', 'city': 'Miami', 'state': 'FL', 'country': 'US', 'latitude': 25.7617, 'longitude': -80.1918},
    {'key': 'atlanta_ga', 'city': 'Atlanta', 'state': 'GA', 'country': 'US', 'latitude': 33.7490, 'longitude': -84.3880},
    {'key': 'portland_or', 'city': 'Portland', 'state': 'OR', 'country': 'US', 'latitude': 45.5152, 'longitude': -122.6784},
]

CITY_CHOICES = [(entry['key'], f"{entry['city']}, {entry['state']}") for entry in CITY_DATA]
CITY_LOOKUP = {entry['key']: entry for entry in CITY_DATA}


class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})


# location-feature-branch: User profile form exposes dropdown of supported cities
class UserProfileForm(forms.Form):
    location = forms.ChoiceField(
        choices=CITY_CHOICES,
        required=True,
        label='Your Location'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].widget.attrs.update({'class': 'form-select'})
