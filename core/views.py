from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Like
from .serializers import PostSerializer
from django.db import IntegrityError
from core.authentication import CsrfExemptSessionAuthentication
from .models import Comment
from .serializers import CommentSerializer
from django.utils import timezone
from datetime import timedelta
from django.db.models import Case, When, IntegerField, Sum
from django.contrib.auth.models import User

# Create your views here.
@api_view(["POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def create_post(request):
    content = request.data.get("content")

    if not content:
        return Response(
            {"error": "Content is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    post = Post.objects.create(
        author=request.user,
        content=content
    )

    serializer = PostSerializer(post)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def list_posts(request):
    posts = Post.objects.select_related("author").order_by("-created_at")
    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(["POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    try:
        Like.objects.create(
            user=request.user,
            target_type="POST",
            target_id=post_id
        )
        return Response({"liked": True})
    except IntegrityError:
        return Response(
            {"error": "You have already liked this post"},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(["POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def create_comment(request):
    content = request.data.get("content")
    post_id = request.data.get("post_id")
    parent_id = request.data.get("parent_id")

    if not content or not post_id:
        return Response(
            {"error": "content and post_id are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    parent = None
    if parent_id:
        parent = Comment.objects.get(id=parent_id)

    comment = Comment.objects.create(
        author=request.user,
        post_id=post_id,
        parent=parent,
        content=content
    )

    serializer = CommentSerializer(comment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def get_comments(request, post_id):
    comments = Comment.objects.filter(
        post_id=post_id
    ).select_related("author").order_by("created_at")

    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

@api_view(["DELETE"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
        
        # Only allow author to delete their own comment
        if comment.author != request.user:
            return Response(
                {"error": "You can only delete your own comments"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        comment.delete()
        return Response({"deleted": True}, status=status.HTTP_200_OK)
    except Comment.DoesNotExist:
        return Response(
            {"error": "Comment not found"},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(["GET"])
def leaderboard(request):
    since = timezone.now() - timedelta(hours=24)

    likes = Like.objects.filter(created_at__gte=since)

    # Post likes → post.author
    post_scores = (
        likes
        .filter(target_type="POST")
        .values("target_id")
        .annotate(score=Sum(
            Case(
                When(target_type="POST", then=5),
                output_field=IntegerField()
            )
        ))
    )

    # Comment likes → comment.author
    comment_scores = (
        likes
        .filter(target_type="COMMENT")
        .values("target_id")
        .annotate(score=Sum(
            Case(
                When(target_type="COMMENT", then=1),
                output_field=IntegerField()
            )
        ))
    )

    user_karma = {}

    posts = {
        p.id: p.author_id
        for p in Post.objects.filter(
            id__in=[p["target_id"] for p in post_scores]
        )
    }

    comments = {
        c.id: c.author_id
        for c in Comment.objects.filter(
            id__in=[c["target_id"] for c in comment_scores]
        )
    }

    for item in post_scores:
        user_id = posts[item["target_id"]]
        user_karma[user_id] = user_karma.get(user_id, 0) + item["score"]

    for item in comment_scores:
        user_id = comments[item["target_id"]]
        user_karma[user_id] = user_karma.get(user_id, 0) + item["score"]

    leaderboard = (
        User.objects
        .filter(id__in=user_karma.keys())
        .annotate(karma=Case(
            *[
                When(id=user_id, then=karma)
                for user_id, karma in user_karma.items()
            ],
            output_field=IntegerField()
        ))
        .order_by("-karma")[:5]
    )

    return Response([
        {"username": u.username, "karma": u.karma}
        for u in leaderboard
    ])
