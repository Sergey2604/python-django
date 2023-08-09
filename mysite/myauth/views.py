from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DetailView

from .forms import UserForm
from myauth.models import Profile


class UsersListView(ListView):
    template_name = 'myauth/users_list.html'
    context_object_name = 'users'
    model = User
    # queryset = Profile.objects.prefetch_related('avatar')


class UserUpdateView(UserPassesTestMixin, UpdateView):
    model = User
    template_name_suffix = '_update_form'
    form_class = UserForm
    context_object_name = 'user_upd'

    def get_success_url(self):
        return reverse(
            'myauth:user-list',
            kwargs = {'pk': self.object.pk}
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist('images'):
            User.objects.update_or_create(
                user = self.object,
                avatar = image
            )
        return response

    def get_object(self, queryset = None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        user = User.objects.select_related("profile").get(pk = pk)
        try:
            return user.profile
        except Profile.DoesNotExist:
            return Profile.objects.create(user = user)

    def test_func(self):
        if self.request.user.is_staff or self.request.user.is_superuser or (self.request.user.pk == Profile.user.pk):
            return True
        return False


class AboutMeView(TemplateView):
    template_name = 'myauth/about-me.html'


class UserInfoView(DetailView):
    template_name = 'myauth/about_user.html'
    model = User
    context_object_name = 'userr'

    def get_success_url(self):
        return reverse(
            'shopapp:product_details',
            kwargs = {'pk': self.object.pk}
        )


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about-me')

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user = self.object)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(self.request,
                            username = username,
                            password = password)
        login(request = self.request, user = user)
        return response


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/admin/')
        return render(request, 'myauth/login.html')
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username = username, password = password)
    if user:
        login(request, user)
        return redirect('/admin/')
    return render(request, 'myauth/login.html', {'error': 'Invalid login credentials'})


def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse('myauth:login'))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('myauth:login')


def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Set cookie')
    response.set_cookie('foo', 'bar', max_age = 600)
    return response


def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get('foo', 'getting cookies')
    return HttpResponse(f'Cookie value: {value!r}')


def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session['foobar'] = 'fizz buzz'
    return HttpResponse('Session set!')


def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get('foobar')
    return HttpResponse(f'Session value: {value!r}')


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({'foo': 'bar', 'spam': 'eggs'})
