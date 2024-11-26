# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

#COPY favicon.ico /


COPY python_packages /python_packages
RUN pip install --no-cache-dir --find-links=/python_packages -r requirements.txt


EXPOSE 8501

CMD ["streamlit", "run", "Fintech_Insights.py"]


#ENTRYPOINT ["streamlit", "run", "Fintech_Insights.py", "--server.port=8080", "--server.address=0.0.0.0"]