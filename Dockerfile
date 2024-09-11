FROM ubuntu:jammy
RUN apt update && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install -y keyboard-configuration tzdata
RUN apt install -y gir1.2-appindicator3-0.1 gir1.2-gtk-3.0 libglib2.0-dev p7zip-full python-is-python3 python3 python3-gi python3-pip python3-wxgtk4.0
COPY requirements.txt /tmp
RUN python -m pip install -r /tmp/requirements.txt
CMD ["/bin/bash", "/save-game-backup-tool/build-linux.sh"]
