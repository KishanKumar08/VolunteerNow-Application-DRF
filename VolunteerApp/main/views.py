from django.shortcuts import render

from django.contrib.auth.hashers import make_password
from django.contrib.auth import login,authenticate,logout

from rest_framework.response import Response

from rest_framework.generics import *
from rest_framework.decorators import APIView

from rest_framework import status,permissions
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken

from rest_framework.exceptions import NotFound,PermissionDenied
from rest_framework.permissions import IsAuthenticated

from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .permissions import IsCompany, IsUser
from .models import *
from .serializers import *

class UserSignUpView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = user_create_serializer

    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'message':'Account Created successfully',
                'user_data':serializer.data
            },
            status=status.HTTP_200_OK)

class LoginView(APIView):

    permission_classes = [permissions.AllowAny]

    def get(self,request):
        return Response({'message':'Put all the details required for Login'},status=status.HTTP_200_OK)

    def post(self,request):
        username = request.data.get('username',None)
        name = request.data.get('name',None)
        password = request.data['password']

        if username and not name:
            user = User.objects.filter(username=username).first()

        if name and not username:
            user = User.objects.filter(username=name).first()

        if user is None:
            return Response({'detail': 'User not Found with this username'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({'detail': 'Wrong paasword'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        response = Response()

        response.data = {
            'message':'Login Successfull',
            'refresh_token':str(refresh),
            'access_token':str(refresh.access_token),
            'data':user_serializer(user).data
        }
        response.status = status.HTTP_200_OK
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
        )
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
        )

        return response

class UserReadUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated,IsUser]

    def get_object(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            if user != request.user:
                raise PermissionDenied(detail="You do not have permission to access this user's data.")
            return user
        except User.DoesNotExist:
            raise NotFound(detail="User not found")
    
    def get(self, request, pk):
        user = self.get_object(request, pk)
        serializer = user_serializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = self.get_object(request, pk)
        serializer = user_serializer(user, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(request, pk)
        user.delete()
        return Response({'message':'Deleted'},status=status.HTTP_204_NO_CONTENT)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        refresh_token = request.COOKIES.get('refresh_token')
        access_token = request.COOKIES.get('access_token')

        if not refresh_token or not access_token:
            return Response({'detail': 'Tokens are required in cookies'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response({'detail': 'Successfully logged out'}, status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie('refresh_token')
            response.delete_cookie('access_token')

            return response
        
        except TokenError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrganizationRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self,request):
        return Response({'message':'Put all the details required for Registration for a company'},status=status.HTTP_200_OK)

    def post(self,request):
        serializer = organization_create_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'message':'Company registered successfully',
                'user_data':serializer.data
            },
            status=status.HTTP_200_OK)

class OrganizationListView(ListAPIView):
    permission_classes = [IsAuthenticated,IsUser]
    queryset = Organization.objects.all()
    serializer_class = organization_serializer
    filter_backends = [SearchFilter,DjangoFilterBackend]
    search_fields = ['=city','^name','^address']
    filterset_fields = ['city']

class OrganizationReadUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,IsCompany]
    serializer_class = organization_serializer

    def get_object(self):
        pk = self.kwargs.get('pk')
        request = self.request
        try:
            organization = Organization.objects.get(pk=pk)
            if organization.name != request.user.username:
                raise PermissionDenied(detail="You do not have permission to access this company's data.")
            return organization
        except Organization.DoesNotExist:
            raise NotFound(detail="Company not found")

class AllOpportunitiesView(ListAPIView):
    permission_classes = [IsAuthenticated,IsUser]
    queryset = Opportunity.objects.all()
    serializer_class = opportunity_serializer
    filter_backends = [SearchFilter,DjangoFilterBackend]
    search_fields = ['location']
    filterset_fields = ['location','organization','cause_area','skills','status']

class OrganizationOpportunitiesView(APIView):
    permission_classes = [IsAuthenticated,IsCompany]
    
    def get(self,request,org_id):
        org = Organization.objects.filter(id=org_id).first()
        if org.name != request.user.username:
            raise PermissionDenied(detail="You do not have permission to access this company's data")
        opportunities = Opportunity.objects.filter(organization=org_id)
        serializer = opportunity_serializer(opportunities,many=True)
        return Response({'data':serializer.data})

class OpportunityCreateView(APIView):

    permission_classes = [IsAuthenticated,IsCompany]

    def post(self,request,org_id):
        org = Organization.objects.get(id=org_id)
        if org.name != request.user.username:
            raise PermissionDenied(detail="You do not have permission for this company")

        request.data['organization'] = org_id
        serializer = opportunity_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Opportunity Created'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class OpportunityReadUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,IsCompany]
    serializer_class = opportunity_serializer

    def get_object(self):
        opp_id = self.kwargs.get('opp_id')
        opportunity = Opportunity.objects.get(id=opp_id)
        if opportunity.organization.name != self.request.user.username:
            raise PermissionDenied(detail="You do not have permission for updating this opportunity")
        return opportunity
        
class ApplicationsForOpportunityView(ListAPIView):
    serializer_class = application_serializer

    def get_queryset(self):
        opp_id = self.kwargs.get('opp_id')
        return Application.objects.filter(opportunity=opp_id)

class ApplicationCreateView(CreateAPIView):
    serializer_class = application_serializer
    permission_classes = [IsAuthenticated,IsUser]

    def post(self,request,org_id,opp_id):
        request.data["user"] = request.user.id
        request.data["opportunity"] = opp_id

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'Application created Successfully'},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApplicationReadView(RetrieveAPIView):
    queryset = Application.objects.all()
    serializer_class = application_serializer
    permission_classes = [IsAuthenticated,IsCompany]

class ApplicationUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated,IsCompany]
    serializer_class = application_serializer

    def put(self,request,org_id,opp_id,app_id):
        application = Application.objects.get(id=app_id)
        if application.opportunity.organization.name != request.user.username:
            raise PermissionDenied(detail="You do not have permission to update this Event")
        serializer = self.get_serializer(application,data = request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'Application Details updated Successfully'},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApplicationDeleteView(DestroyAPIView):
    queryset = Application.objects.all()
    serializer_class = application_serializer
    permission_classes = [IsAuthenticated,IsCompany]

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return Response({'detail': 'Application successfully deleted'}, status=status.HTTP_204_NO_CONTENT)

class OrganizationReviews(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = review_serializer
    def get_queryset(self):
        org_id = self.kwargs['org_id']
        return Review.objects.filter(org=org_id)

class CreateReviewView(APIView):
    
    permission_classes = [IsAuthenticated,IsUser]

    def post(self,request,org_id):
        request.data["org"] = org_id
        request.data["user"] = request.user.id
        serializer = review_serializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'Review added Successfully'},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateReviewView(UpdateAPIView):

    permission_classes = [IsAuthenticated,IsUser]
    serializer_class = review_serializer

    def put(self,request,org_id,pk):
        review = Review.objects.get(id=pk)
        if review.user != request.user.id:
            raise PermissionDenied(detail="You do not have permission to update this review")
        serializer = self.get_serializer(review,data = request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'Review updated Successfully'},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteReviewView(DestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = review_serializer
    permission_classes = [IsAuthenticated,IsUser,IsCompany]

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return Response({'detail': 'Review successfully deleted'}, status=status.HTTP_204_NO_CONTENT)

class OrganizationEventsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = event_serializer
    def get_queryset(self):
        org_id = self.kwargs['org_id']
        return Event.objects.filter(Organization=org_id)

class EventsView(ListAPIView):
    permission_classes = [IsAuthenticated,IsUser]
    queryset = Event.objects.all()
    serializer_class = event_serializer
    filter_backends = [SearchFilter,DjangoFilterBackend]
    search_fields = ['location']
    filterset_fields = ['location','Organization','date']
    
class CreateEventView(APIView):
    permission_classes = [IsAuthenticated,IsCompany]
    def post(self,request,org_id):
        request.data["Organization"] = org_id
        serializer = event_serializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'Event created Successfully'},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateEventView(UpdateAPIView):
    permission_classes = [IsAuthenticated,IsCompany]
    serializer_class = event_serializer

    def get_object(self):
        pk = self.kwargs.get('pk')
        event = Event.objects.get(id=pk)
        if event.Organization.name != self.request.user.username:
            raise PermissionDenied(detail="You do not have permission to update this Event")
        return event

class EventDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = event_serializer
    permission_classes = [IsAuthenticated,IsUser,IsCompany]

    def get_object(self):
        event = super().get_object()
        if event.Organization.name != self.request.user.username:
            raise PermissionDenied(detail="You do not have permission to update this Event")
        return event
    
    def put(self,request,*args,**kwargs):
        response = super().put(self, request, *args, **kwargs)
        return Response({'detail': 'Event updated successfully '}, status=status.HTTP_204_NO_CONTENT)
    
    def patch(self,request,*args,**kwargs):
        response = super().patch(self, request, *args, **kwargs)
        return Response({'detail': 'Event updated successfully '}, status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return Response({'detail': 'Event deleted successfully '}, status=status.HTTP_204_NO_CONTENT)


