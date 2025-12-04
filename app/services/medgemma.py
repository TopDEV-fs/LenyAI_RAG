import requests
import os
import json
from typing import List, Dict, Generator
MEDGEMMA_API_URL = "http://69.19.136.148:8050/v1/chat/completions"


# def generate_prompt(evidences: List[Dict], user_query: str) -> str:
#     evidence_text = ""
#     for evidence in evidences:
#         evidence_text += f"[PMID:{evidence['pmid']}] {evidence['title']} — {evidence['abstract']}\n\n"

#     prompt = f"""
#     You are a clinical reasoning assistant.
#     Use the EVIDENCE below to answer the QUESTION.

#     EVIDENCE:
#     {evidence_text}

#     QUESTION:
#     {user_query}


#     Answer concisely and factually, summarizing findings.
#     Answer must be easy to see.
#     """
#     return prompt.strip()

def generate_prompt(evidences: List[Dict], user_query: str) -> str:
    evidence_text = ""
    for i,evidence in enumerate(evidences):
        evidence_text += f"[{evidence['pmcid']}] {evidence['article_title']} — {evidence['text']}\n\n"

    prompt = f"""
    You are a clinical decision support assistant. Your role is to provide concise, clinically actionable answers based on high-quality evidence and guidelines. When generating answers, synthesize the following:
    Clinical Evidence: Cite the evidence articles provided by PMC. When citing articles, ensure to mention the journal or source in the format like [PMC115038] After the setence. You can see exact PMCID in the every articles. 
    Guidelines: Summarize key recommendations from well-established guidelines (e.g., NCBI) without quoting them verbatim. Mention the guideline or provide a synthesized recommendation with clear reference to the guideline name (e.g., NCBI).
    Patient-specific factors: Always account for patient-specific factors, such as age, comorbidities, and disease stage when applicable. These factors should help shape the clinical decisions or treatment recommendations provided.
    Risk stratification: Indicate risk (e.g., high vs. low) based on clinical features and evidence.
    Treatment recommendations: Provide treatment options ranked from most preferred to alternatives. When applicable, give context for first-line treatments or when alternatives might be considered.
    Concise and Structured Answer: Your response should be short (7-10 sentences). Avoid long paragraphs, and ensure it is structured in a way that a busy clinician can quickly grasp the essential information.

    EVIDENCE:
    {evidence_text}

    QUESTION:
    {user_query}

    """
    return prompt.strip()

def generate_medical_message(prompt: str) -> str:
    # print(f"PROMPT \n {prompt}")
    payload = {"messages": [{"role": "user", "content": prompt, "stream": False}]}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(MEDGEMMA_API_URL, json=payload, headers=headers, timeout=180)
        response.raise_for_status()
        data = response.json()
        
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error generating medical message: {str(e)}"

def generate_medical_message_stream(prompt: str) -> Generator[str, None, None]:
    """Generate medical message with streaming support."""
    payload = {"messages": [{"role": "user", "content": prompt}], "stream": True}
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(MEDGEMMA_API_URL, json=payload, headers=headers, timeout=180, stream=True)
    response.raise_for_status()
    
    for line in response.iter_lines():
        if line:
            line_text = line.decode('utf-8')
            if line_text.startswith('data: '):
                data_str = line_text[6:]  # Remove 'data: ' prefix
                if data_str.strip() == '[DONE]':
                    break
                try:
                    data = json.loads(data_str)
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            yield content
                except json.JSONDecodeError:
                    continue