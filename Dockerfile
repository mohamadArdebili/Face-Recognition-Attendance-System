FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libopenblas0 \
    libgomp1 \
    libglib2.0-0 \
    libx11-6 \
    libpng16-16 \
    libjpeg62-turbo \
    libwebp7 \
    liblapack3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements_pa.txt .
COPY wheels/ wheels/

RUN pip install --no-cache-dir flask==3.0.3 flask-cors==4.0.0 gunicorn==22.0.0 \
    python-dotenv==1.0.1 numpy==1.26.4 Pillow==10.4.0 \
    opencv-python-headless==4.10.0.84

RUN pip install --no-cache-dir wheels/dlib-19.24.6-cp310-cp310-linux_x86_64.whl

RUN pip install --no-cache-dir face-recognition==1.3.0

RUN python3 -c "import dlib; print('dlib OK')"

COPY . .
RUN mkdir -p data logs

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "120", "wsgi:application"]
