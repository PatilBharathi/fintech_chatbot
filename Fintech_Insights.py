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