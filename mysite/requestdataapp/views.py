from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get('a', '')
    b = request.GET.get('b', '')
    result = a + b
    context = {
        'a': a,
        'b': b,
        'result': result
    }
    return render(request, 'requestdataapp/request-query-params.html', context=context)


def file_download(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST' and request.FILES.get('myfile'):
        max_size = 1048576
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        if myfile.size <= max_size:
            filename = fs.save(myfile.name, myfile)
            return render(request, 'requestdataapp/file-upload.html')
        else:
            return HttpResponse("Размер файла слишком велик.")
    return render(request, 'requestdataapp/file-upload.html')
