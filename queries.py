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