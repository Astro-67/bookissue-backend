from rest_framework import serializers
from .models import Comment
from users.serializers import UserListSerializer


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model
    """
    author_name = serializers.ReadOnlyField()
    ticket_title = serializers.ReadOnlyField()
    author_details = UserListSerializer(source='author', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'ticket',
            'author',
            'author_name',
            'author_details',
            'message',
            'created_at',
            'ticket_title'
        ]
        read_only_fields = ['author', 'created_at', 'author_name', 'ticket_title']

    def validate_message(self, value):
        """Validate that message is not empty or just whitespace"""
        if not value or not value.strip():
            raise serializers.ValidationError("Comment message cannot be empty.")
        return value.strip()


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating comments (simplified)
    """
    class Meta:
        model = Comment
        fields = ['message']

    def validate_message(self, value):
        """Validate that message is not empty or just whitespace"""
        if not value or not value.strip():
            raise serializers.ValidationError("Comment message cannot be empty.")
        return value.strip()
