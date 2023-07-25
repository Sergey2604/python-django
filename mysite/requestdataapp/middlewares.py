import datetime

from django.http import HttpRequest, HttpResponse


class CountRequestMiddlewares:
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest):
        self.request_count += 1
        if self.request_count == 1:
            self.time_start = datetime.datetime.now()
        if self.request_count == 55:
            self.time_end = datetime.datetime.now()
            print(self.time_start)
            print(self.time_end)
            if self.time_end - self.time_start <= datetime.timedelta(seconds=60):
                return HttpResponse('Вы слишком часто обновляете страницу!')
        response = self.get_response(request)
        self.responses_count += 1
        return response
