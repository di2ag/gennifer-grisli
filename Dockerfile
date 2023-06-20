FROM ubuntu:latest

USER root

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y unzip xorg wget curl libstdc++6

# GENNIFER Stuff
RUN apt-get update && apt-get install -y time python3-pip


RUN mkdir /mcr-install && \
    mkdir /opt/mcr && \
    cd /mcr-install && \
    wget -q http://ssd.mathworks.com/supportfiles/downloads/R2019a/Release/0/deployment_files/installer/complete/glnxa64/MATLAB_Runtime_R2019a_glnxa64.zip && \
    cd /mcr-install && \
    unzip MATLAB_Runtime_R2019a_glnxa64.zip && \
    ./install -destinationFolder /opt/mcr -agreeToLicense yes -mode silent && \
    cd / && \
    rm -rf mcr-install

# add app user
RUN groupadd gennifer_user && useradd -ms /bin/bash -g gennifer_user gennifer_user

# Set the working directory to /app
WORKDIR /app

COPY ./requirements.txt /app

# Install the required packages
RUN pip3 install --no-cache-dir -r requirements.txt

# chown all the files to the app user
RUN chown -R gennifer_user:gennifer_user /app

RUN mkdir runGRISLI

COPY runGRISLI/ /app

ENV LD_LIBRARY_PATH /opt/mcr/v96/runtime/glnxa64:/opt/mcr/v96/bin/glnxa64

RUN mkdir -p /root/.mcrCache9.6/GRISLI0/GRISLI/

#RUN cp -r /runGRISLI/spams-matlab-v2.6/ /root/.mcrCache9.6/GRISLI0/GRISLI/

RUN mkdir data/

RUN apt-get update

RUN apt-get install -y libgomp1 --fix-missing

USER gennifer_user

# Copy the current directory contents into the container at /app
COPY . /app

# Start the Flask app
CMD ["flask", "--app", "grisli", "run", "--host", "0.0.0.0", "--debug"]
