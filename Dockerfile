FROM python:3.9-slim-bullseye
SHELL ["/bin/bash", "-c"]
RUN apt update
RUN apt install -y dpkg-dev build-essential python3-dev freeglut3-dev libgl1-mesa-dev libglu1-mesa-dev libgstreamer-plugins-base1.0-dev libgtk-3-dev libjpeg-dev libnotify-dev libpng-dev libsdl2-dev libsm-dev libtiff-dev libwebkit2gtk-4.0-dev libxtst-dev p7zip-full
COPY requirements.txt /tmp
RUN python -m pip install -r /tmp/requirements.txt
CMD ["/bin/bash", "/save-game-backup-tool/build-linux.sh"]
