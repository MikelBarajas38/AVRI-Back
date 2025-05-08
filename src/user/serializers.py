"""
Serializers for the user API View.
"""

from django.contrib.auth import (
    get_user_model,
    authenticate
)

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user object.
    """

    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'password',
            'name',
            'first_name',
            'last_name',
            'education_level',
            'field_of_study',
            'is_staff',
            'is_author',
        )
        read_only_fields = ('is_staff',)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """
        Create a new user with encrypted password and return it.
        """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """
        Update a user, setting the password correctly and return it.
        """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AnonymousUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the anonymous user object.
    """

    class Meta:
        model = get_user_model()
        fields = ('is_anonymous', 'anonymous_id')
        read_only_fields = ('is_anonymous', 'anonymous_id')

    def create(self, validated_data):
        """
        Create a new anonymous user and return it.
        """
        return get_user_model().objects.create_user(
            is_anonymous=True,
            **validated_data
        )


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for the user authentication token.
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """
        Validate and authenticate the user.
        """
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = 'Unable to authenticate with provided credentials.'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class AnonymousAuthTokenSerializer(serializers.Serializer):
    """
    Serializer for the anonymous user authentication token.
    """
    anonymous_id = serializers.UUIDField()

    def validate(self, attrs):
        """
        Validate and authenticate the anonymous user.
        """
        anonymous_id = attrs.get('anonymous_id')
        user = get_user_model().objects.filter(
            anonymous_id=anonymous_id,
            is_anonymous=True
        ).first()

        if not user:
            msg = 'Unable to authenticate with provided credentials.'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
