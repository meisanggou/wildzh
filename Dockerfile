FROM docker.io/python
MAINTAINER meisanggou


ADD https://raw.githubusercontent.com/meisanggou/wildzh/exam/requirement.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirement.txt

ENV WILDPATH /opt/wildzh
ENV PYTHONPATH $WILDPATH
ENV LISTENPORT 2402
WORKDIR $WILDPATH
CMD ["python", "wildzh/web02/web.py", "$LISTENPORT"]
