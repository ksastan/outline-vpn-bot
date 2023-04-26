FROM python:3.7
ENV TELEGRAM_API_TOKEN=''
ENV OUTLINE_API_URL=''
ENV AUTHORIZED_IDS=''
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
COPY . /app
CMD python /app/main.py
