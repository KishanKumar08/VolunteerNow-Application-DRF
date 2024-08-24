from .models import User, Organization, Opportunity, Review, Event, Application, CauseArea, Skill, userProfile, EventRegistration
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from rest_framework import serializers

from django.contrib.auth.hashers import make_password

# Serializer for user creation
class user_create_serializer(ModelSerializer):
    class Meta:
        model = userProfile
        fields = ['id', 'name', 'password', 'email', 'date_of_birth', 'city']
        extra_kwargs = {'password': {'write_only': True}, 'email': {'required': True}}  # Ensure password is write-only

    def create(self, validated_data):
        # Create a new User and userProfile instance
        user = User.objects.create(
            username=validated_data['name'],
            email=validated_data['email'],
            is_user=True,
            is_active=True
        )
        user.set_password(validated_data['password'])
        userprofile = userProfile.objects.create(**validated_data)
        return userprofile

# Serializer for user details (update and retrieve)
class user_serializer(ModelSerializer):
    class Meta:
        model = userProfile
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}  # Ensure password is write-only

# Serializer for user login
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)

# Serializer for organization creation
class organization_create_serializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}, 'website': {'required': False}}  # Ensure password is write-only

    def create(self, validated_data):
        # Create a new User and Organization instance
        name = validated_data.get('name')
        password = validated_data.get('password', None)
        email = validated_data.get('email')
        user = User.objects.create(username=name, password=password, email=email, is_company=True)
        org = Organization.objects.create(**validated_data)
        return org

# Serializer for organization details (update and retrieve)
class organization_serializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}  # Ensure password is write-only

# Serializer for cause areas
class cause_area_serializer(ModelSerializer):
    class Meta:
        model = CauseArea
        fields = '__all__'

# Serializer for skills
class skill_serializer(ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

# Serializer for opportunities
class opportunity_serializer(ModelSerializer):
    cause_area = PrimaryKeyRelatedField(queryset=CauseArea.objects.all())  # Associate with CauseArea
    skills = PrimaryKeyRelatedField(queryset=Skill.objects.all(), many=True)  # Associate with multiple Skills

    class Meta:
        model = Opportunity
        fields = '__all__'

    def create(self, validated_data):
        # Create a new Opportunity instance
        cause_area = validated_data.pop('cause_area', None)
        skills = validated_data.pop('skills', [])
        opportunity = Opportunity.objects.create(cause_area=cause_area, **validated_data)
        opportunity.skills.set(skills)  # Set multiple skills
        return opportunity

# Serializer for reviews
class review_serializer(ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

# Serializer for events
class event_serializer(ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

# Serializer for applications
class application_serializer(ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'

# Serializer for event registrations
class event_register_serializer(ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = '__all__'
