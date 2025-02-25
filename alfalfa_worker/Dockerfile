FROM michaelwetter/ubuntu-1804_jmodelica_trunk

USER root
ENV HOME /home/alfalfa

WORKDIR /alfalfa

RUN apt-get update -y && apt-get install -y \
    ca-certificates curl libglu1 libjpeg8 libfreetype6 libxi6 libdbus-glib-1-2 libfontconfig1 libsm6 gdebi-core python3 python3-pip \
    && apt-get install -y git

RUN apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository -y ppa:openjdk-r/ppa \
    && apt-get update -y \
    && apt-get install -y openjdk-8-jdk-headless \
    && update-alternatives --config java \
    && update-alternatives --config javac \
    && curl -SLO http://openstudio-resources.s3.amazonaws.com/bcvtb-linux.tar.gz \
    && tar -xzf bcvtb-linux.tar.gz \
    && apt-get install -y ca-certificates nodejs

ENV SPAWN_DOWNLOAD_BASE_URL https://spawn.s3.amazonaws.com/builds
ENV SPAWN_DOWNLOAD_FILENAME Spawn-0.0.1-1ad59a6dbf-Linux.tar.gz
ENV SPAWN_DOWNLOAD_URL ${SPAWN_DOWNLOAD_BASE_URL}/${SPAWN_DOWNLOAD_FILENAME}

ENV OPENSTUDIO_DOWNLOAD_FILENAME OpenStudio-3.1.0+e165090621-Linux.deb
ENV OPENSTUDIO_DOWNLOAD_URL https://github.com/NREL/OpenStudio/releases/download/v3.1.0/OpenStudio-3.1.0+e165090621-Linux.deb

ENV ENERGYPLUS_VERSION 9.4.0
ENV ENERGYPLUS_TAG v9.4.0
ENV ENERGYPLUS_SHA 998c4b761e

# mlep / external interface needs parts of EnergyPlus that are not included with OpenStudio
# expandobjects, runenergyplus might be two examples, but the need to install EnergyPlus separately from OpenStudio
# might be revaluated
ENV ENERGYPLUS_DOWNLOAD_BASE_URL https://github.com/NREL/EnergyPlus/releases/download/$ENERGYPLUS_TAG
ENV ENERGYPLUS_DOWNLOAD_FILENAME EnergyPlus-$ENERGYPLUS_VERSION-$ENERGYPLUS_SHA-Linux-Ubuntu18.04-x86_64.tar.gz
ENV ENERGYPLUS_DOWNLOAD_URL $ENERGYPLUS_DOWNLOAD_BASE_URL/$ENERGYPLUS_DOWNLOAD_FILENAME

# Extract Spawn executable
RUN curl -SLO ${SPAWN_DOWNLOAD_URL} \
    && mkdir /usr/local/Spawn-0.0.1 \
    && tar -C /usr/local/Spawn-0.0.1/ --strip-components=1 -xzf ${SPAWN_DOWNLOAD_FILENAME} \
    && ln -s /usr/local/Spawn-0.0.1/bin/spawn /usr/local/bin/ \
    && rm ${SPAWN_DOWNLOAD_FILENAME}
RUN spawn --version


# We would rather use the self extracting tarball distribution of EnergyPlus, but there appears to
# be a bug in the installation script so using the tar.gz manually here and making our own links
RUN curl -SLO $ENERGYPLUS_DOWNLOAD_URL \
    && mkdir /usr/local/EnergyPlus-9-4-0 \
    && tar -C /usr/local/EnergyPlus-9-4-0/ --strip-components=1 -xzf $ENERGYPLUS_DOWNLOAD_FILENAME \
    && ln -s /usr/local/EnergyPlus-9-4-0/energyplus /usr/local/bin/ \
    && ln -s /usr/local/EnergyPlus-9-4-0/ExpandObjects /usr/local/bin/ \
    && ln -s /usr/local/EnergyPlus-9-4-0/runenergyplus /usr/local/bin/ \
    && rm $ENERGYPLUS_DOWNLOAD_FILENAME

RUN curl -SLO $OPENSTUDIO_DOWNLOAD_URL \
    && gdebi -n $OPENSTUDIO_DOWNLOAD_FILENAME \
    && rm -f $OPENSTUDIO_DOWNLOAD_FILENAME

# Need to set the lang to use Python 3.6 with Poetry
ENV  LANG C.UTF-8
COPY pyproject.toml /alfalfa/
COPY poetry.lock /alfalfa/
COPY alfalfa_worker/requirements/py2-production.txt /alfalfa/
# Reinstall/upgrade setuptools because this is needed for symfit (used in E+ Python)
# Line 3 below installs python packages to the system and not in a virtualenv.
RUN  python3 -m pip install --upgrade pip setuptools && \
     python3 -m pip install poetry==1.1.4 && \
     python3 -m poetry config virtualenvs.create false && \
     python3 -m poetry install --no-dev
# Python 2 dependencies
RUN  python -m pip install --ignore-installed -r /alfalfa/py2-production.txt

# Include the path to where alfalfa_worker is so that system calls can find it.
ENV  PYTHONPATH="/alfalfa:${PYTHONPATH}"

COPY . /alfalfa
COPY ./deploy/wait-for-it.sh /usr/local/wait-for-it.sh
COPY ./deploy/start_worker.sh start_worker.sh

WORKDIR /alfalfa/alfalfa_worker
RUN tar -czf workflow.tar.gz workflow

ENV ROOT_DIR /usr/local
ENV JMODELICA_HOME $ROOT_DIR/JModelica
ENV IPOPT_HOME $ROOT_DIR/Ipopt-3.12.4
ENV SUNDIALS_HOME $JMODELICA_HOME/ThirdParty/Sundials
ENV SEPARATE_PROCESS_JVM /usr/lib/jvm/java-8-openjdk-amd64/
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
ENV PYTHONPATH $PYTHONPATH:$JMODELICA_HOME/Python:$JMODELICA_HOME/Python/pymodelica

CMD [ "/alfalfa/start_worker.sh" ]
