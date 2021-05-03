FROM python:3.8

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
RUN pytest tests

EXPOSE 5001
CMD python app.py
