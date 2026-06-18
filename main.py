from pymongo import MongoClient
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


# ====== CONFIG ======
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "mydb")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "mycollection")

URL_BASE = os.getenv("URL_BASE", "https://chai-api.intel.com/")
URL = URL_BASE + "ask-ChAI"

CLIENT_SECRET = os.getenv("CLIENT_SECRET", "YOUR_CLIENT_SECRET")


# ====== LOAD DATA FROM MONGODB ======
def load_data():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    data = list(collection.find({}))

    # Convert ObjectId to string
    for doc in data:
        doc["_id"] = str(doc["_id"])

    client.close()
    return data


# ====== ASK API ======
def ask_chai(question, data):
    # Convert data to JSON string
    context = json.dumps(data, indent=2)

    # Combine DB + question
    full_prompt = f"Here is the MongoDB data:\n{context}\n\nAnswer this question:\n{question}"

    json_input = {
        "queries": [full_prompt],
        "assistant_name": "QnA",   # or "Chat Mode"
        "model_name": "GPT o4-mini",
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(URL, data={"input": json.dumps(json_input)})

    if response.status_code == 200:
        response_json = response.json()
        return response_json["answers"], response_json["sources"]
    else:
        return f"Error {response.status_code}: {response.text}", None


# ====== MAIN LOOP ======
def main():
    print("Loading MongoDB data...")
    data = load_data()
    print(f"Loaded {len(data)} documents.\n")

    while True:
        question = input("Ask a question (or type 'exit'): ")

        if question.lower() == "exit":
            break

        answers, sources = ask_chai(question, data)

        print("\nAnswer:")
        print(answers)

        if sources:
            print("\nSources:")
            print(sources)

        print("-" * 50)


if __name__ == "__main__":
    main()
