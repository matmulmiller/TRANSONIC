FROM continuumio/miniconda3

RUN apt-get update
RUN apt-get install sudo
RUN apt-get install 'ffmpeg'\
    'libsm6'\ 
    'libxext6'  -y


RUN git clone -b 61-create-docker-image "https://github.com/matmulmiller/TRANSONIC" /root/TRANSONIC


#RUN ~/miniconda3/bin/conda init bash
RUN conda env create -f /root/TRANSONIC/environment.yml
RUN conda init
RUN echo "conda activate transonic_env" >> ~/.bashrc
RUN echo "cd ~/TRANSONIC/" >> ~/.bashrc
