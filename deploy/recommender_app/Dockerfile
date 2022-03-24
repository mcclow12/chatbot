FROM clearlinux/numpy-mp:latest

COPY requirements.txt .

RUN swupd bundle-add c-basic && \
    pip install -r requirements.txt && \
	rm requirements.txt

EXPOSE 100

COPY ./app /app

WORKDIR /

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "100"]
