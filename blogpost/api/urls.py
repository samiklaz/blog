from django.urls import path
from blogpost.api.views import *


app_name = 'blog'

urlpatterns = [
    path('<slug>/', api_detail_blog_view, name='detail'),
    path('<slug>/update/', api_update_blog_view, name='update'),
    path('<slug>/delete/', api_delete_blog_view, name='delete'),
    path('create', api_create_blog_view, name='create'),
    path('list', ApiBlogListView.as_view(), name=''),
    path('<slug>/is_author', api_is_author_of_blogpost, name='is_author'),
]