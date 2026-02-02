from django.db import models
from django.contrib.auth.models import User

## post model
class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post {self.id} by {self.author.username}"
    

## comment model    
class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment {self.id} by {self.author.username}"


## like model
class Like(models.Model):
    POST = "POST"
    COMMENT = "COMMENT"

    TARGET_CHOICES = [
        (POST, "Post"),
        (COMMENT, "Comment"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    target_type = models.CharField(
        max_length=10,
        choices=TARGET_CHOICES
    )
    target_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "target_type", "target_id"],
                name="unique_user_like"
            )
        ]

    def __str__(self):
        return f"{self.user.username} liked {self.target_type} {self.target_id}"
