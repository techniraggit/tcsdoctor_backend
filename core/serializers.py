from rest_framework import serializers
import pretty_errors


class BaseSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super(BaseSerializer, self).__init__(*args, **kwargs)
        if fields is not None:
            allowed_fields = set(fields)
            existing_fields = set(self.fields.keys())
            if len(allowed_fields) == 1 and list(allowed_fields)[0].startswith("-"):
                allowed_fields = {item.replace("-", "") for item in allowed_fields}
                for field_name in existing_fields.intersection(allowed_fields):
                    self.fields.pop(field_name)
            else:
                for field_name in existing_fields - allowed_fields:
                    self.fields.pop(field_name)
