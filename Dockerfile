FROM python:3.12

WORKDIR /admin

COPY requirements.txt /admin/
RUN pip install -r requirements.txt

COPY . /admin/
