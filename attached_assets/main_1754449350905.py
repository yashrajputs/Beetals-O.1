import pymupdf  
import re
import uuid
from textwrap import wrap
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os
import requests
import json 
import fitz
import getpass 

os.environ['API_KEY'] = getpass.getpass('ENTER YOUR API KEY')
API_KEY = os.getenv("API_KEY")
def is_title(line: str) -> bool:
    """
    Uses heuristics to determine if a line is a section title.
    - Titles are generally short.
    - They often start with numbers, letters, or bullets (e.g., "1.", "A.", "(i)").
    - They are often in ALL CAPS or Title Case.
    - They do not end with a period.
    """
    stripped_line = line.strip()
    
    if not stripped_line or len(stripped_line) > 120:
        return False
        
    if stripped_line.endswith('.'):
        return False

    if re.match(r'^\s*(\d{1,2}\.|[A-Z]\.|\([a-z]\)|\([ivx]+\)|•)\s+', stripped_line):
        return True
        
    # Heuristic for short, capitalized lines likely being titles
    if len(stripped_line.split()) < 8:
        if stripped_line.isupper():
            return True
        if stripped_line.istitle():
            return True
            
    return False

def is_junk(line: str) -> bool:
    """
    Determines if a line is boilerplate junk (headers, footers, etc.).
    """
    stripped_line = line.strip().lower()
    
    if not stripped_line:
        return True

    # List of keywords that indicate a line is junk
    junk_keywords = [
        'uin:', 'irda', 'regn. no.', 'reg. no.', 'cin:', 'gstin',
        'subject matter of solicitation', 'trade logo', 'corporate office',
        'registered office', 'toll-free', 'website:', 'e-mail', '.com', '.in',
        'confidential', 'internal use'
    ]
    
    if any(keyword in stripped_line for keyword in junk_keywords):
        return True
        
    if re.search(r'^(page\s*\d+|\d+\s*of\s*\d+)$', stripped_line):
        return True
        
    return False


def extract_structured_sections(pdf_path: str) -> list[dict]:

    structured_data = []
    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc):
        current_title = "General Information" # Default title for text before the first heading
        current_text_block = ""
        
        text = page.get_text("text")
        lines = text.split('\n')
        
        for line in lines:
            if is_title(line):
                # When we find a new title, the previous section is complete.
                # Save the completed section before starting a new one.
                if current_text_block.strip():
                    structured_data.append({
                        "id": str(uuid.uuid4()),
                        "page_number": page_num + 1,
                        "title": current_title,
                        "text": " ".join(current_text_block.split()), # Normalize whitespace
                        "source": pdf_path
                    })
                
                # Start the new section
                current_title = line.strip()
                current_text_block = ""
            elif not is_junk(line):
                # If the line is not a title and not junk, it's content.
                current_text_block += " " + line.strip()

        # After the loop, save the last section from the page
        if current_text_block.strip():
            structured_data.append({
                "id": str(uuid.uuid4()),
                "page_number": page_num + 1,
                "title": current_title,
                "text": " ".join(current_text_block.split()),
                "source": pdf_path
            })
            
    return structured_data


def get_top_similar_clauses(query: str, indexed_data: list[dict], index: faiss.Index, model: SentenceTransformer, k: int = 5) -> list[dict]:
    """
    Finds and returns the top k most similar clauses from the indexed data.
    """
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, k)
    
    results = [indexed_data[i] for i in indices[0]]
    
    print(f"✅ Retrieved Top {k} Clauses for query: '{query}'\n")
    for clause in results:
        print(f"🔹 Title: {clause['title']} (Page {clause['page_number']})")
        print(f"📝 Text: {clause['text'][:300]}...")
        print("-" * 20)
        
    return results

pdf_path = "path_to_your_pdf"
structured_clauses = extract_structured_sections(pdf_path)
structured_clauses = [clause for clause in structured_clauses if len(clause['text'])>50]

model = SentenceTransformer('BAAI/bge-base-en-v1.5')

text_to_embed =[f"{d['title']}:{d['text']}" for d in structured_clauses]

embeddings = model.encode(text_to_embed, convert_to_numpy=True)
dimensions = embeddings.shape[1]
index = faiss.IndexFlatL2(dimensions)
index.add(embeddings)


query = "50M, used air ambulance, distance traveled 300 km, seeking 100% reimbursement"







top_clauses = get_top_similar_clauses(
        query=query,
        indexed_data=structured_clauses,
        index=index,
        model=model,
        k=5
    )




prompt = f"""
You are an expert insurance claims analyst for Indian health insurance policies.

User Query:
"{query}"

This query refers to:
- Age: 
- Gender: 
- Procedure: 
- Location: 
- Policy Duration: 

Relevant Clauses:
{top_clauses}

Instructions:
Using only the relevant clauses, decide:
1. Is this procedure covered under the policy?
2. Is it subject to any condition or restriction?
3. Return only a JSON object with:
   {{
     "decision": "Yes/No",
     "amount": "₹...", 
     "justification": "..."
   }}
"""

url = "https://api.perplexity.ai/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Request payload
payload = {
    "model": "sonar-reasoning-pro",
    "messages": [
        {"role": "system", "content": "You are an insurance assistant that explains coverage decisions clearly and briefly in human language."},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.1
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

# Output
if response.status_code == 200:
    print("✅ Response:")
    print(response.json()['choices'][0]['message']['content'])
else:
    print("❌ Error:")
    print(response.status_code, response.text)
