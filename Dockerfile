FROM ubuntu:18.04

MAINTAINER path-help@sanger.ac.uk

ARG DEBIAN_FRONTEND=noninteractive

ARG BUILD_DIR=/tmp/local-install

ARG BLAST_VERSION="2.9.0"
ARG BLAST_DOWNLOAD_FILENAME="ncbi-blast-${BLAST_VERSION}+-x64-linux.tar.gz"
ARG BLAST_PLUS_URL="ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/${BLAST_VERSION}/${BLAST_DOWNLOAD_FILENAME}"

ARG PYFASTQ_VERSION=3.17.0

# Ubuntu
RUN apt-get update -qq -y && \
    apt-get upgrade -qq -y

# Dependencies for singularity and python
RUN apt-get update -qq -y && \
    apt-get install -qq -y \
      python3 \
      python3-pip \
      wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
    

# NCBI blast+
RUN cd /opt && \
    wget -q "$BLAST_PLUS_URL" -O "${BLAST_DOWNLOAD_FILENAME}" && \
    tar xzvf "${BLAST_DOWNLOAD_FILENAME}" && \
    rm "${BLAST_DOWNLOAD_FILENAME}"
ENV PATH "/opt/ncbi-blast-${BLAST_VERSION}+/bin:${PATH}"

# Farm blast
COPY . "${BUILD_DIR}"
RUN cd "${BUILD_DIR}" && \
    pip3 install "pyfastaq==${PYFASTQ_VERSION}" && \
    pip3 install . && \
    rm -rf "${BUILD_DIR}"
