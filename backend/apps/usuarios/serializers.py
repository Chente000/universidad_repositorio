# backend/apps/usuarios/serializers.py

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from apps.usuarios.models import Usuario
from universidad_repositorio.settings import CAREERS, USER_ROLES


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """
    Serializer para el registro de usuarios
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'cedula', 'telefono',
            'carrera', 'rol'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return attrs
    
    def validate_cedula(self, value):
        if Usuario.objects.filter(cedula=value).exists():
            raise serializers.ValidationError("Esta cédula ya está registrada.")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = Usuario.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UsuarioLoginSerializer(serializers.Serializer):
    """
    Serializer para el login de usuarios
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Credenciales inválidas.')
            if not user.activo:
                raise serializers.ValidationError('Usuario desactivado.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Debe incluir username y password.')


class UsuarioPerfilSerializer(serializers.ModelSerializer):
    """
    Serializer para el perfil de usuario
    """
    carrera_display = serializers.CharField(source='carrera.nombre', read_only=True)
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'cedula', 'telefono', 'carrera', 'carrera_display',
            'rol', 'rol_display', 'activo', 'verificado',
            'fecha_registro', 'ultima_conexion'
        ]
        read_only_fields = ['id', 'fecha_registro', 'ultima_conexion']
        
    def get_carrera_display(self, obj):
        if obj.carrera:
            return obj.carrera.nombre
        return "No asignada"


class UsuarioListSerializer(serializers.ModelSerializer):
    """
    Serializer para listado de usuarios (admin)
    """
    carrera_display = serializers.CharField(source='carrera.nombre', read_only=True)
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'carrera', 'carrera_display', 'rol', 'rol_display',
            'activo', 'fecha_registro', 'ultima_conexion'
        ]


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar perfil de usuario
    """
    class Meta:
        model = Usuario
        fields = [
            'first_name', 'last_name', 'email', 'telefono',
            'carrera'
        ]
    
    def validate_email(self, value):
        user = self.instance
        if Usuario.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está en uso.")
        return value


class CambioPasswordSerializer(serializers.Serializer):
    """
    Serializer para cambio de contraseña
    """
    password_actual = serializers.CharField(write_only=True)
    password_nueva = serializers.CharField(write_only=True, validators=[validate_password])
    password_nueva_confirm = serializers.CharField(write_only=True)
    
    def validate_password_actual(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Contraseña actual incorrecta.")
        return value
    
    def validate(self, attrs):
        if attrs['password_nueva'] != attrs['password_nueva_confirm']:
            raise serializers.ValidationError("Las contraseñas nuevas no coinciden.")
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['password_nueva'])
        user.save()
        return user