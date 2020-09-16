FROM nvidia/cuda:10.1-devel-ubuntu18.04
# install anaconda and required packages for python scripts
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git mercurial subversion

RUN wget --quiet https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-x86_64.sh -O ~/anaconda.sh && \
    /bin/bash ~/anaconda.sh -b -p /opt/conda && \
    rm ~/anaconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc

# Use python 3.6 due to syntax incompatibility with python 3.7+
RUN conda install python=3.6
RUN conda install -y gdal
RUN conda install -c conda-forge pyshp fiona kafka-python
# install hipims
RUN pip install hipims_io=0.4.9

# Set CUDA_ROOT
ENV CUDA_ROOT /usr/local/cuda/bin
RUN apt-get update && apt-get install -y wget cmake python3-pip

RUN mkdir -p Newcastle_Docker
RUN apt-get update && apt-get install -y git
# get hipims code, input data, and python script to setup and run hipims model
RUN git clone https://github.com/flood-PREPARED/hipims.git
#RUN pwd
# compile hipims model
WORKDIR hipims
RUN cmake . -DCMAKE_BUILD_TYPE=Release  && \
    make -j"$(nproc)"

# create input folder and files for HiPIMS
# Change the number to specify the number of GPUs to be used
RUN python Newcastle/generate_ncl_inputs.py 4

#CMD ["git", "pull"] # renew codes from github repo https://github.com/flood-PREPARED/hipims.git
#CMD ["ls Newcastle/"]
#CMD ["python3" "Newcastle/generate_ncl_inputs.py"]


#Mount output directories. Must be container directory
VOLUME /hipims/Outputs

# Kafka broker address
# Change the second address below to change the Kafka broker address
RUN sed -i 's/10.79.253.132:30002/10.3.224.15:30002/g' Newcastle/KafkaConsumer.py

# Entrypoint, comment out either one of the CMD instructions
# Run on local
# CMD git pull && python3 Newcastle/run_NCL_2m_MG.py && python3 Newcastle/combine_mgpu_results.py
# Run through Kafka messaging
CMD git pull && python3 Newcastle/KafkaConsumer.py
