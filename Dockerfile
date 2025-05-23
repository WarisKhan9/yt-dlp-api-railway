FROM python:3.10-slim

WORKDIR /app

COPY cookies.txt .
COPY server.py .

RUN pip install flask yt-dlp

EXPOSE 8080

CMD ["python", "server.py"]