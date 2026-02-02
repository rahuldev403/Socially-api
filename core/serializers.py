from rest_framework import serializers
from .models import Post
from django.contrib.auth.models import User
from .models import Post, Like
from .models import Comment

class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    like_count = serializers.SerializerMethodField()
    liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "author", "content", "created_at", "like_count", "liked_by_user"]

    def get_like_count(self, obj):
        return Like.objects.filter(
            target_type="POST",
            target_id=obj.id
        ).count()
    
    def get_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user,
                target_type="POST",
                target_id=obj.id
            ).exists()
        return False

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "author",
            "content",
            "parent",
            "created_at",
        ]
