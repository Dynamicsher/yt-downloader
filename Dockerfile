FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3.11-dev python3-pip \
    git zip unzip openjdk-11-jdk \
    autoconf libtool pkg-config \
    cmake libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Make python3.11 the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
RUN python3.11 -m pip install --upgrade pip
RUN python3.11 -m pip install \
    buildozer==1.5.0 \
    cython==0.29.33 \
    "python-for-android==2023.09.16"
