from rest_framework import generics, status
from rest_framework.viewsets import ModelViewSet
from .serializers import SignUpSerializer, PostSerializer, LikeSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from app.models import Post, Like
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]


class PostView(ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(author=user)
    
    @action(detail=True, methods=['get', 'post'])
    def like(self, request, pk):
        if request.method == 'GET':
            like =  self.get_object()
            serializer = LikeSerializer(like.likes.all(), many=True)
            print(serializer.data)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            post =  self.get_object()
            liked, is_liked = Like.objects.get_or_create(user=request.user, post=post)
            print(f'liked: {liked}, is_liked: {is_liked}')

            return Response({"detail": f"{request.user.username} liked you're video" if is_liked else f"You already liked it."})
    
    @action(detail=True, methods=['post'])
    def dislike(self, request, pk):  
        post =  self.get_object()
        like = get_object_or_404(post.likes.all(), user=request.user)
        like.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
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
            