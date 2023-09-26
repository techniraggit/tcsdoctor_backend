from core.serializers import BaseSerializer
from accounts.models import User


class UserSerializer(BaseSerializer):
    class Meta:
        model = User
        fields = "__all__"
