# serializers.py
from rest_framework import serializers
from .models import Consultation,Notification,UserInfo,LabResult
from django.contrib.auth.models import User
import calendar
from django.db.models import Count
from django.db.models.functions import ExtractMonth

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
    


class LabResultSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(source='id', read_only=True)
    fileUrl = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at')

    class Meta:
        model = LabResult
        fields = ['_id', 'record_type', 'createdAt', 'fileUrl']

    def get_fileUrl(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.file.url) if obj.file else None
    

class UserDashboardSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    display_picture = serializers.SerializerMethodField()
    first_consultation = serializers.SerializerMethodField()
    last_consultation = serializers.SerializerMethodField()
    latest_consultations = serializers.SerializerMethodField()
    records = LabResultSerializer(source='lab_results', many=True)

    total_visits = serializers.SerializerMethodField()
    total_met = serializers.SerializerMethodField()
    total_pending = serializers.SerializerMethodField()
    total_results_viewed = serializers.SerializerMethodField()
    monthly_visits = serializers.SerializerMethodField()  # ✅ New field

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'date_joined', 'last_login',
            'location', 'display_picture','first_consultation', 'last_consultation',
            'latest_consultations', 'records',
            'total_visits', 'total_met', 'total_pending', 'total_results_viewed',
            'monthly_visits'  # ✅ Include in response
        ]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_location(self, obj):
        user_info = obj.userinfo.first()
        return user_info.address if user_info else None


    def get_display_picture(self, obj):
        user_info = obj.userinfo.first()
        if user_info and user_info.display_picture:
            request = self.context.get('request')
            return request.build_absolute_uri(user_info.display_picture.url)
        return None


    def get_first_consultation(self, obj):
        first = obj.consultations.order_by('visit_date', 'visit_time').first()
        return first.visit_date if first else None

    def get_last_consultation(self, obj):
        last = obj.consultations.order_by('-visit_date', '-visit_time').first()
        return last.visit_date if last else None

    def get_latest_consultations(self, obj):
        latest_two = obj.consultations.order_by('-visit_date', '-visit_time')[:2]
        return [
            {
                "visitDate": c.visit_date.strftime('%Y-%m-%d'),
                "ReasonForVisit": c.reason_for_visit,
                "staff": c.doctor_name
            }
            for c in latest_two
        ]

    def get_total_visits(self, obj):
        return obj.consultations.count()

    def get_total_met(self, obj):
        return obj.consultations.filter(status=True).count()

    def get_total_pending(self, obj):
        return obj.consultations.filter(status=False).count()

    def get_total_results_viewed(self, obj):
        return obj.lab_results.count()

    def get_monthly_visits(self, obj):
        # Group by month and count
        monthly_data = (
            obj.consultations
            .annotate(month=ExtractMonth('visit_date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        return [
            {
                "month": calendar.month_name[item['month']],
                "count": item['count']
            }
            for item in monthly_data
        ]