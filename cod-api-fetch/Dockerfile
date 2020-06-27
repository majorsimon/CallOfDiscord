FROM python:3

RUN pip install pymongo apscheduler requests

ADD cod.py /
ADD cod-api-fetch.py /

CMD [ "python", "-u", "/cod-api-fetch.py" ]
