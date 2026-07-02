import sqlite3
import random
import pandas as pd

# --- Configuration ---
TOTAL_CASES = 100
DB_NAME = 'customer_service_data.db'

# Target distribution for 100 cases:
TARGET_SENTIMENT = {
    "Positive": 34,  # ~34%
    "Negative": 38,  # ~38%
    "Neutral": 28   # ~28%
}

def generate_query(sentiment):
    """Generates a query based on the desired sentiment."""
    if sentiment == "Positive":
        queries = [
            "Just wanted to say thank you! Your agent, Sarah, was so helpful and fast.",
            "The product arrived much sooner than expected. Excellent service!",
            "I love the new interface update! It's intuitive and easy to use. Keep up the great work.",
            "Everything worked perfectly right out of the box. Highly recommend this company!",
            "Support was amazing, they solved my issue quickly and professionally."
        ]
        return random.choice(queries)
    elif sentiment == "Negative":
        queries = [
            "I have been waiting for a refund since last week, and no one has updated me.",
            "This billing error is unacceptable! I was charged twice for the same month.",
            "The app keeps crashing whenever I try to upload photos. This needs an immediate fix.",
            "I received the wrong item entirely. The description said red, but it's blue.",
            "Customer service was impossible to reach; kept going through endless menus."
        ]
        return random.choice(queries)
    elif sentiment == "Neutral":
        queries = [
            "What is your return policy for electronics that are opened?",
            "Can you provide documentation on how to integrate this API with a third-party system?",
            "I need help resetting my password and confirming the account details.",
            "Are there any upcoming changes to the subscription tiers I should be aware of?",
            "When is the next batch of Product X expected to be available?"
        ]
        return random.choice(queries)

def generate_response(sentiment):
    """Generates a response that matches or addresses the sentiment."""
    if sentiment == "Positive":
        responses = [
            "We are so glad we could help! Thank you for your kind words and patience.",
            "It was our pleasure! We appreciate your feedback. Have a wonderful day!",
            "You're very welcome! Our team works hard to ensure the best experience possible."
        ]
        return random.choice(responses)
    elif sentiment == "Negative":
        responses = [
            "I sincerely apologize for the inconvenience and billing error. I have escalated this to our finance team for immediate review.",
            "I understand your frustration regarding the app crashing. We are working on an urgent patch and will update you within 24 hours.",
            "We deeply regret that you received the wrong item. Please use this prepaid label, and we will ship the correct blue item immediately."
        ]
        return random.choice(responses)
    elif sentiment == "Neutral":
        responses = [
            "Our standard return policy allows for a full refund within 30 days, provided the item is unused.",
            "Yes, you can find detailed documentation here: [link]. Please ensure you meet the necessary API key requirements.",
            "To reset your password, please use the 'Forgot Password' link on the login page. We will verify your identity via email.",
            "We anticipate a slight change in tiers next quarter; check our official website for full details.",
            "We expect the next batch of Product X to be available by the end of next month."
        ]
        return random.choice(responses)

def generate_data(distribution):
    """Generates the complete dataset list."""
    all_cases = []
    for sentiment, count in distribution.items():
        for i in range(count):
            case = {
                "case_id": 100 + (len(all_cases) + i), # Ensure unique IDs starting high
                "sentiment": sentiment,
                "customer_query": generate_query(sentiment),
                "agent_response": generate_response(sentiment)
            }
            all_cases.append(case)
    return all_cases

def write_to_sqlite(data, db_name):
    """Connects to SQLite and writes the generated data."""
    print("--- Starting Database Write Process ---")
    try:
        # Connect or create the database file
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # 1. Create the table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_cases (
                case_id INTEGER PRIMARY KEY,
                sentiment TEXT NOT NULL,
                customer_query TEXT,
                agent_response TEXT
            )
        """)

        # 2. Prepare data for bulk insertion
        rows = []
        for case in data:
            rows.append((
                case['case_id'],
                case['sentiment'],
                case['customer_query'],
                case['agent_response']
            ))

        # 3. Execute the bulk INSERT operation
        cursor.executemany("""
            INSERT INTO service_cases (case_id, sentiment, customer_query, agent_response)
            VALUES (?, ?, ?, ?)
        """, rows)

        # Commit changes and close the connection
        conn.commit()
        print(f"\n✅ Success! Successfully inserted {len(data)} records into '{db_name}'.")
        
    except sqlite3.Error as e:
        print(f"❌ Database error occurred: {e}")
    finally:
        # Ensure the connection is closed even if errors occur
        if conn:
            conn.close()

# --- Main Execution Block ---
if __name__ == "__main__":
    
    # 1. Generate the 100 synthetic cases
    synthetic_data = generate_data(TARGET_SENTIMENT)
    
    # Verification check
    print("--- Data Generation Summary ---")
    actual_count = pd.Series([c['sentiment'] for c in synthetic_data]).value_counts().sort_index()
    target_summary = {k: v for k, v in TARGET_SENTIMENT.items()}
    
    print(f"Total Cases Generated: {len(synthetic_data)}")
    print("Expected vs Actual Distribution:")
    for sentiment in ["Positive", "Negative", "Neutral"]:
        print(f"- {sentiment:<10}: Target={target_summary[sentiment]:<3} | Actual={actual_count.get(sentiment, 0):<3}")

    # 2. Write the generated data to the SQLite database
    write_to_sqlite(synthetic_data, DB_NAME)
