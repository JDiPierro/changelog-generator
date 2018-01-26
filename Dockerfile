FROM python:2.7.14-alpine3.7

WORKDIR /app

COPY requirements.pip ./
RUN pip install --no-cache-dir -r requirements.pip

COPY changelog_generator .

CMD [ "python", "./generate_changelog.py", "save", "$VERSION", "/changelog_yamls", ]