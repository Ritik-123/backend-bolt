FROM python:3.10

WORKDIR /backend_bolt

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "manage.py"]