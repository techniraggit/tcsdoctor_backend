from core.serializers import BaseSerializer, serializers
from administrator.models import *


class PushNotificationSerializer(BaseSerializer):
    users = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="email",
    )

    class Meta:
        model = PushNotification
        fields = "__all__"
