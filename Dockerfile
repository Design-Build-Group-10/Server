FROM python:3.9-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY . .
ENV PRODUCTION=True
ENV DEBUG=False

RUN apt-get update && \
    apt-get install -y gcc libmariadb-dev pkg-config && \
    apt-get clean

RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000

RUN chmod +x entrypoint.sh

CMD [ "/app/entrypoint.sh" ]