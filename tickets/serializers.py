from rest_framework import serializers
from .models import Ticket
from users.serializers import UserListSerializer


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer for Ticket model
    """
    created_by = UserListSerializer(read_only=True)
    assigned_to = UserListSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'status',
            'created_by', 'assigned_to', 'assigned_to_id',
            'created_at', 'updated_at', 'comments_count'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_comments_count(self, obj):
        """Get the number of comments for this ticket"""
        return obj.comments.count()

    def validate_assigned_to_id(self, value):
        """Validate that assigned user can manage tickets"""
        if value is not None:
            from users.models import User
            try:
                user = User.objects.get(id=value)
                if not user.can_manage_tickets():
                    raise serializers.ValidationError(
                        "User must be staff or ICT to be assigned tickets."
                    )
                return value
            except User.DoesNotExist:
                raise serializers.ValidationError("User does not exist.")
        return value

    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance:  # For updates
            current_status = self.instance.status
            # Define allowed transitions
            allowed_transitions = {
                'OPEN': ['IN_PROGRESS', 'RESOLVED'],
                'IN_PROGRESS': ['OPEN', 'RESOLVED'],
                'RESOLVED': ['OPEN', 'IN_PROGRESS']  # Allow reopening
            }
            
            if value != current_status and value not in allowed_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot change status from {current_status} to {value}"
                )
        
        return value

    def update(self, instance, validated_data):
        """Custom update to handle assigned_to_id"""
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        
        if assigned_to_id is not None:
            from users.models import User
            if assigned_to_id:
                assigned_user = User.objects.get(id=assigned_to_id)
                instance.assigned_to = assigned_user
            else:
                instance.assigned_to = None
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class TicketCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating tickets (simplified)
    """
    class Meta:
        model = Ticket
        fields = ['title', 'description']

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value.strip()

    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long.")
        return value.strip()


class TicketListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing tickets (minimal info)
    """
    created_by = UserListSerializer(read_only=True)
    assigned_to = UserListSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'status', 'created_by', 'assigned_to', 'created_at', 'comments_count'
        ]

    def get_comments_count(self, obj):
        """Get the number of comments for this ticket"""
        return obj.comments.count()
