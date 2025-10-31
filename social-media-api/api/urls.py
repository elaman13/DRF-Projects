from django.urls import path, include
from .views import SignUpView, PostView, CommentView, CommentDetailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('posts', PostView, basename='posts')


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('token/', TokenObtainPairView.as_view(), name='token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('', include(router.urls)),
    path('posts/<int:pk>/comments/', CommentView.as_view(), name='comment'),
    path('posts/<int:post_id>/comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail')
]

