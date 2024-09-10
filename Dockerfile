FROM ubuntu:22.04
LABEL maintainer="AaronPB"

# Install base dependencies and Python 3.10 (default on ubuntu 22.04)
RUN apt-get update && apt-get install -y \
    curl \
    software-properties-common \
    python3 \
    python3-pip

# MRPT requires tzdata package to be configured
RUN apt-get update && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata

# Install dependencies
## Phidget
RUN curl -fsSL https://www.phidgets.com/downloads/setup_linux | bash &&\
    apt-get install -y libphidget22

## MRPT
RUN add-apt-repository ppa:joseluisblancoc/mrpt
RUN apt-get update && apt-get install -y \
    libmrpt-dev \
    mrpt-apps \
    python3-pymrpt

# Install python and python dependencies
COPY requirements-dev.txt requirements-dev.txt
COPY requirements.txt requirements.txt

# Use python3 -m pip to install dependencies
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements-dev.txt

# Define workdir and copy project
ENV prj_dir=/app/
WORKDIR ${prj_dir}
COPY . ${prj_dir}

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_store/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
