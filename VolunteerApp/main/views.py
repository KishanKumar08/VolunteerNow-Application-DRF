from django.shortcuts import render

from django.contrib.auth.hashers import make_password
from django.contrib.auth import login,authenticate,logout

from rest_framework.response import Response
from rest_framework.generics import ListAPIView,DestroyAPIView,CreateAPIView,ListCreateAPIView,RetrieveAPIView,RetrieveDestroyAPIView,RetrieveUpdateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.decorators import APIView
from rest_framework import status,permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework.exceptions import NotFound,PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .permissions import IsCompany, IsUser
from .models import User,Organization,Opportunity,Review,Event,Notification,Application,CauseArea,Skill
from .serializers import organization_create_serializer,user_create_serializer,user_serializer,opportunity_serializer,organization_serializer,review_serializer,event_serializer,notification_serializer,application_serializer


class custom_pagination(PageNumberPagination):
    page_size = 2

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
    permission_classes = [IsAuthenticated]
    queryset = Organization.objects.all()
    serializer_class = organization_serializer

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
    permission_classes = [permissions.IsAuthenticated,IsUser]
    queryset = Opportunity.objects.all()
    serializer_class = opportunity_serializer

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
    pass

class ApplicationsForOpportunityView(ListAPIView):
    serializer_class = application_serializer

    def get_queryset(self):
        opp_id = self.kwargs.get('opp_id')
        return Application.objects.filter(opportunity=opp_id)

class ApplicationCreateView(CreateAPIView):
    serializer_class = application_serializer
    permission_classes = [permissions.IsAuthenticated,IsUser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ApplicationReadUpdateView(APIView):
    pass

class org_reviews(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated,IsUser]
    serializer_class = review_serializer

    def get_queryset(self):
        return Review.objects.filter(org=self.kwargs['org_id'])
    


    # def get(self,request,pk):
    #     queryset = Review.objects.filter(org=pk)
    #     serializer = review_serializer(queryset,many=True)
    #     return Response({'data':serializer.data})

    # def post(self,request,pk):
    #     serializer = review_serializer(data = request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({'message':'Review Added','data':serializer.data},tatus=status.HTTP_200_OK)
    #     return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)




