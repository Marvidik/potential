# serializers.py
from rest_framework import serializers
from .models import Consultation,Notification,UserInfo
from django.contrib.auth.models import User

class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = ['id','visitor_id','doctor_name', 'doctor_department', 'visit_date', 'visit_time', 'reason_for_visit']
        read_only_fields = ['id', 'visitor_id', 'user', 'status']



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'img', 'title', 'description', 'date']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['date'] = instance.date.strftime('%Y-%m-%d %H:%M:%S')  # format date
        return rep



class UserUpdateSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='info.phone_number', required=False)
    address = serializers.CharField(source='info.address', required=False)
    display_picture = serializers.ImageField(source='info.display_picture', required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'phone_number', 'address', 'display_picture']

    def update(self, instance, validated_data):
        # Extract info data
        info_data = validated_data.pop('info', {})

        # Update user fields
        if 'email' in validated_data:
            instance.email = validated_data['email']
            instance.username = validated_data['email']  # Email as username
        if 'first_name' in validated_data:
            instance.first_name = validated_data['first_name']
        if 'last_name' in validated_data:
            instance.last_name = validated_data['last_name']

        # Update password securely
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])

        instance.save()

        # Update or create related UserInfo
        user_info, created = UserInfo.objects.get_or_create(user=instance)
        if 'phone_number' in info_data:
            user_info.phone_number = info_data['phone_number']
        if 'address' in info_data:
            user_info.address = info_data['address']
        if 'display_picture' in info_data:
            user_info.display_picture = info_data['display_picture']
        user_info.save()

        return instance