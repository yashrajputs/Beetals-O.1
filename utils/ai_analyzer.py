import os
import requests
import json

def analyze_claim_with_ai(query: str, relevant_clauses: list[dict]) -> str:
    """
    Analyze insurance claim using Perplexity AI API.
    Returns the AI analysis result.
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY environment variable not found")
    
    # Format relevant clauses for the prompt
    clauses_text = ""
    for i, clause in enumerate(relevant_clauses, 1):
        clauses_text += f"""
Clause {i}: {clause['title']} (Page {clause['page_number']})
{clause['text']}

"""
    
    # Create the prompt
    prompt = f"""
You are an expert insurance claims analyst for Indian health insurance policies.

User Query:
"{query}"

Relevant Policy Clauses:
{clauses_text}

Instructions:
Using only the relevant clauses provided above, analyze this insurance claim and decide:
1. Is this procedure/claim covered under the policy?
2. Is it subject to any condition or restriction?
3. What amount should be approved (if any)?

Return only a JSON object with the following structure:
{{
  "decision": "Yes/No/Partial",
  "amount": "₹... or percentage or 'Not specified'", 
  "justification": "Detailed explanation based on the policy clauses, including specific clause references"
}}

Be precise and reference specific clauses in your justification. If information is missing or unclear, state that in your justification.
"""

    # API configuration
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Request payload
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system", 
                "content": "You are an insurance claims analyst. Provide precise coverage decisions in JSON format based only on the provided policy clauses."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "temperature": 0.1,
        "max_tokens": 1000
    }
    
    try:
        # Make the API request
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
    
    except requests.exceptions.Timeout:
        raise Exception("API request timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Error analyzing claim: {str(e)}")
