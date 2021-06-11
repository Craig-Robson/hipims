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
RUN pip install hipims_io==0.4.9

# Set CUDA_ROOT
ENV CUDA_ROOT /usr/local/cuda/bin
RUN apt-get install -y wget cmake python3-pip

# get hipims code, input data, and python script to setup and run hipims model
RUN mkdir -p /hipims
COPY apps /hipims/apps
COPY hipims_io /hipims/hipims_io
COPY lib /hipims/lib
COPY Newcastle /hipims/Newcastle
COPY CMakeLists.txt /hipims
COPY LICENSE.txt /hipims
#RUN pwd
# compile hipims model
WORKDIR hipims
RUN cmake . -DCMAKE_BUILD_TYPE=Release  && \
    make -j"$(nproc)"

# create input folder and files for HiPIMS
# Change the number to specify the number of GPUs to be used
RUN python Newcastle/generate_ncl_inputs.py 1

#CMD ["git", "pull"] # renew codes from github repo https://github.com/flood-PREPARED/hipims.git
#CMD ["ls Newcastle/"]
#CMD ["python3" "Newcastle/generate_ncl_inputs.py"]

# create a data dir (this is where DAFNI will check for the data)
RUN mkdir /data
RUN mkdir /data/outputs
#Mount output directories. Must be container directory
VOLUME /hipims/Outputs

# Entrypoint, comment out either one of the CMD instructions
# Run on local
# CMD git pull && python3 Newcastle/run_NCL_2m_MG.py && python3 Newcastle/combine_mgpu_results.py
# Run through Kafka messaging
CMD python3 -u Newcastle/run.py
