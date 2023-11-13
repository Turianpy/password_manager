from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .utils import generate_salt
from .encryption import encrypt_password

from passwords.models import PasswordServicePair as PSP

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
        validated_data['salt'] = generate_salt()
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


class PSPCreateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = PSP
        fields = ('service_name', 'password')

    def create(self, validated_data):
        user = self.context['request'].user
        user_password = user.password
        password = validated_data.pop('password')

        iv, encrypted_password = encrypt_password(
            password,
            user_password,
            user.salt
        )

        psp, _ = PSP.objects.update_or_create(
            user=user,
            service_name=validated_data['service_name'],
            defaults={
                'encrypted_password': encrypted_password,
                'iv': iv
            }
        )
        return psp

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['password'] = instance.get_password()
        return ret


class PSPSerializer(serializers.ModelSerializer):

    class Meta:
        model = PSP
        fields = ('service_name', )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['password'] = instance.get_password()
        return representation
