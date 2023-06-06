FROM python:latest


WORKDIR /HOMECATALOG

COPY requirements.txt /HOMECATALOG
RUN pip install  --no-cache-dir --upgrade -r requirements.txt

COPY . /HOMECATALOG

#CMD ["gunicorn", "-w", "4", "HomeCatalog:app", "--bind", "127.0.0.1:80"]
CMD ["python", "HomeCatalog.py"]