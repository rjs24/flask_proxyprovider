FROM alpine:latest
RUN apk update
RUN apk add --no-cache --virtual build-dependencies python3 \
    && apk add --virtual build-runtime \
    build-base python3-dev openblas-dev freetype-dev pkgconfig gfortran libxml2-dev libxslt-dev gcc \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && ln -sf pip3 /usr/bin/pip \
    && rm -r /root/.cache
COPY ./ ./app
WORKDIR  ./app
EXPOSE 5000
RUN pip3 install -r requirements.txt
RUN ["chmod", "+x", "./src/main.py"]
CMD ["python3", "./src/main.py"]