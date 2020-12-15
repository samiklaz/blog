from django.urls import path
from account.api.views import *

app_name = 'account'

urlpatterns = [
    path('register', registration_view, name='register'),
    path('login', ObtainAuthTokenView.as_view(), name='login'),
    path('profile', account_properties_view, name='view'),
    path('profile/update', update_account_view, name='update'),
    path('check_if_account_exists/', does_account_exist_view, name='check if account exists'),
    path('change_password', ChangePasswordView.as_view(), name='change_password'),

]