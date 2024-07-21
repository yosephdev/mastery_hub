from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from .forms import MentorApplicationForm
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from .models import Profile, Feedback, Session, Mentorship

from .forms import (
    CustomSignupForm,
    CustomUserChangeForm,
    ProfileForm,
    SessionForm,
    ForumPostForm,
    MentorApplicationForm,
)
from .models import Profile, Mentorship, Session, Forum, Category, Feedback


# Create your views here.


def home(request):
    return render(request, "masteryhub/index.html")


def signup_view(request):
    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save(request=request)
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(
                request, f"Welcome, {user.username}! Registration successful!"
            )
            return redirect("home")
        else:
            for field, error in form.errors.items():
                messages.error(request, f"{field}: {error}")
    else:
        form = CustomSignupForm()
    return render(request, "account/signup.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "account/login.html"

    def form_valid(self, form):
        user = form.get_user()
        auth_login(self.request, user)
        if not self.request.session.get("message_sent", False):
            messages.success(self.request, f"Welcome back, {user.username}!")
            self.request.session["message_sent"] = True
        if user.is_superuser:
            return redirect("admin:index")
        elif user.profile.is_expert:
            return redirect("view_mentor_profile", username=user.username)
        else:
            return redirect("view_profile", username=user.username)

    def form_invalid(self, form):
        messages.error(
            self.request, "Login failed. Please check your username and password."
        )
        return self.render_to_response(self.get_context_data(form=form))


class CustomLogoutView(LogoutView):
    template_name = "account/logout.html"
    next_page = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            if not self.request.session.get("message_sent", False):
                messages.success(request, "You have been logged out successfully.")
                self.request.session["message_sent"] = True
            logout(request)
            return HttpResponseRedirect(self.get_next_page())
        elif request.method == "GET":
            return self.render_to_response(self.get_context_data())

    def get_next_page(self):
        return str(self.next_page)


def get_user_profile(username):
    return get_object_or_404(Profile, user__username=username)


@login_required
def view_profile(request, username=None):
    if username:
        profile = get_object_or_404(Profile, user__username=username)
        is_own_profile = request.user.username == username
    else:
        profile = request.user.profile
        is_own_profile = True

    context = {
        "profile": profile,
        "is_own_profile": is_own_profile,
        "has_profile_picture": bool(profile.profile_picture),
    }

    if profile.is_expert:
        return render(request, "masteryhub/view_mentor_profile.html", context)
    else:
        return render(request, "masteryhub/view_mentee_profile.html", context)


@login_required
def view_mentor_profile(request, username):
    profile = get_object_or_404(Profile, user__username=username, is_expert=True)
    is_own_profile = request.user.username == username
    context = {
        "profile": profile,
        "is_own_profile": is_own_profile,
        "has_profile_picture": bool(profile.profile_picture),
    }
    return render(request, "masteryhub/view_mentor_profile.html", context)


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("view_profile", username=profile.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, "masteryhub/edit_profile.html", {"form": form})


def search_mentors(request):
    query = request.GET.get("q")
    mentors = Profile.objects.filter(is_expert=True)
    if query:
        mentors = mentors.filter(mentorship_areas__icontains=query)
    return render(
        request, "masteryhub/search_mentors.html", {"mentors": mentors, "query": query}
    )


@login_required
def request_mentorship(request, mentor_id):
    mentor_user = get_object_or_404(User, id=mentor_id)
    mentor_profile = get_object_or_404(Profile, user=mentor_user)
    mentee_profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":
        mentorship, created = Mentorship.objects.get_or_create(
            mentor=mentor_profile, mentee=mentee_profile, status="pending"
        )
        if created:
            messages.success(
                request, f"Mentorship request sent to {mentor_user.username}"
            )
        else:
            messages.info(
                request,
                f"You already have a pending request with {mentor_user.username}",
            )
        return redirect("view_mentor_profile", username=mentor_user.username)

    return render(
        request, "masteryhub/request_mentorship.html", {"mentor": mentor_user}
    )


@login_required
def manage_mentorship_requests(request):
    mentor_profile = Profile.objects.get(user=request.user)
    pending_requests = Mentorship.objects.filter(
        mentor=mentor_profile, status="pending"
    )
    return render(
        request,
        "masteryhub/manage_mentorship_requests.html",
        {"pending_requests": pending_requests},
    )


def list_mentors(request):
    mentors = Profile.objects.filter(is_expert=True)
    return render(request, "masteryhub/list_mentors.html", {"mentors": mentors})


@login_required
def my_mentorships(request):
    mentorships_as_mentor = Mentorship.objects.filter(mentor=request.user)
    mentorships_as_mentee = Mentorship.objects.filter(mentee=request.user)
    context = {
        "mentorships_as_mentor": mentorships_as_mentor,
        "mentorships_as_mentee": mentorships_as_mentee,
    }
    return render(request, "masteryhub/my_mentorships.html", context)


@login_required
def accept_mentorship(request, mentorship_id):
    mentorship = get_object_or_404(Mentorship, id=mentorship_id, mentor=request.user)
    mentorship.status = "accepted"
    mentorship.start_date = timezone.now().date()
    mentorship.save()
    messages.success(request, f"Mentorship with {mentorship.mentee.username} accepted")
    return redirect("manage_mentorship_requests")


@login_required
def reject_mentorship(request, mentorship_id):
    mentorship = get_object_or_404(Mentorship, id=mentorship_id, mentor=request.user)
    mentorship.status = "rejected"
    mentorship.save()
    messages.success(request, f"Mentorship with {mentorship.mentee.username} rejected")
    return redirect("manage_mentorship_requests")


def session_list(request):
    query = request.GET.get("q")
    selected_category = request.GET.get("category")
    sessions = Session.objects.filter(status="scheduled")
    categories = Category.objects.all()

    if query:
        sessions = sessions.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if selected_category:
        sessions = sessions.filter(category__name=selected_category)

    context = {
        "sessions": sessions,
        "categories": categories,
        "selected_category": selected_category,
    }

    return render(request, "masteryhub/session_list.html", context)


@login_required
def view_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    return render(request, "masteryhub/view_session.html", {"session": session})


@login_required
def create_session(request):
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.host = request.user
            session.save()
            messages.success(request, "Session created successfully.")
            return redirect("view_session", session_id=session.id)
    else:
        form = SessionForm()
    return render(request, "masteryhub/create_session.html", {"form": form})


@login_required
def edit_session(request, session_id):
    session = get_object_or_404(Session, id=session_id, host=request.user)
    if request.method == "POST":
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, "Session updated successfully.")
            return redirect("view_session", session_id=session.id)
    else:
        form = SessionForm(instance=session)
    return render(
        request, "masteryhub/edit_session.html", {"form": form, "session": session}
    )


@login_required
def session_register(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if session.available_spots > 0:
        session.participants.add(request.user)
        messages.success(request, "You have successfully registered for this session.")
        return redirect("session_list")
    else:
        messages.error(request, "This session is full.")
        return render(request, "masteryhub/session_full.html")


@login_required
def forum_list(request):
    categories = Category.objects.all()
    posts = Forum.objects.filter(parent_post=None)
    return render(
        request,
        "masteryhub/forum_list.html",
        {"categories": categories, "posts": posts},
    )


@login_required
def create_forum_post(request):
    if request.method == "POST":
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.profile
            post.save()
            messages.success(request, "Forum post created successfully.")
            return redirect("view_forum_post", post_id=post.id)
    else:
        form = ForumPostForm()
    return render(request, "masteryhub/create_forum_post.html", {"form": form})


@login_required
def view_forum_post(request, post_id):
    post = get_object_or_404(Forum, id=post_id)
    comments = post.comments.all()
    return render(
        request, "masteryhub/view_forum_post.html", {"post": post, "comments": comments}
    )


@login_required
def reply_forum_post(request, post_id):
    parent_post = get_object_or_404(Forum, id=post_id)
    if request.method == "POST":
        form = ForumPostForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user.profile
            reply.parent_post = parent_post
            reply.save()
            messages.success(request, "Reply posted successfully.")
            return redirect("view_forum_post", post_id=parent_post.id)
    else:
        form = ForumPostForm()
    return render(
        request,
        "masteryhub/reply_forum_post.html",
        {"form": form, "parent_post": parent_post},
    )


@login_required
def expert_dashboard(request):
    expert_profile = Profile.objects.get(user=request.user)
    participants = Profile.objects.filter(
        mentorship_areas__icontains=expert_profile.mentorship_areas
    )
    feedbacks = Feedback.objects.filter(mentor=expert_profile)
    sessions = Session.objects.filter(host=expert_profile)

    labels = []
    data = []
    for session in sessions:
        labels.append(session.date.strftime("%B %Y"))
        data.append(1)

    context = {
        "username": request.user.username,
        "participants": participants,
        "feedbacks": feedbacks,
        "sessions": sessions,
        "labels": labels,
        "data": data,
    }
    return render(request, "masteryhub/expert_dashboard.html", context)


def become_mentor(request):
    if request.method == "POST":
        form = MentorApplicationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            areas_of_expertise = form.cleaned_data["areas_of_expertise"]

            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                LogEntry.objects.log_action(
                    user_id=admin_user.pk,
                    content_type_id=ContentType.objects.get_for_model(User).pk,
                    object_id=admin_user.pk,
                    object_repr=f"Mentor Application: {name} ({email})",
                    action_flag=ADDITION,
                    change_message=areas_of_expertise,
                )
            messages.success(
                request, "Your mentor application has been submitted successfully."
            )
            return redirect("home")
    else:
        form = MentorApplicationForm()
    return render(request, "masteryhub/become_mentor.html", {"form": form})


def match_mentor_mentee(mentee):
    mentee_profile = Profile.objects.get(user=mentee)
    mentee_skills = set(mentee_profile.skills.split(","))
    mentee_goals = set(mentee_profile.goals.split(","))

    potential_mentors = Profile.objects.filter(is_expert=True)
    matches = []

    for mentor_profile in potential_mentors:
        mentor_skills = set(mentor_profile.skills.split(","))
        mentor_areas = set(mentor_profile.mentorship_areas.split(","))

        skill_match = mentee_skills & mentor_skills
        goal_match = mentee_goals & mentor_areas

        if skill_match or goal_match:
            matches.append(
                {
                    "mentor": mentor_profile.user,
                    "skill_match": len(skill_match),
                    "goal_match": len(goal_match),
                    "total_match": len(skill_match) + len(goal_match),
                }
            )

    matches.sort(key=lambda x: x["total_match"], reverse=True)
    return matches


@login_required
def mentor_matching_view(request):
    if request.user.is_authenticated:
        mentee = request.user
        matches = match_mentor_mentee(mentee)
        return render(request, "masteryhub/matching_results.html", {"matches": matches})
    else:
        return redirect("login")


@login_required
def mentee_dashboard(request):
    mentee_profile = Profile.objects.get(user=request.user)
    feedbacks = Feedback.objects.filter(mentee=mentee_profile)
    sessions = Session.objects.filter(participants=mentee_profile)

    labels = []
    data = []

    session_counts = (
        sessions.values("date__month")
        .annotate(count=Count("id"))
        .order_by("date__month")
    )

    for entry in session_counts:
        month_name = entry["date__month"]
        labels.append(f"{month_name:02d}")
        data.append(entry["count"])

    skills = mentee_profile.skills.split(",") if mentee_profile.skills else []
    goals = mentee_profile.goals.split(",") if mentee_profile.goals else []

    context = {
        "username": request.user.username,
        "mentee_profile": mentee_profile,
        "feedbacks": feedbacks,
        "skills": skills,
        "goals": goals,
        "labels": labels,
        "data": data,
    }
    return render(request, "masteryhub/mentee_dashboard.html", context)


def pricing(request):
    return render(request, "masteryhub/pricing.html")


def forums(request):
    return render(request, "masteryhub/forum_list.html")


def report_concern(request):
    return render(request, "masteryhub/report_concern.html")


def mentor_help(request):
    return render(request, "masteryhub/mentor_help.html")


def mentor_rules(request):
    return render(request, "masteryhub/mentor_rules.html")
