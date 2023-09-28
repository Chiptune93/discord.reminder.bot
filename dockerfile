FROM python:3.10.8-buster
COPY . /app
WORKDIR /app
RUN pip3 install -r requirement.txt
ENTRYPOINT ["python3"]
CMD ["main.py"]
