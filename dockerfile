# Pulls an image endowed with minizinc
FROM minizinc/minizinc:latest

# Setting the working directory for the container
WORKDIR /src

# Copy all the files of our project to the container
COPY . .

# Install libraries
RUN apt-get update \
    && apt-get install -y python3 \
    && apt-get install -y python3-pip \
    && python3 -m pip install -r requirements.txt

CMD python3 CP/src/solve_cp.py

# docker build . -t <name_image> // to build
# docker run -v local_machine_path:container_path // to run the image with an specified volume
# docker run -it -d -v local_machine_path:container_path // to run persist the execution of a container in the background to use a terminal

# -it -> interactive terminal
# -d -> daemon (run in the background)
# -v -> specify volume