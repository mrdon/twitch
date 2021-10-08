FROM python:3.8-slim

ENV PYTHONUNBUFFERED=1

RUN pip install -U pip

WORKDIR /app


COPY requirements.txt .
RUN pip install -r requirements.txt


COPY director /app/director


#
# ARG REVISION_HASH
# ENV REVISION_HASH ${REVISION_HASH}
# RUN echo "REVISION_HASH '$REVISION_HASH'"

EXPOSE 8080/tcp


CMD ["hypercorn", "director.web:app"]
