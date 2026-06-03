FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    git zip unzip openjdk-11-jdk \
    autoconf libtool pkg-config \
    cmake libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install \
    buildozer==1.5.0 \
    cython==0.29.33 \
    "python-for-android==2023.09.16"
