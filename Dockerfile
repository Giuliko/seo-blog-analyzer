FROM mcr.microsoft.com/playwright/python:v1.43.1-jammy

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    xvfb \
    ffmpeg \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    && apt-get clean

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN playwright install --with-deps

CMD ["xvfb-run", "--auto-servernum", "--", "python", "xp_blog_scraper.py"]
