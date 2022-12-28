# Use the official lightweight Python image.
FROM python:3.9-slim
# Necessary for GCP
EXPOSE 8080
# Allow statements and log 
ENV PYTHONUNBUFFERED True
# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./
# Install production dependencies.
RUN pip install -r requirements.txt
# Run
ENTRYPOINT ["streamlit", "run", "WCA_NR.py", "--server.port=8080", "--server.address=0.0.0.0"]
