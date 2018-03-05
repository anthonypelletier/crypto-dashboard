from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, REDIRECT_FIELD_NAME
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView
from .forms import UserCreationWithEmailForm


class LoginView(FormView):
    success_url = reverse_lazy('index')
    template_name = 'login.html'
    form_class = AuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)


class RegisterView(FormView):
    success_url = reverse_lazy('login')
    template_name = 'register.html'
    form_class = UserCreationWithEmailForm
    redirect_field_name = REDIRECT_FIELD_NAME

    def form_valid(self, form):
        form.save()
        return super(RegisterView, self).form_valid(form)


class LogoutView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)
