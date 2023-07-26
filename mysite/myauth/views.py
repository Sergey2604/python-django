from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy


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
