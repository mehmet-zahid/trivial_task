FROM cypress/browsers:latest

SHELL ["/bin/bash", "-c"]
ENV APP_PORT=443

# this is for the non-interactive shell to load .bashrc file 
ENV BASH_ENV=/root/.bashrc

#ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        curl \
        ca-certificates \
        build-essential \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        llvm \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        libxml2-dev \
        libxmlsec1-dev \
        libffi-dev \
        liblzma-dev \
        wget

ARG PYTHON_VERSION=3.11.2

COPY . /api
WORKDIR /api

# Install pyenv python and packages
RUN curl https://pyenv.run | bash && \
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc && \
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc && \
    echo 'export PATH="$PYENV_ROOT/shims:$PATH"' >> ~/.bashrc && \
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile && \
    echo 'export PATH="$PYENV_ROOT/shims:$PATH"' >> ~/.profile && \
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile && source ~/.bashrc && \
    pyenv install $PYTHON_VERSION && \
    pyenv global $PYTHON_VERSION && \
    pip install -r requirements.txt

# Set environment variables
#ENV PYENV_ROOT=/root/.pyenv
#ENV PATH=/root/.pyenv/shims:$PATH
#ENV PATH=/root/.pyenv/bin:$PATH