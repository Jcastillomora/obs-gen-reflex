
FROM python:3.11 as init
WORKDIR /app

COPY requirements.txt .

ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python3 -m venv $VIRTUAL_ENV && \
    pip install -r requirements.txt

COPY . .

RUN reflex export

EXPOSE 8000
EXPOSE 3000

CMD ["reflex", "run", "--env", "prod"]