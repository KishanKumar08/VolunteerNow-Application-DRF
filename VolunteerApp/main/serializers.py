
from .models import User,Organization,Opportunity,Review,Event,Notification,Application,CauseArea,Skill
from rest_framework.serializers import ModelSerializer,PrimaryKeyRelatedField

from django.contrib.auth.hashers import make_password

class user_create_serializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password':{'write_only':True}}

    def create(self,validated_data):
        password = validated_data.pop('password',None)
        if password is not None:
            password = make_password(password)
            validated_data['is_user'] = True
            validated_data['password'] = password
            user = User.objects.create(**validated_data)
            return user

class user_serializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password':{'write_only':True}}

class organization_create_serializer(ModelSerializer):

    class Meta:
        model = Organization
        fields = '__all__'
        extra_kwargs = {'password':{'write_only':True}}

    def create(self,validated_data):
        name = validated_data.get('name')
        password = validated_data.pop('password')
        password = make_password(password)
        validated_data['password'] = password
        email = validated_data.get('email')

        user = User.objects.create(username=name,password=password,email=email,is_company=True)
        org = Organization.objects.create(**validated_data)
        return org

class organization_serializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        extra_kwargs = {'password':{'write_only':True}}
    
class cause_area_serializer(ModelSerializer):
    class Meta:
        model = CauseArea
        fields = '__all__'

class skill_serializer(ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class opportunity_serializer(ModelSerializer):

    cause_area = PrimaryKeyRelatedField(queryset=CauseArea.objects.all())
    skills = PrimaryKeyRelatedField(queryset=Skill.objects.all(),many=True)

    class Meta:
        model = Opportunity
        fields = '__all__'

    def create(self,validated_data):
        cause_area = validated_data.pop('cause_area',None)
        skills = validated_data.pop('skills',[])
        opportunity = Opportunity.objects.create(cause_area=cause_area,**validated_data)
        opportunity.skills.set(skills)
        return opportunity
        
class review_serializer(ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class event_serializer(ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class notification_serializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class application_serializer(ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'
