from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator 
from django.contrib.auth.hashers import make_password

# Custom User model extending AbstractUser
class User(AbstractUser):
    is_company = models.BooleanField(default=False)  # Indicates if the user is a company
    is_user = models.BooleanField(default=False)     # Indicates if the user is a regular user
    email = models.EmailField(unique=True)            # Unique email field

    def save(self, *args, **kwargs):
        # Hash password before saving if it's not None
        if self.password is not None:
            self.password = make_password(self.password)
        return super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

# Profile model for additional user information
class userProfile(models.Model):
    name = models.CharField(max_length=150, unique=True)  # Unique name field
    password = models.CharField(max_length=255)            # Password field (hashed before saving)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone_no = models.CharField(max_length=10, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Hash password before saving if it's not None
        if self.password is not None:
            self.password = make_password(self.password)
        return super(userProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

# Model representing organizations
class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)   # Unique name for the organization
    password = models.CharField(max_length=255)            # Password field (hashed before saving)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(unique=True)                   # Unique email field
    address = models.TextField()
    linkedin_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    mission = models.TextField()
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Hash password before saving if it's not None
        if self.password is not None:
            self.password = make_password(self.password)
        return super(Organization, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

# Model representing cause areas for opportunities
class CauseArea(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

# Model representing skills
class Skill(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Model representing opportunities for users
class Opportunity(models.Model):
    STATUS_CHOICES = [
        ('open', 'open'),
        ('closed', 'closed'),
    ]

    title = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="opportunities")
    opportunity_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=255)
    cause_area = models.ForeignKey(CauseArea, on_delete=models.CASCADE, related_name='opportunities')
    skills = models.ManyToManyField(Skill)
    is_favorite = models.BooleanField(default=False)
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default='open')

    def __str__(self):
        return f'{self.title} - {self.organization}'

# Model representing applications to opportunities
class Application(models.Model):
    user = models.ForeignKey(userProfile, on_delete=models.CASCADE, related_name='applications')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    def __str__(self):
        return f"Application by {self.user} for {self.opportunity}"

# Model representing reviews for organizations
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user} for {self.org}"

# Model representing events organized by organizations
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    Organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='events')

    def __str__(self):
        return f'Event - {self.title}'

# Model representing user registrations for events
class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="eventregistration")
    user = models.ForeignKey(userProfile, on_delete=models.CASCADE, related_name="eventregistration")
    register_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.name} registered for {self.event.title}'
