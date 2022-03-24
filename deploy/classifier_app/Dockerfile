FROM pytorch/torchserve:latest-cpu

COPY requirements.txt .

COPY config.txt /tmp

COPY ./model_store /tmp/models

RUN pip install --upgrade pip && \ 
    pip install -r requirements.txt && \
	rm requirements.txt

EXPOSE 8080

WORKDIR /


CMD ["torchserve", "--model-store=/tmp/models", "--start", "--ncs", "--models", "OnnxClassifier.mar", "--ts-config",  "/tmp/config.txt"]
