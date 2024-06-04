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
import re
import requests
import json

from . import models

ID_REGEX = re.compile(r"[0-9]{6,20}")

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


def _process_sb3_file(request, tmpdir, file_name, project_name, directory, language, project_link, scratch_id):
        data = sb3.get_sb3_data(file_name)
        project = sb3.get_intermediate(data, project_name)
        sb3.create_project(file_name, project_name, project, directory, language, project_link=request.build_absolute_uri(f"/conversion/{project_link}"))
        

        conversion = models.Conversion()
        conversion.tmpdir = tmpdir
        conversion.project_link = project_link
        conversion.scratch_id = scratch_id
        conversion.sb3_file_name = f"{project_name}.sb3"
        conversion.project_name = project_name
        conversion.language = language
        conversion.sb3_json = json.dumps(data, indent=2)
        conversion.intermediate = json.dumps(project, indent=2)
        conversion.python_code = sb3.get_python(project, language, project_link=request.build_absolute_uri(f"/conversion/{project_link}"))
        conversion.save()



def convert(request):
    if request.POST:
        context = {}
    tmpdir = tempfile.mkdtemp()
    print("Tmpdir: {}".format(tmpdir))

    if "url" in request.POST:
        match = ID_REGEX.search(request.POST["url"])
        if match:
            scratch_id = match.group()
        else:
            scratch_id = None


    project_link = models.generate_unique_link()
    language = request.POST["language"]
        

    if request.FILES and "sb3" in request.FILES:
        print("File found.")
        file = request.FILES["sb3"]
        project_name = sb3.to_filename(Path(file.name).stem)
        file_name = "{}/{}.sb3".format(tmpdir, project_name)
        directory = "{}/{}".format(tmpdir, project_name + "-" + project_link)
        with open(file_name, mode="wb") as f:
            for chunk in file.chunks():
                f.write(chunk)
        _process_sb3_file(request, tmpdir, file_name, project_name, directory, language, project_link, scratch_id)
        
    elif scratch_id:
        try:
            response = requests.get(f"https://api.scratch.mit.edu/projects/{scratch_id}")
            project_data = response.json()
            project_name = sb3.to_filename(project_data["title"])
            file_name = "{}/{}.sb3".format(tmpdir, project_name)
            directory = "{}/{}".format(tmpdir, project_name + "-" + project_link)
            token = project_data["project_token"]
            print("Token:", token)
            response = requests.get(f"https://projects.scratch.mit.edu/{scratch_id}?token={token}")
            sb3_data = response.json() 
            with zipfile.ZipFile(file_name, "w") as zip:
                zip.writestr("project.json", json.dumps(sb3_data))
                for target in sb3_data["targets"]:
                    print(target)
                    for costume in target["costumes"]:
                        print(costume)
                        response = requests.get(f"https://assets.scratch.mit.edu/internalapi/asset/{costume['md5ext']}/get/")
                        zip.writestr(costume["md5ext"], response.content)
                    for sound in target["sounds"]:
                        print(sound)
                        response = requests.get(f"https://assets.scratch.mit.edu/internalapi/asset/{sound['md5ext']}/get/")    
                        zip.writestr(sound["md5ext"], response.content)
            _process_sb3_file(request, tmpdir, file_name, project_name, directory, language, project_link, scratch_id)
        except Exception as e:
            print(e)
          
    return redirect("conversion", project_link)