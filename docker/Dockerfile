FROM continuumio/miniconda3

RUN apt-get update
RUN apt-get install sudo
RUN apt-get install -y x11-apps
RUN apt-get install 'ffmpeg'\
    'libsm6'\ 
    'libxext6'  -y
RUN apt-get install -y libqt5gui5 && \
    rm -rf /var/lib/apt/lists/*
ENV QT_DEBUG_PLUGINS=1


RUN git clone -b 61-create-docker-image "https://github.com/matmulmiller/TRANSONIC" /root/TRANSONIC


#RUN ~/miniconda3/bin/conda init bash
RUN conda env create -f /root/TRANSONIC/environment.yml
RUN conda init
RUN echo "conda activate transonic_env" >> ~/.bashrc
RUN echo "cd ~/TRANSONIC/" >> ~/.bashrc
