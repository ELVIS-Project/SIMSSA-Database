from django.shortcuts import render
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import MusicalWork
from .models.genre import Genre
from .models.person import Person
from .models.instrument import Instrument
from .models.institution import Institution
from .models.section import Section
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import EmailMessage
# Create your views here.


class HomeView(TemplateView):  # show about page
    template_name = 'home.html'

class AboutView(TemplateView):  # show about page
    template_name = 'about.html'


class CreatePieceView(LoginRequiredMixin, CreateView): # This function
    # searches for post_form page!
    # you cannot create a post unless logged in
    login_url = '/login/'

    redirect_field_name = 'database/musicalwork_detail.html'  # save the new
    #  post, and it redirects to post_detail page

    form_class = PieceForm  # This creates a new PostForm,
    # and PostForm already specifies which fields we need to create
    model = MusicalWork


class MusicalWorkDetailView(DetailView):  # show the content
    # of the post when clicking
    model = MusicalWork  #


class MusicalWorkListView(ListView):  # home page: show a list of post
    model = MusicalWork  # what do you want to show
    # in this list: post, so model = Post
    paginate_by = 10
    queryset = MusicalWork.objects.all()

class GenreDetailView(DetailView):
    model = Genre


class GenreListView(ListView):
    model = Genre


class PersonListView(ListView):
    model = Person


class PersonDetailView(DetailView):
    model = Person


class InstrumentListView(ListView):
    model = Instrument


class InstrumentDetailView(DetailView):
    model = Instrument


class InstitutionListView(ListView):
    model = Institution


class InstitutionDetailView(DetailView):
    model = Institution


class SectionListView(ListView):
    model = Section


class SectionDetailView(DetailView):
    model = Section


def signup(request):
    if request.method == 'POST':  # 'POST' means the client submits something as resources to the server
        form = UserCreateForm(request.POST)  # We get the form from the user
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # user can’t login without email confirmation.
            user.save()
            current_site = get_current_site(request)
            message = render_to_string('registration/acc_active_email.html', { # Use this html template with the following variables
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })  # this creates a body of email where you are specified using a html
            mail_subject = 'Activate your SIMSSA DB account.'
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return HttpResponse('A confirmation email has been sent to your email address. '
                                'Please confirm your email address to complete the registration by '
                                'clicking the activation link in the email.')
    else:
        form = UserCreateForm()  # display the form for the user to fill in, since we got a GET request
    return render(request, 'registration/signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user) # automatically log in
        return redirect('home')
    else:
        return HttpResponse('Invalid activation link. Please examine your activation link and try again!')
    template_name = "registration/signup.html"
