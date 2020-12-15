from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter

from account.models import Account
from blogpost.models import BlogPost
from blogpost.api.seralizers import BlogPostSerializer, BlogPostUpdateSerializer, BlogPostCreateSerializer


@api_view(['GET', ])
@permission_classes((IsAuthenticated, ))
def api_detail_blog_view(request, slug):
    try:
        blog_post = BlogPost.objects.get(slug=slug)
    except BlogPost.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BlogPostSerializer(blog_post)
        return Response(serializer.data)


@api_view(['GET', ])
@permission_classes((IsAuthenticated, ))
def api_is_author_of_blogpost(request, slug):
    try:
        blog_post = BlogPost.objects.get(slug=slug)
    except BlogPost.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    data = {}
    user = request.user
    if blog_post.author != user:
        data['response'] = "You don't have permission to edit that"
        return Response(data=data)
    data['response'] = "You have permission to edit that"
    return Response(data=data)


@api_view(['PUT', ])
@permission_classes((IsAuthenticated, ))
def api_update_blog_view(request, slug):
    try:
        blog_post = BlogPost.objects.get(slug=slug)
    except BlogPost.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if blog_post.author != user:
        context = {
            'response': "You don't have permission to edit that"
        }
        return Response(context)

    if request.method == 'PUT':
        serializer = BlogPostUpdateSerializer(blog_post, data=request.data, partial=True)
        data = {}

        if serializer.is_valid():
            serializer.save()
            data = {
                'response': 'updated successfully',
                'pk': blog_post.pk,
                'title': blog_post.title,
                'body': blog_post.body,
                'slug': blog_post.slug,
                'date_updated': blog_post.date_updated,
                'username': blog_post.author.username
            }
            image_url = str(request.build_absolute_uri(blog_post.image.url))
            if "?" in image_url:
                image_url = image_url[:image_url.rfind('?')]

            data['image'] = image_url

            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
@permission_classes((IsAuthenticated, ))
def api_delete_blog_view(request, slug):
    try:
        blog_post = BlogPost.objects.get(slug=slug)
    except BlogPost.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if blog_post.author != request.user:
        context = {
            'response': "You don't have permission to delete this post"
        }
        return Response(context)

    if request.method == 'DELETE':
        operation = blog_post.delete()
        data = {}
        if operation:
            data = {
                'success': 'Deleted Successfully'
            }
        else:
            data = {
                'failure': 'Delete failed'
            }
        return Response(data=data)


@api_view(['POST', ])
@permission_classes((IsAuthenticated, ))
def api_create_blog_view(request):

    if request.method == 'POST':
        data = request.data
        data['author'] = request.user.pk
        serializer = BlogPostCreateSerializer(data=data)

        if serializer.is_valid():
            blog_post = serializer.save()

            image_url = str(request.build_absolute_uri(blog_post.image.url))
            if '?' in image_url:
                image_url = image_url[:image_url.rfind("?")]

            data = {
                'response': 'Post created successfully',
                'author': request.user.pk,
                'pk': blog_post.pk,
                'title': blog_post.title,
                'body': blog_post.body,
                'slug': blog_post.slug,
                'username': blog_post.author.username,
                'date_updated': blog_post.date_updated,
                'image': image_url,
            }

            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApiBlogListView(ListAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'body', 'author__username')