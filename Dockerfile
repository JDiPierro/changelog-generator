FROM python:2.7.14-alpine3.7

WORKDIR /app

COPY requirements.pip ./
RUN pip install --no-cache-dir -r requirements.pip

COPY changelog_generator .

ENV YAMLCLOG_INPUT /project/changelogs
ENV YAMLCLOG_MARKDOWN /project/CHANGELOG.md

ENTRYPOINT ["python", "generate_changelog.py"]
