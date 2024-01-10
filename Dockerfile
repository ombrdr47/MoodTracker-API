# First stage: Build the application
FROM python:3.7-alpine3.9 AS builder

RUN apk update && apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev

WORKDIR /app

COPY requirements.txt .
RUN python3 -m venv venv && \
    source venv/bin/activate && \
    venv/bin/pip install --no-cache-dir --upgrade pip && \
    venv/bin/pip install --no-cache-dir -r requirements.txt


# Second stage: Create the final image
FROM python:3.7-alpine3.9

RUN apk update && apk add --no-cache libstdc++

RUN adduser -D -g '' admin
WORKDIR /home/MoodTracker

COPY --from=builder /app/venv venv
COPY --from=builder /app/app app
COPY --from=builder /app/migrations migrations
COPY --from=builder /app/mood_tracker.py .
COPY --from=builder /app/config.py .
COPY --from=builder /app/boot.sh .
RUN chmod +x boot.sh

ENV FLASK_APP=mood_tracker.py
USER admin

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]

CMD ["gunicorn", "-b", ":5000", "mood_tracker:app"]
