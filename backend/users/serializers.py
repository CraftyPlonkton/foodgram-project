from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from djoser.conf import settings
from rest_framework import serializers

User = get_user_model()


class MyUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.USER_ID_FIELD,
            settings.LOGIN_FIELD,
            'is_subscribed',
        )
        read_only_fields = (settings.LOGIN_FIELD,)

    def get_is_subscribed(self, obj):
        return obj.followers.filter(id=self.context['request'].user.id).exists()
