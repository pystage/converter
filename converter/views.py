from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
import tempfile
import pystage
from pystage.convert import sb3
from pathlib import Path
import json
import zipfile
import io
import os
import shutil

from . import models

# Create your views here.

def index(request):
    return render(request, "converter/index.html", {})


def conversion(request, project_link):
    conversion = get_object_or_404(models.Conversion, project_link=project_link)
    return render(request, "converter/conversion.html", {"conversion": conversion, "permalink": request.build_absolute_uri(f"/conversion/{project_link}")})

def download_sb3(request, project_link):
    conversion = get_object_or_404(models.Conversion, project_link=project_link)
    file_name = "{}/{}.sb3".format(conversion.tmpdir, conversion.project_name)
    with open(file_name, mode="rb") as f:
        response = HttpResponse(f.read())
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename={}-{}.sb3'.format(conversion.project_name, conversion.project_link)
        return response

def download(request, project_link):
    conversion = get_object_or_404(models.Conversion, project_link=project_link)
    buffer = io.BytesIO()
    zip = zipfile.ZipFile(buffer, "w")
    for root, dirs, files in os.walk(Path(conversion.tmpdir) / "{}-{}".format(conversion.project_name, conversion.project_link)):
        for file in files:
            zip.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       conversion.tmpdir))
    zip.close()
    response = HttpResponse(buffer.getvalue())
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Disposition'] = 'attachment; filename={}-{}.zip'.format(conversion.project_name, conversion.project_link)
    return response

def delete(request, project_link):
    return render(request, "converter/delete.html", {"project_link": project_link})


def delete_confirmed(request, project_link):
    conversion = get_object_or_404(models.Conversion, project_link=project_link)
    shutil.rmtree(conversion.tmpdir)
    conversion.delete()
    return redirect("index")

def convert(request):
    if request.POST:
        context = {}
    tmpdir = tempfile.mkdtemp()
    print("Tmpdir: {}".format(tmpdir))

    if request.FILES and "sb3" in request.FILES:
        print("File found.")
        file = request.FILES["sb3"]
        project_name = sb3.to_filename(Path(file.name).stem)
        project_link = models.generate_unique_link()
        file_name = "{}/{}.sb3".format(tmpdir, project_name)
        directory = "{}/{}".format(tmpdir, project_name + "-" + project_link)
        with open(file_name, mode="wb") as f:
            for chunk in file.chunks():
                f.write(chunk)
        
        data = sb3.get_sb3_data(file_name)
        project = sb3.get_intermediate(data, project_name)
        language = request.POST["language"]
        sb3.create_project(file_name, project_name, project, directory, language, project_link=request.build_absolute_uri(f"/conversion/{project_link}"))
        

        conversion = models.Conversion()
        conversion.tmpdir = tmpdir
        conversion.project_link = project_link
        conversion.sb3_file_name = file.name
        conversion.project_name = project_name
        conversion.language = language
        conversion.sb3_json = json.dumps(data, indent=2)
        conversion.intermediate = json.dumps(project, indent=2)
        conversion.python_code = sb3.get_python(project, language, project_link=request.build_absolute_uri(f"/conversion/{project_link}"))
        conversion.save()
        
        
    return redirect("conversion", project_link)