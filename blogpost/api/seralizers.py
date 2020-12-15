import sys
import os
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from blogpost.models import BlogPost
import cv2
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from blogpost.utils import *

IMAGE_SIZE_MAX_BYTES = 1024 * 1024 * 2
MIN_TITLE_LENGTH = 5
MIN_BODY_LENGTH = 50


class BlogPostSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField('get_username_from_author')
    image = serializers.SerializerMethodField('validate_image_url')

    class Meta:
        model = BlogPost
        fields = ['pk', 'slug', 'title', 'body', 'image', 'date_updated', 'username']

    def get_username_from_author(self, blog_post):
        username = blog_post.author.username
        return username

    def validate_image_url(self, blog_post):
        image = blog_post.image
        new_url = image.url
        if "?" in new_url:
            new_url = image.url[:image.url.rfind("?")]
        return new_url


class BlogPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['title', 'body', 'image', 'date_updated', 'author']

    def save(self):
        try:
            image = self.validated_data['image']
            title = self.validated_data['title']
            author = self.validated_data['author']
            body = self.validated_data['body']

            if len(title) < MIN_TITLE_LENGTH:
                context = {
                    'response': 'Enter a title longer than ' + str(MIN_TITLE_LENGTH)
                }
                raise serializers.ValidationError(context)

            if len(body) < MIN_BODY_LENGTH:
                context = {
                    'response': 'Enter a body longer than ' + str(MIN_BODY_LENGTH)
                }
                raise serializers.ValidationError(context)

            blog_post = BlogPost(author=author, title=title, body=body, image=image)

            url = os.path.join(settings.TEMP, str(image))
            storage = FileSystemStorage(location=url)

            with storage.open('', 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
                destination.close()

            if not is_image_size_valid(url, IMAGE_SIZE_MAX_BYTES):
                os.remove(url)
                context = {
                    "response": "That image is too large. Image must be less than 2MB"
                }
                raise serializers.ValidationError(context)

            if not is_image_aspect_ratio_valid(url):
                os.remove(url)
                context = {
                    "response": "Image doesn't have the correct dimensions"
                }
                raise serializers.ValidationError(context)

            os.remove(url)
            blog_post.save()
            return blog_post
        except KeyError:
            context = {
                'response': 'Insert all the required data'
            }
            raise serializers.ValidationError(context)


class BlogPostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['title', 'body', 'image']

    def validate(self, blog_post):
        try:
            title = blog_post['title']
            if len(title) < MIN_TITLE_LENGTH:
                context = {
                    'response': 'Enter a title longer than ' + str(MIN_TITLE_LENGTH)
                }
                raise serializers.ValidationError(context)
            body = blog_post['body']
            if len(body) < MIN_BODY_LENGTH:
                context = {'response': 'Enter a body longer than ' + str(MIN_BODY_LENGTH)}
                raise serializers.ValidationError(context)

            image = blog_post['image']
            url = os.path.join(settings.TEMP, str(image))
            storage = FileSystemStorage(location=url)

            with storage.open('', 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
                destination.close()

            if not is_image_size_valid(url, IMAGE_SIZE_MAX_BYTES):
                os.remove(url)
                context = {"response": "The size of the image is larger"}
                raise serializers.ValidationError(context)

            if not is_image_aspect_ratio_valid(url):
                os.remove(url)
                context = {"response": "Image has incorrect dimensions"}
                raise serializers.ValidationError(context)

            os.remove(url)
        except KeyError:
            pass
        return blog_post
