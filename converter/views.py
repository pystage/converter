from django.shortcuts import render
from django.http import HttpResponse
import tempfile

# Create your views here.

def index(request):
    return render(request, "converter/index.html", {})

def convert(request):
    if request.POST:
        context = {}
    tmpdir = tempfile.mkdtemp()
    print("Tmpdir: {}".format(tmpdir))

    if request.FILES and "sb3" in request.FILES:
        print("File found.")
        with open(tmpdir + '/input.sb3', mode="wb") as f:
            for chunk in request.FILES["sb3"].chunks():
                f.write(chunk)
    return HttpResponse("ok")