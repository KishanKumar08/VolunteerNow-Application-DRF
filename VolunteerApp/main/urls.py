from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from .views import (
    UserSignUpView,UserReadUpdateDeleteView,
    LoginView,LogoutView,
    OrganizationRegisterView,OrganizationListView,OrganizationReadUpdateDeleteView,
    AllOpportunitiesView,OpportunityCreateView,ApplicationsForOpportunityView,OpportunityReadUpdateDeleteView,
    OrganizationOpportunitiesView,
    OrganizationReviews,CreateReviewView,UpdateReviewView,DeleteReviewView,
    OrganizationEventsView,EventsView,CreateEventView,EventDetailView,
    ApplicationUpdateView,ApplicationDeleteView,ApplicationReadView,ApplicationCreateView,
    EventRegistrationView,EventAttendeesListView
)

from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Volunteer API",
        default_version='v1',
        description="API documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourdomain.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[AllowAny],  # Ensure this is a list or tuple
)

urlpatterns = [
    # User
    path('user/signup/',UserSignUpView.as_view(),name="user-signup"),
    path('user/login/',LoginView.as_view(),name="user-login"),
    path('user/<int:pk>/', UserReadUpdateDeleteView.as_view(), name='user-detail-update-delete'),
    path('user/logout/', LogoutView.as_view(), name='user-logout'),

    path('organization/register/',OrganizationRegisterView.as_view(),name="organization-register"),
    path('organization/login/',LoginView.as_view(),name="organization-login"),
    path('organization/all/',OrganizationListView.as_view(),name="organizations-list"),
    path('organization/<int:pk>/',OrganizationReadUpdateDeleteView.as_view(),name="organization-detail-update-delete"),
    path('organization/logout/', LogoutView.as_view(), name='organization-logout'),

    path('organization/<int:org_id>/opportunities/all',OrganizationOpportunitiesView.as_view(),name="organization-opportunities"),
    path('organization/<int:org_id>/opportunities/create/',OpportunityCreateView.as_view(),name="opportunity-create"),
    path('organization/<int:org_id>/opportunities/<int:opp_id>/',OpportunityReadUpdateDeleteView.as_view(),name="opportunity-detail-update-delete"),

    path(
        'organization/<int:org_id>/opportunities/<int:opp_id>/applications/all/',
        ApplicationsForOpportunityView.as_view(),
        name="opportunity-applications"
    ),
    path(
        'organization/<int:org_id>/opportunities/<int:opp_id>/applications/create/',
        ApplicationCreateView.as_view(),
        name="application-create"
    ),
    path(
        'organization/<int:org_id>/opportunities/<int:opp_id>/applications/<int:app_id>/update/',
        ApplicationUpdateView.as_view(),
        name="application-update"
    ),
    path(
        'organization/<int:org_id>/opportunities/<int:opp_id>/applications/<int:pk>/',
        ApplicationReadView.as_view(),
        name="application-read"
    ),
    path(
        'organization/<int:org_id>/opportunities/<int:opp_id>/applications/<int:pk>/delete/',
        ApplicationDeleteView.as_view(),
        name="application-delete"
    ),

    path('opportunities/all/',AllOpportunitiesView.as_view(),name="all-opportunities"),

    path('organization/<int:org_id>/reviews/',OrganizationReviews.as_view(),name="organization-reviews"),
    path('organization/<int:org_id>/reviews/create/',CreateReviewView.as_view(),name="review-create"),
    path('organization/<int:org_id>/reviews/<int:pk>/update/',UpdateReviewView.as_view(),name="review-update"),
    path('organization/<int:org_id>/reviews/<int:pk>/delete/',DeleteReviewView.as_view(),name="review-delete"),


    path('events/all/',EventsView.as_view(),name="events"),
    path('organization/<int:org_id>/events/all/',OrganizationEventsView.as_view(),name="organization-events"),
    path('organization/<int:org_id>/events/create/',CreateEventView.as_view(),name="event-create"),
    path('organization/<int:org_id>/events/<int:pk>/',EventDetailView.as_view(),name="event-detail-update-delete"),
    path('organization/<int:org_id>/events/<int:event_id>/',EventAttendeesListView.as_view(),name="event-attendees-list"),
    path('events/int:<event_id>/register',EventRegistrationView.as_view(),name="event-register"),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-schema'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)