# Build image based on ubuntu 18.04
FROM ubuntu:18.04

# Install python and pip
RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get install -y python3 && \
	apt-get install -y python3-pip

# Install required modules	
RUN pip3 install pandas && \
	pip3 install requests && \
	pip3 install elementpath && \
	pip3 install xlsxwriter

# Create directories	
RUN mkdir /home/oecd_dataset_processor && \
	mkdir /home/oecd_dataset_processor/output

# Copy files from Docker file directory to image directory
COPY . /home/oecd_dataset_processor

# Run entrypoint script as soon as container is run
ENTRYPOINT python3 /home/oecd_dataset_processor/oecd_dataset_processor.py ${DATASET_ID} /home/oecd_dataset_processor/output ${SAVE_MODE} ${HOST_WORK_DIR}