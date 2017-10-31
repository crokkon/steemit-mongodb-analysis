FROM python:3

RUN pip install -U steemdata
RUN sed -i 's/(==0.9.3.1)/(==0.9.3)/g' /usr/local/lib/python3.6/site-packages/steem*/METADATA
RUN pip install -U matplotlib
RUN mkdir -p /steemdata/
ADD query_database.py /
ADD analyze.py /
ENTRYPOINT python query_database.py && python analyze.py
