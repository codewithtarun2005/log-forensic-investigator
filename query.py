# query.py

from sentence_transformers import SentenceTransformer
import chromadb
from openai import OpenAI
import os
import re

# -------------------------------
# 🔑 API KEY (set using env variable)
# -------------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------------
# 📌 STEP 1: Load Embedding Model
# -------------------------------
print("Loading embedding model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------
# 📌 STEP 2: Setup Vector DB
# -------------------------------
db_client = chromadb.Client()
collection = db_client.get_or_create_collection("logs")

# -------------------------------
# 📌 STEP 3: Index Logs
# -------------------------------
print("Reading and indexing logs...")

with open("server.log", "r") as f:
    lines = f.readlines()

chunk_size = 20
chunks_added = 0

for i in range(0, len(lines), chunk_size):
    chunk_text = "".join(lines[i:i + chunk_size])
    chunk_id = str(i // chunk_size)

    embedding = embedder.encode(chunk_text).tolist()

    collection.add(
        ids=[chunk_id],
        embeddings=[embedding],
        documents=[chunk_text],
        metadatas=[{"start_line": i}]
    )

    chunks_added += 1

print(f"✓ Indexed {chunks_added} chunks\n")

# -------------------------------
# 📌 STEP 4: Retrieval (RAG)
# -------------------------------
def search_logs(user_query, top_k=5):
    query_vector = embedder.encode(user_query).tolist()

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )

    return results.get("documents", [[]])[0]

# -------------------------------
# 📌 STEP 5: LLM + Fallback
# -------------------------------
def build_attack_story(user_query, log_chunks):
    context = "\n\n".join(log_chunks)

    prompt = f"""
You are a cybersecurity analyst.

Query: {user_query}

Logs:
{context}

Generate:
- Summary
- Suspicious IPs
- Timeline
- Attack type
- Severity
"""

    # ✅ Try OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return "🤖 LLM Mode: OpenAI\n\n" + response.choices[0].message.content

    # ❌ Fallback
    except Exception:
        print("\n⚠️ API failed, using fallback AI...\n")

        report = "🤖 LLM Mode: Fallback (No API)\n\n"
        report += "🚨 INCIDENT REPORT\n\n"

        ips = {}
        ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"

        for chunk in log_chunks:
            for line in chunk.split("\n"):
                matches = re.findall(ip_pattern, line)
                for ip in matches:
                    ips[ip] = ips.get(ip, 0) + 1

        sorted_ips = sorted(ips.items(), key=lambda x: x[1], reverse=True)

        report += "🌐 Suspicious IPs:\n"
        for ip, count in sorted_ips[:3]:
            report += f"- {ip} ({count} events)\n"

        report += "\n⚠️ Attack Type:\n"
        if "failed" in context.lower():
            report += "- Possible Brute Force\n"
        if "lateral" in context.lower():
            report += "- Lateral Movement\n"

        report += "\n🔥 Severity: HIGH\n"

        report += "\n🧠 Conclusion:\n"
        report += "Multiple suspicious activities detected.\n"

        return report

# -------------------------------
# 📌 STEP 6: CLI (ONLY when run directly)
# -------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("  🔍 LLM-Powered Log Forensic Investigator")
    print("=" * 50)

    print("\nExample queries:")
    print("  - brute force")
    print("  - lateral movement")
    print("  - failed login from 192.168.1.42\n")

    print("Type 'quit' to exit\n")

    while True:
        user_query = input("🔍 Query: ").strip()

        if user_query.lower() == "quit":
            print("Exiting...")
            break

        if not user_query:
            print("Please enter a valid query.\n")
            continue

        print("\n🔎 Searching logs...")
        chunks = search_logs(user_query)

        print("\n📄 Retrieved logs:\n")
        for i, chunk in enumerate(chunks):
            print(f"[Evidence {i+1}]")
            print(chunk[:300])
            print("...\n")

        print("\n🤖 Generating AI Report...\n")
        story = build_attack_story(user_query, chunks)

        print("=" * 50)
        print(story)
        print("=" * 50 + "\n")