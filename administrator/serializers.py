from core.serializers import BaseSerializer, serializers
from administrator.models import *
from accounts.serializers import UserSerializer


class PushNotificationSerializer(BaseSerializer):
    users = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="email",
    )

    class Meta:
        model = PushNotification
        fields = "__all__"

class UserPaymentPriceSerializer(BaseSerializer):
    created_by = UserSerializer(read_only=True, fields=["first_name", "last_name", "is_superuser"])
    class Meta:
        model = UserPaymentPrice
        fields = "__all__"
