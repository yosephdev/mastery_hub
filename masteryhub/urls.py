from django.urls import path

from . import views
from .views import CustomLoginView, CustomLogoutView
from .admin_views import admin_dashboard


urlpatterns = [
    # Home and Authentication
    path("", views.home, name="home"),
    path("signup/", views.signup_view, name="account_signup"),
    path("login/", CustomLoginView.as_view(), name="account_login"),
    path("logout/", CustomLogoutView.as_view(), name="account_logout"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("report-concern/", views.report_concern, name="report_concern"),
    # Admin Dashboard
    path("admin/dashboard/", admin_dashboard, name="admin_dashboard"),
    # Profile URLs
    path("profile/", views.view_profile, name="view_own_profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>/", views.view_profile, name="view_profile"),
    # Mentor URLs
    path("mentors/", views.list_mentors, name="list_mentors"),
    path(
        "mentor/<str:username>/", views.view_mentor_profile, name="view_mentor_profile"
    ),
    path("search-mentors/", views.search_mentors, name="search_mentors"),
    path("sessions/", views.session_list, name="session_list"),
    path("become-mentor/", views.become_mentor, name="become_mentor"),
    path("mentor-help/", views.mentor_help, name="mentor_help"),
    path("mentor-rules/", views.mentor_rules, name="mentor_rules"),
    # Mentorship URLs
    path(
        "request-mentorship/<int:mentor_id>/",
        views.request_mentorship,
        name="request_mentorship",
    ),
    path(
        "manage-mentorship-requests/",
        views.manage_mentorship_requests,
        name="manage_mentorship_requests",
    ),
    path(
        "accept-mentorship/<int:mentorship_id>/",
        views.accept_mentorship,
        name="accept_mentorship",
    ),
    path(
        "reject-mentorship/<int:mentorship_id>/",
        views.reject_mentorship,
        name="reject_mentorship",
    ),
    path("my-mentorships/", views.my_mentorships, name="my_mentorships"),
    # Session URLs
    path("sessions/", views.session_list, name="session_list"),
    path("sessions/<int:session_id>/", views.view_session, name="view_session"),
    path("sessions/create/", views.create_session, name="create_session"),
    path("sessions/<int:session_id>/edit/", views.edit_session, name="edit_session"),
    path(
        "sessions/<int:session_id>/register/",
        views.session_register,
        name="session_register",
    ),
    path("pricing/", views.pricing, name="pricing"),
    # Forum URLs
    path("forum/", views.forum_list, name="forum_list"),
    path("forum/create/", views.create_forum_post, name="create_forum_post"),
    path("forum/<int:post_id>/", views.view_forum_post, name="view_forum_post"),
    path("forum/<int:post_id>/reply/", views.reply_forum_post, name="reply_forum_post"),
    path("forums/", views.forums, name="forums"),
]
