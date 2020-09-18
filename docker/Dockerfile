FROM docker.io/python
MAINTAINER meisanggou


ADD https://raw.githubusercontent.com/meisanggou/wildzh/exam/requirement.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirement.txt -i https://mirrors.aliyun.com/pypi/simple/ && \
    pip install --no-cache-dir gevent gunicorn  -i https://mirrors.aliyun.com/pypi/simple/ && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

ENV WILDPATH /opt/wildzh
ENV PYTHONPATH $WILDPATH
ENV LISTENPORT 2402
WORKDIR $WILDPATH

ADD Dockerfile /root
ADD entrypoint.sh /opt/
RUN chmod a+x /opt/entrypoint.sh
ENTRYPOINT ["/opt/entrypoint.sh"]
# CMD ["python3", "wildzh/web02/web.py", "$LISTENPORT"]
# CMD ["gunicorn", "-b", "0.0.0.0:$LISTENPORT", "-w", "4", "-k", "eventlet", "--chdir", "wildzh/web02", "web:app"]
CMD ["gunicorn", "-b", "0.0.0.0:$LISTENPORT", "-w", "4", "-k", "gevent", "--chdir", "wildzh/web02", "web:app"]
