# Specifying base image
FROM python:3.9.0

ARG UID=1000
ARG GID=1000

# Creating the user
RUN groupadd -g "${GID}" dockeruser \
  && useradd --create-home --no-log-init -u "${UID}" -g "${GID}" dockeruser

# Setting environment variables
# For our home directory path
ENV HOME=/home
# Diasbles generation of pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# stdout and stderr streams are not buffered and sent straight to your terminal
ENV PYTHONUNBUFFERED 1

ENV PATH="$PATH:/home/bin"

# Setting work directory
WORKDIR $HOME

# Copying the project data into work directory
COPY . $HOME

# Installing dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Changing ownership of all files and folders in work dir to user
RUN chown -R dockeruser:dockeruser $HOME

# Changing to user
USER dockeruser

# Running Django on 0.0.0.0:8000
CMD gunicorn project.wsgi -b 0.0.0.0:8042

# Exposing port inside the container
EXPOSE 8042
