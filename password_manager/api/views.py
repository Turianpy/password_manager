import jwt
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.response import Response
from users.models import User

from .serializers import UserSerializer, GetTokenSerializer
from .tasks import send_activation_email_task
from .utils import get_tokens, generate_user_token


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    send_activation_email_task(serializer.validated_data)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def activate(request):
    token = request.query_params.get('token')
    if not token:
        return Response(
            {'error': 'Token not provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(email=payload['email'])
        if user.is_active:
            return Response(
                {"message": "User already activated"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.is_active = True
        user.save()
        return Response(
            {"message": "Account successfully activated"},
            status=status.HTTP_200_OK
        )
    except jwt.ExpiredSignatureError:
        return Response(
            {'error': 'Activation link has expired'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except jwt.DecodeError:
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except User.DoesNotExist:
        return Response(
            {'error': 'User with given email not found'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, email=serializer.validated_data['email'])
    return Response(get_tokens(user), status=status.HTTP_200_OK)