#Fintech Chatbot Using Generative AI with Vertex AI

This repository contains the code and instructions for building a Fintech chatbot powered by Generative AI using Google Cloud Vertex AI. 
The chatbot leverages Vertex AI for dynamic insights, BigQuery for scalable financial data querying, and Streamlit for an interactive user interface. 
Deployment is handled via Google Cloud Run for a seamless serverless experience.

===================================================================================================================================

Medium Blog - https://medium.com/@bharathi72826/building-a-fintech-chatbot-using-generative-ai-with-vertex-ai-83e8c2e2d13a 

===================================================================================================================================
Building a Fintech Chatbot Using Generative AI with Vertex AI


How to leverage Google Cloud’s Vertex AI to create an intelligent chatbot for fintech applications.

Introduction | Overview
In the ever-evolving fintech landscape, delivering exceptional customer support is critical. Chatbots powered by Generative AI offer a scalable solution to automate user interactions, improve customer experience, and streamline operations.

This blog demonstrates how to build a Fintech Chatbot using Google Cloud Vertex AI, focusing on its Generative AI capabilities. Whether you’re a fintech enthusiast, a developer, or a product manager, this guide will help you understand the steps required to create and deploy an intelligent chatbot tailored to the needs of financial applications.

Problem statement: Financial institutions need efficient, secure, and reliable customer service solutions.

Target audience: Developers and tech-savvy professionals familiar with Python, Streamlit, BigQuery, and cloud platforms.

Final outcome: By the end of this blog, you’ll have a functioning Fintech Chatbot deployed via Vertex AI.

System Design
The architecture of the Fintech Chatbot involves the integration of Vertex AI, BigQuery, and a Streamlit API hosted on Google Cloud Run. This design ensures scalability, security, and seamless query handling for financial data.

Requirements:
High-level design:
Vertex AI for Generative AI model serving.
BigQuery for secure and scalable financial data querying.
Streamlit API for the chatbot backend.
Cloud Run for deployment.
Design rationale:
Generative AI enhances user interaction with dynamic, contextual responses.
BigQuery ensures data integrity and supports large-scale analytics.
Cloud Run offers serverless deployment, reducing operational overhead.

Simple flowchart-style diagram for the Fintech Chatbot system
Prerequisites
Before starting, ensure you have the following:

Software & Tools:
Google Cloud account with Vertex AI and BigQuery enabled.
Python 3.8+ installed locally.
Streamlit API development.
BigQuery datasets for testing.
Knowledge:
Familiarity with API’s.
Basic understanding of Generative AI concepts.
Prior experience with Google Cloud services (BigQuery, Vertex AI).
Step-by-step Instructions
1. Set Up Your Google Cloud Environment
Create a BigQuery dataset and upload sample financial data for queries.
Here I have used a python script to generate the bank transactions data.
import csv
import random
from datetime import datetime, timedelta

# Define categories and descriptions
categories = {
    "Groceries": "Supermarket Bill",
    "Entertainment": "Movie Ticket",
    "Rent": "Monthly Rent",
    "Utilities": "Electricity Bill",
    "Dining": "Restaurant Bill",
    "Travel": "Flight Ticket",
    "Shopping": "Online Purchase",
    "Miscellaneous": "Other Expenses"
}

# Generate random date
def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

# Generate dataset
rows = []
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 1, 1)

for i in range(1000):
    account_id = f"ACC{random.randint(100, 200)}"
    transaction_date = random_date(start_date, end_date).strftime('%Y-%m-%d')
    amount = round(random.uniform(10, 2000), 2)
    category = random.choice(list(categories.keys()))
    description = categories[category]
    rows.append([account_id, transaction_date, amount, category, description])

# Save to CSV
with open("transactions.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["account_id", "transaction_date", "amount", "category", "description"])  # Header
    writer.writerows(rows)

print("transactions.csv has been created successfully!")
Download the file to local system and upload it to big query as a SQL Database.

Enable APIs: Vertex AI, BigQuery, and Cloud Run.
Here I have written all the files locally, used docker to push them to google cloud.

Specifying the requirements.txt file for docker to preinstall required modules and libraries

#requirements.txt file
google-cloud-bigquery
gunicorn
google-cloud-aiplatform
streamlit
queries.py file to fetch the data from bigquery

# queries.py

import re

def get_transactions_query(account_id):
    """
    Fetch transactions for a specific account ID.
    """
    # Sanitize account_id to prevent injection or formatting errors
    sanitized_account_id = re.sub(r"[^a-zA-Z0-9_-]", "", account_id)
    return f"""
    SELECT *
    FROM `fintechchatbot.fintech_data.transactions`
    WHERE account_id = '{sanitized_account_id}'
    """
main.py file to fetch the user input and also connect to Aertex AI — Here I have named it as Fintech_Insights.py

import streamlit as st
from google.cloud import bigquery
import vertexai
import queries
from vertexai.generative_models import GenerativeModel, SafetySetting
import pandas as pd

# Explicitly set your Google Cloud project ID
PROJECT_ID = "fintechchatbot"

# Initialize BigQuery client with project ID
client = bigquery.Client(project=PROJECT_ID)

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location="us-central1")
generative_model = GenerativeModel("gemini-1.5-pro-002")

# Safety settings for the generative AI
safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF,
    ),
]

# Generation configuration
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}


def get_transactions(account_id):
    """
    Fetches transactions for a specific account and enhances them with AI insights.
    """
    try:
        # Fetch transactions from BigQuery
        query = queries.get_transactions_query(account_id)
        query_job = client.query(query)
        results = query_job.result()

        transactions = [
            {
                "account_id": row.account_id,
                "transaction_date": str(row.transaction_date),
                "amount": row.amount,
                "category": row.category,
                "description": row.description,
            }
            for row in results
        ]

        # Generate insights using Generative AI
        prompt = f"Analyze the following transactions and provide a concise summary, detailed analysis, and recommendations on personal loan approval.  {account_id}:\n{transactions}"
        ai_response = generative_model.generate_content(
            [prompt], generation_config=generation_config, stream=False
        )

        return transactions, ai_response.text

    except Exception as e:
        st.error(f"Failed to process transactions: {str(e)}")
        return None, None


def total_spend():
    """
    Fetches total spend for all accounts.
    """
    try:
        # Fetch total spend from BigQuery
        query = queries.total_spend_query()
        query_job = client.query(query)
        results = query_job.result()

        spend_summary = [
            {"account_id": row.account_id, "total_spend": row.total_spend}
            for row in results
        ]

        return spend_summary

    except Exception as e:
        st.error(f"Failed to process total spend: {str(e)}")
        return None


st.title("Fintech Chatbot with AI Insights")

'''Note: Account numbers range from **ACC100** to **ACC200**'''
'''Date Range currently Available for Analysis : **01-Jan-2023** to **01-Jan-2024**'''
'''Region : **US**'''
'''**Enter Account ID**'''

# Get account ID from user input
account_id = st.text_input("")


if account_id:
    # Get transactions and insights
    transactions, insights = get_transactions(account_id)

    if transactions and insights:
        st.header("Transactions for Account ID: {}".format(account_id))
        st.dataframe(transactions)

        # Create a DataFrame from the transactions data
        df = pd.DataFrame(transactions)

        # Display data range
        st.write(f"Data Range: {df['transaction_date'].min()} to {df['transaction_date'].max()}")

        # Display total transaction count
        st.write(f"Total Transactions: {len(df)}")

        # Display transaction count by category
        category_counts = df['category'].value_counts()
        st.write("Transaction Count by Category:")
        st.dataframe(category_counts)

        st.markdown("**AI Insights:**")
        st.write(insights)
    else:
        st.warning("No Account found with specified Account number : Please try in the available range.")
Finally a docker file to create the image and push it to cloud.

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
Save all the files in single directory to avoid issues.

Next we shall run the commands to set up necessary permissions and build and docker image.

Login to the Google cloud and get the access

PS D:\> cd '.\All Folders\'
PS D:\All Folders> CD .\fintech_chatbot\
PS D:\All Folders\fintech_chatbot> gcloud auth application-default login
Your browser has been opened to visit:

    https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A8085%2F&scope=openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fsqlservice.login&state=XumAJ8BObFt4g73H8Xx4Y0HBUy1wHS&access_type=offline&code_challenge=FXdTbDQMbedU3ZES8xtY-tQQtx1U7ONJ4PyQMDWPK8E&code_challenge_method=S256


Credentials saved to file: [C:\Users\Lenovo\AppData\Roaming\gcloud\application_default_credentials.json]

These credentials will be used by any library that requests Application Default Credentials (ADC).

Quota project "fintechchatbot" was added to ADC which can be used by Google client libraries for billing and quota. Note that some services may still bill the project owning the resource.
PS D:\All Folders\fintech_chatbot>
Cross verify if all the API’s are enabled.

PS D:\All Folders\fintech_chatbot> gcloud services list --enabled
NAME                                 TITLE
aiplatform.googleapis.com            Vertex AI API
analyticshub.googleapis.com          Analytics Hub API
artifactregistry.googleapis.com      Artifact Registry API
bigquery.googleapis.com              BigQuery API
bigqueryconnection.googleapis.com    BigQuery Connection API
bigquerydatapolicy.googleapis.com    BigQuery Data Policy API
bigquerymigration.googleapis.com     BigQuery Migration API
bigqueryreservation.googleapis.com   BigQuery Reservation API
bigquerystorage.googleapis.com       BigQuery Storage API
cloudaicompanion.googleapis.com      Gemini for Google Cloud API
cloudapis.googleapis.com             Google Cloud APIs
cloudresourcemanager.googleapis.com  Cloud Resource Manager API
cloudtrace.googleapis.com            Cloud Trace API
compute.googleapis.com               Compute Engine API
containerregistry.googleapis.com     Container Registry API
datacatalog.googleapis.com           Google Cloud Data Catalog API
dataflow.googleapis.com              Dataflow API
dataform.googleapis.com              Dataform API
dataplex.googleapis.com              Cloud Dataplex API
datastore.googleapis.com             Cloud Datastore API
deploymentmanager.googleapis.com     Cloud Deployment Manager V2 API
iam.googleapis.com                   Identity and Access Management (IAM) API
iamcredentials.googleapis.com        IAM Service Account Credentials API
logging.googleapis.com               Cloud Logging API
monitoring.googleapis.com            Cloud Monitoring API
notebooks.googleapis.com             Notebooks API
oslogin.googleapis.com               Cloud OS Login API
pubsub.googleapis.com                Cloud Pub/Sub API
retail.googleapis.com                Vertex AI Search for Retail API
run.googleapis.com                   Cloud Run Admin API
servicemanagement.googleapis.com     Service Management API
serviceusage.googleapis.com          Service Usage API
sql-component.googleapis.com         Cloud SQL
storage-api.googleapis.com           Google Cloud Storage JSON API
storage-component.googleapis.com     Cloud Storage
storage.googleapis.com               Cloud Storage API
visionai.googleapis.com              Vision AI API
PS D:\All Folders\fintech_chatbot>
Build the docker image — Make sure that docker is running in local desktop.

PS D:\All Folders\fintech_chatbot> docker build -t fintech-chatbot .
[+] Building 362.0s (11/11) FINISHED                                                                                                                   docker:desktop-linux
 => [internal] load build definition from Dockerfile                                                                                                                   0.1s
 => => transferring dockerfile: 605B                                                                                                                                   0.0s
 => [internal] load metadata for docker.io/library/python:3.11-slim-buster                                                                                             2.4s
 => [auth] library/python:pull token for registry-1.docker.io                                                                                                          0.0s
 => [internal] load .dockerignore                                                                                                                                      0.0s
 => => transferring context: 2B                                                                                                                                        0.0s
 => [1/5] FROM docker.io/library/python:3.11-slim-buster@sha256:c46b0ae5728c2247b99903098ade3176a58e274d9c7d2efeaaab3e0621a53935                                       0.1s
 => => resolve docker.io/library/python:3.11-slim-buster@sha256:c46b0ae5728c2247b99903098ade3176a58e274d9c7d2efeaaab3e0621a53935                                       0.1s
 => [internal] load build context                                                                                                                                      0.0s
 => => transferring context: 2.74kB                                                                                                                                    0.0s
 => CACHED [2/5] WORKDIR /app                                                                                                                                          0.0s
 => CACHED [3/5] COPY . /app                                                                                                                                           0.0s
 => CACHED [4/5] COPY python_packages /python_packages                                                                                                                 0.0s
 => [5/5] RUN pip install --no-cache-dir --find-links=/python_packages -r requirements.txt                                                                           310.5s
 => exporting to image                                                                                                                                                46.7s
 => => exporting layers                                                                                                                                               32.9s
 => => exporting manifest sha256:a930e75978c252cef42609310f06db48c3e49a23b73756c2e6324d8826b0995a                                                                      0.0s
 => => exporting config sha256:e8b232352afcf91872018b156245a14850a67353f2c96b33b5e0522fff5ac07e                                                                        0.0s
 => => exporting attestation manifest sha256:03dba8a4f1c9d2546c4c53aa2116e49effa33159d002e18a218736c206a7fa0e                                                          0.1s
 => => exporting manifest list sha256:8124555b60420780d50e652b25201f597d66b1853b734ba5b2aadf50396abc73                                                                 0.0s
 => => naming to docker.io/library/fintech-chatbot:latest                                                                                                              0.0s
 => => unpacking to docker.io/library/fintech-chatbot:latest                                                                                                          13.4s
PS D:\All Folders\fintech_chatbot>
Push the docker image to cloud

PS D:\All Folders\fintech_chatbot> docker tag fintech-chatbot gcr.io/fintechchatbot/fintech-chatbot
PS D:\All Folders\fintech_chatbot> docker push gcr.io/fintechchatbot/fintech-chatbot
Using default tag: latest
The push refers to repository [gcr.io/fintechchatbot/fintech-chatbot]
724b30a16eec: Layer already exists
7997264534ef: Layer already exists
af247aac0764: Layer already exists
10c990f49486: Layer already exists
2ab95eeda4fb: Layer already exists
af0fdd10dd6b: Pushed
505b0407da24: Pushed
c3cc7b6f0473: Layer already exists
73f8983e760e: Layer already exists
caf069fdc3b3: Pushed
b2b31b28ee3c: Layer already exists
2112e5e7c3ff: Layer already exists
latest: digest: sha256:06a39cee4a7d1082d481d2e287e28538f00001357c386d7f0aed58cf39b2ad47 size: 856
PS D:\All Folders\fintech_chatbot>
Run the docker image

PS D:\All Folders\fintech_chatbot> docker run -p 8501:8501 -v C:/Users/Lenovo/AppData/Roaming/gcloud:/root/.config/gcloud -e GOOGLE_APPLICATION_CREDENTIALS="/root/.config/gcloud/application_default_credentials.json" fintech-chatbot

Collecting usage statistics. To deactivate, set browser.gatherUsageStats to false.


  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://172.17.0.2:8501
  External URL: http://152.59.199.226:8501
If you see the URL, then your code is working fine.

Open the Local URL — http://localhost:8501


UI for our FintechChatBot
Once you are at this page — start querying the details based on account id.




We should be able to see the AI generated Analysis on the user transaction data and recommendations on loan Approval.

In Google Cloud console — under cloud run — we can get the Public URL to access it in any device.

Please feel free to build versions of it and make use of it.

A Big thank you for the google and code Upasana for hosting the Build and Blog Marathon — In Person Event at Hyderabad Google office.

Karan Mittal Thank you :-). It wouldn’t have been possible without your guidance.

To learn more about Google Cloud services and to create impact for the work you do, get around to these steps right away:
Register for Code Vipassana sessions: [https://rsvp.withgoogle.com/events/cv]
Join the meetup group Datapreneur Social: [https://www.meetup.com/datapreneur-social/]
Sign up to become a Google Cloud Innovator: [Google Cloud Innovator]
Expanding on the Project:

Explore Advanced Features: Delve deeper into the capabilities of [specific Google Cloud service] to optimize your solutions.
Integrate with Other Services: Combine [specific Google Cloud service] with other services to create more powerful and comprehensive applications.
Optimize for Performance: Fine-tune your project’s performance and cost-efficiency by leveraging Google Cloud’s advanced tools and techniques.
Challenges to Take Your Skills Further:

Participate in Hackathons: Test your skills and collaborate with other developers in challenging and fun environments.
Contribute to Open Source Projects: Share your knowledge and experience by contributing to open-source projects on GitHub.
Earn Certifications: Validate your expertise and advance your career by obtaining Google Cloud certifications.
