from django.contrib import admin

from .models import User,Organization,Opportunity,Review,Event,Notification,Application,CauseArea,Skill

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'is_user', 'is_company', 'date_of_birth']
    search_fields = ['username', 'email']

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'phone', 'city', 'country']
    search_fields = ['name', 'email']
    list_filter = ['city', 'country']

@admin.register(CauseArea)
class CauseAreaAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']
    search_fields = ['title']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'organization', 'start_date', 'end_date', 'status']
    search_fields = ['title', 'organization__name']
    list_filter = ['status', 'cause_area', 'skills']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'opportunity', 'status']
    search_fields = ['user__username', 'opportunity__title']
    list_filter = ['status']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'org', 'rating', 'message']
    search_fields = ['user__username', 'org__name']
    list_filter = ['rating']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'date', 'location', 'Organization']
    search_fields = ['title', 'Organization__name']
    list_filter = ['date']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message', 'date_sent', 'is_read']
    search_fields = ['user__username', 'message']
    list_filter = ['is_read']

