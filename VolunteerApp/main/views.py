from django.shortcuts import render

from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, authenticate, logout

from rest_framework.response import Response

from rest_framework.generics import *
from rest_framework.decorators import APIView

from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .permissions import IsCompany, IsUser
from .models import *
from .serializers import (LoginSerializer, user_create_serializer, user_serializer, 
                          organization_create_serializer, organization_serializer, 
                          opportunity_serializer, cause_area_serializer, 
                          skill_serializer, event_serializer, review_serializer, 
                          application_serializer, event_register_serializer)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class UserSignUpView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = user_create_serializer

    # Handle user signup
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validate the input data
        serializer.save()  # Save the user data
        return Response(
            {
                'message': 'Account Created successfully',
                'user_data': serializer.data
            },
            status=status.HTTP_200_OK)  # Respond with success message

class LoginView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    # Handle user login and return JWT tokens
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if validation fails

        email = serializer.validated_data.get('email', None)
        password = serializer.validated_data.get('password', None)
        
        user = User.objects.filter(email=email).first()  # Find the user by email
        if user is None:
            return Response({'detail': 'User not Found with this email'}, status=status.HTTP_400_BAD_REQUEST)  # Return error if user not found

        refresh = RefreshToken.for_user(user)  # Create refresh token for the user

        response = Response()
        response.data = {
            'message': 'Login Successful',
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
        }
        response.status = status.HTTP_200_OK
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,  # Set cookie as HTTP-only
            secure=True,   # Use secure cookie for HTTPS
        )
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,  # Set cookie as HTTP-only
            secure=True,   # Use secure cookie for HTTPS
        )
        return response

class UserReadUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsUser]

    # Retrieve user profile object
    def get_object(self, request, pk):
        try:
            profile = userProfile.objects.get(pk=pk)  # Get the profile by primary key
            if profile.email != request.user.email:
                raise PermissionDenied(detail="You do not have permission to access this user's data.")  # Check if user has access
            return profile
        except userProfile.DoesNotExist:
            raise NotFound(detail="User not found")  # Handle profile not found

    # Retrieve user profile data
    def get(self, request, pk):
        profile = self.get_object(request, pk)
        serializer = user_serializer(profile)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=user_serializer,
        responses={
            200: user_serializer,
        }
    )
    # Update user profile data
    def put(self, request, pk):
        profile = self.get_object(request, pk)
        user = User.objects.filter(email=profile.email).first()  # Get associated user
        serializer = user_serializer(profile, data=request.data, partial=True)  # Update the profile
        if serializer.is_valid():
            updated_profile = serializer.save()
            if user:
                user.username = updated_profile.name
                user.email = updated_profile.email
                user.save()  # Update user data
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete user profile
    def delete(self, request, pk):
        profile = self.get_object(request, pk)
        user = User.objects.filter(email=profile.email).first()  # Get associated user
        profile.delete()  # Delete the profile
        if user:
            user.delete()  # Delete the user
        return Response({'message': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    # Handle user logout and blacklist tokens
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        access_token = request.COOKIES.get('access_token')

        if not refresh_token or not access_token:
            return Response({'detail': 'Tokens are required in cookies'}, status=status.HTTP_400_BAD_REQUEST)  # Check if tokens are present

        token = RefreshToken(refresh_token)
        token.blacklist()  # Blacklist the refresh token

        response = Response({'detail': 'Successfully logged out'}, status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie('refresh_token')  # Remove refresh token cookie
        response.delete_cookie('access_token')  # Remove access token cookie

        return response
        
class OrganizationRegisterView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = organization_create_serializer

    # Handle organization registration
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validate input data
        serializer.save()  # Save organization data
        return Response(
            {
                'message': 'Company registered successfully',
                'user_data': serializer.data
            },
            status=status.HTTP_200_OK)

class OrganizationListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsUser]
    queryset = Organization.objects.all()  # List all organizations
    serializer_class = organization_serializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['name']  # Allow ordering by name
    search_fields = ['=city', '^name', '^address']  # Enable searching
    filterset_fields = ['city']  # Allow filtering by city

class OrganizationReadUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    permission_classes = [IsAuthenticated, IsCompany]
    serializer_class = organization_serializer

    # Retrieve organization object
    def get_object(self):
        organization = super().get_object()
        try:
            if organization.name != self.request.user.username:
                raise PermissionDenied(detail="You do not have permission to access this company's data.")  # Check permission
            return organization
        except Organization.DoesNotExist:
            raise NotFound(detail="Company not found")  # Handle organization not found

    # Update organization details
    def put(self, request):
        organization = self.get_object()
        user = User.objects.filter(email=organization.email).first()  # Get associated user
        serializer = self.get_serializer(organization, data=request.data, partial=True)  # Update the organization
        if serializer.is_valid():
            updated_org = serializer.save()
            if user:
                user.username = updated_org.name
                user.email = updated_org.email
                user.save()  # Update user data
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete organization
    def delete(self, request):
        organization = self.get_object()
        user = User.objects.filter(email=organization.email).first()  # Get associated user
        organization.delete()  # Delete the organization
        if user:
            user.delete()  # Delete the user
        return Response({'message': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)

class AllOpportunitiesView(ListAPIView):
    permission_classes = [IsAuthenticated, IsUser]
    queryset = Opportunity.objects.all()  # List all opportunities
    serializer_class = opportunity_serializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['location']  # Enable searching by location
    filterset_fields = ['location', 'organization', 'cause_area', 'skills', 'status']  # Allow filtering

class OrganizationOpportunitiesView(ListAPIView):
    serializer_class = opportunity_serializer
    permission_classes = [IsAuthenticated, IsCompany]
    
    # Retrieve opportunities for a specific organization
    def get_queryset(self):
        org_id = self.kwargs.get('org_id')
        request = self.request
        org = Organization.objects.filter(id=org_id).first()
        if org.name != request.user.username:
            raise PermissionDenied(detail="You do not have permission to access this company's data")  # Check permission
        opportunities = Opportunity.objects.filter(organization=org_id)
        return opportunities

class OpportunityCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsCompany]
    serializer_class = opportunity_serializer

    # Create a new opportunity
    def post(self, request, org_id):
        org = Organization.objects.get(id=org_id)
        if org.name != request.user.username:
            raise PermissionDenied(detail="You do not have permission to create opportunities for this company")  # Check permission
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validate input data
        serializer.save()  # Save the opportunity
        return Response(
            {
                'message': 'Opportunity created successfully',
                'opportunity_data': serializer.data
            },
            status=status.HTTP_200_OK)

class OpportunityReadUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsCompany]
    serializer_class = opportunity_serializer

    # Retrieve opportunity object
    def get_object(self):
        opp_id = self.kwargs.get('opp_id')
        opportunity = Opportunity.objects.get(id=opp_id)
        if opportunity.organization.name != self.request.user.username:
            raise PermissionDenied(detail="You do not have permission to update this opportunity")  # Check permission
        return opportunity

class ApplicationsForOpportunityView(ListAPIView):
    serializer_class = application_serializer

    # Retrieve applications for a specific opportunity
    def get_queryset(self):
        opp_id = self.kwargs.get('opp_id')
        return Application.objects.filter(opportunity=opp_id)

class ApplicationCreateView(CreateAPIView):
    serializer_class = application_serializer
    permission_classes = [IsAuthenticated, IsUser]

    # Create a new application for an opportunity
    def post(self, request, org_id, opp_id):
        request.data["user"] = request.user.id  # Associate application with the current user
        request.data["opportunity"] = opp_id  # Associate application with the opportunity
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the application
            return Response({'detail': 'Application created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApplicationReadView(RetrieveAPIView):
    queryset = Application.objects.all()
    serializer_class = application_serializer
    permission_classes = [IsAuthenticated, IsCompany]

class ApplicationUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsCompany]
    serializer_class = application_serializer

    # Update application details
    def put(self, request, org_id, opp_id, app_id):
        application = Application.objects.get(id=app_id)
        if application.opportunity.organization.name != request.user.username:
            raise PermissionDenied(detail="You do not have permission to update this application")  # Check permission
        serializer = self.get_serializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save the updated application
            return Response({'detail': 'Application details updated successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApplicationDeleteView(DestroyAPIView):
    queryset = Application.objects.all()
    serializer_class = application_serializer
    permission_classes = [IsAuthenticated, IsCompany]

    # Delete an application
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return Response({'detail': 'Application successfully deleted'}, status=status.HTTP_204_NO_CONTENT)

class OrganizationReviews(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = review_serializer

    # Retrieve reviews for a specific organization
    def get_queryset(self):
        org_id = self.kwargs['org_id']
        return Review.objects.filter(org=org_id)

class CreateReviewView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsUser]
    serializer_class = review_serializer

    # Create a new review for an organization
    def post(self, request, org_id):
        request.data["org"] = org_id  # Associate review with the organization
        request.data["user"] = request.user.id  # Associate review with the user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the review
            return Response({'detail': 'Review added successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateReviewView(UpdateAPIView):
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated, IsUser]
    serializer_class = review_serializer

    # Update an existing review
    def put(self, request, org_id, pk):
        review = Review.objects.get(id=pk)
        if review.user != request.user.id:
            raise PermissionDenied(detail="You do not have permission to update this review")  # Check permission
        serializer = self.get_serializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save the updated review
            return Response({'detail': 'Review updated successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteReviewView(DestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = review_serializer
    permission_classes = [IsAuthenticated, IsUser, IsCompany]

    # Delete a review
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return Response({'detail': 'Review successfully deleted'}, status=status.HTTP_204_NO_CONTENT)

class OrganizationEventsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = event_serializer

    # Retrieve events for a specific organization
    def get_queryset(self):
        org_id = self.kwargs['org_id']
        return Event.objects.filter(Organization=org_id)

class EventsView(ListAPIView):
    permission_classes = [IsAuthenticated, IsUser]
    queryset = Event.objects.all()
    serializer_class = event_serializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['location']  # Enable searching by location
    filterset_fields = ['location', 'Organization', 'date']  # Allow filtering

class CreateEventView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsCompany]
    serializer_class = event_serializer

    # Create a new event
    def post(self, request, org_id):
        request.data["Organization"] = org_id  # Associate event with the organization
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the event
            return Response({'detail': 'Event created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateEventView(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsCompany]
    serializer_class = event_serializer

    # Update event details
    def get_object(self):
        pk = self.kwargs.get('pk')
        event = Event.objects.get(id=pk)
        if event.Organization.name != self.request.user.username:
            raise PermissionDenied(detail="You do not have permission to update this event")  # Check permission
        return event

class EventDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = event_serializer
    permission_classes = [IsAuthenticated, IsUser, IsCompany]

    # Retrieve or update event details
    def get_object(self):
        event = super().get_object()
        if event.Organization.name != self.request.user.username:
            raise PermissionDenied(detail="You do not have permission to update this event")  # Check permission
        return event

    def put(self, request, *args, **kwargs):
        response = super().put(self, request, *args, **kwargs)
        return Response({'detail': 'Event updated successfully'}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        response = super().patch(self, request, *args, **kwargs)
        return Response({'detail': 'Event updated successfully'}, status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return Response({'detail': 'Event deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class EventAttendeesListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsCompany]
    serializer_class = user_serializer

    # Retrieve attendees for a specific event
    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        queryset = userProfile.objects.filter(eventregistration__event=event_id)
        return queryset

class EventRegistrationView(CreateAPIView):
    serializer_class = event_register_serializer
    permission_classes = [IsAuthenticated, IsUser]

    # Register a user for an event
    def post(self, request, event_id):
        email = request.user.email
        userprofile = userProfile.objects.filter(email=email).first()
        serializer = event_register_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validate input data
        entity = serializer.save(commit=False)
        entity.user = userprofile.id  # Associate registration with the user
        entity.event = event_id  # Associate registration with the event
        entity.save()  # Save the registration
        return Response({'detail': 'Successfully Registered'}, status=status.HTTP_200_OK)
