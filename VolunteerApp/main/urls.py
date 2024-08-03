from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (

    UserSignUpView,UserReadUpdateDeleteView,
    LoginView,LogoutView,
    OrganizationRegisterView,OrganizationListView,OrganizationReadUpdateDeleteView,
    AllOpportunitiesView,OpportunityCreateView,ApplicationsForOpportunityView,
    OrganizationOpportunitiesView,
    org_reviews
)

urlpatterns = [
    # User
    path('user/signup/',UserSignUpView.as_view(),name="user-signup"),
    path('user/login/',LoginView.as_view(),name="user-login"),
    path('user/<int:pk>/', UserReadUpdateDeleteView.as_view(), name='user-detail'),
    path('user/<int:pk>/update/', UserReadUpdateDeleteView.as_view(), name='user-update'),
    path('user/<int:pk>/delete/', UserReadUpdateDeleteView.as_view(), name='user-delete'),
    path('user/logout/', LogoutView.as_view(), name='user-logout'),

    path('organization/register/',OrganizationRegisterView.as_view(),name="organization-register"),
    path('organization/login/',LoginView.as_view(),name="organization-login"),
    path('organization/all/',OrganizationListView.as_view(),name="organizations-list"),
    path('organization/<int:pk>/',OrganizationReadUpdateDeleteView.as_view(),name="organization-detail"),
    path('organization/<int:pk>/update/',OrganizationReadUpdateDeleteView.as_view(),name="organization-update"),
    path('organization/<int:pk>/delete/',OrganizationReadUpdateDeleteView.as_view(),name="organization-delete"),
    path('organization/logout/', LogoutView.as_view(), name='organization-logout'),
    path('organization/<int:org_id>/opportunities/all',OrganizationOpportunitiesView.as_view(),name="organization-opportunities"),
    path('organization/<int:org_id>/opportunities/create/',OpportunityCreateView.as_view(),name="opportunity-create"),
    path(
        'organization/<int:org_id>/opportunities/<int:opp_id>/applications/all',
        ApplicationsForOpportunityView.as_view(),
        name="opportunity-applications"
    ),
    path('opportunities/all',AllOpportunitiesView.as_view(),name="all-opportunities"),
    # path('opportunities/<int:pk>/',opportunity_detail.as_view(),name="opportunity"),
    # path('opportunities/<int:pk>/update/',opportunity_detail.as_view(),name="opportunity_update"),
    # path('opportunities/<int:pk>/delete/',opportunity_detail.as_view(),name="opportunity_delete"),

    path('organization/<int:org_id>/reviews/',org_reviews.as_view(),name="reviews_view"),
    path('organization/<int:org_id>/reviews/create',org_reviews.as_view(),name="review_create"),




    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)