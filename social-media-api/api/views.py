from rest_framework import generics, status, filters
from rest_framework.viewsets import ModelViewSet
from .serializers import SignUpSerializer, PostSerializer, LikeSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from app.models import Post, Like
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .paginations import PostPagination
from django.db.models import Q


class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]


class PostView(ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PostPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author__username']


    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    # return user posts ordered by time.
    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.filter(
            Q(visible='public') | Q(visible='friends', author__in=user.following.all()) | Q(visible='private', author=user)).order_by('created_at')

        return queryset
    
    # get all likes in a post.
    @action(detail=True, methods=['get'])
    def likes(self, request, pk):
        post =  self.get_object()
        likes = post.likes.all()
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)
        
    # like a post if user not already like it.
    @action(detail=True, methods=['post'])
    def like(self, request, pk):
        post =  self.get_object()
        liked, created = Like.objects.get_or_create(user=request.user, post=post)
        msg = f"{request.user.username} liked your video" if created else f"You already liked it."

        return Response({"detail": msg})
    
    # dislike a post if a user liked it.
    @action(detail=True, methods=['post'])
    def dislike(self, request, pk):  
        post =  self.get_object()
        like = get_object_or_404(post.likes.all(), user=request.user)
        like.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    # create a comment.
    def perform_create(self, serializer):
        '''
        find a post by user passed query params(id) then find
        author(request sender) and save them in a comment model.
        '''
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        author = self.request.user

        return serializer.save(author=author, post=post)
    
    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs.get('pk', None))
        return post.comments.all()

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id', None))
        return post.comments.all()
            
class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        following = self.request.user.following.all()
        following_posts = Post.objects.filter(author__in=following)

        return following_posts.all()