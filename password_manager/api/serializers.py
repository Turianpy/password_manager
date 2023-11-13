from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }

    def create(self, validated_data):
        pw = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(pw)
        user.save()
        return user


class GetTokenSerializer(serializers.Serializer):

    email = serializers.EmailField(max_length=255, required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Invalid credentials'
            )
        if not user.check_password(attrs['password']):
            raise serializers.ValidationError(
                'Invalid credentials'
            )
        if not user.is_active:
            raise serializers.ValidationError(
                'Account is not activated'
            )
        return attrs