import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0.4,
    groq_api_key=groq_key
)

EMAIL_PROMPT = """
You are an expert job application writer.

Your task is to generate a clean, professional job application email. The output must start directly with the greeting — no introductory lines, no headers, no labels like "To:" or "Subject:". Only the email body.

Inputs:
- Candidate Name: {name}
- Company Name: {company}
- Job Title: {job_title}
- HR Email: {hr_email}
- HR First Name: {hr_first_name}
- Resume Text: {resume_text}
- Job Description: {job_description}

Instructions:
- Start directly with "Dear {hr_first_name}," — use "Hiring Manager" if the name is unknown
- Do NOT include any lines like "Here's a professional email", "To:", or "Subject:"
- Write a concise, confident, respectful email tailored to the job
- Mention the role and company naturally in the first paragraph
- Highlight matching skills from the resume
- Mention willingness to learn any missing skills
- End with a clear call to action
- Include this signature block at the end:

Best regards,  
Shashi Kumar Reddy  
shashi.chintalapalli@gmail.com  
https://www.linkedin.com/in/shashi-chintalapalli/  
9603808379
"""

def extract_hr_first_name(hr_email):
    if hr_email and "@" in hr_email:
        return hr_email.split("@")[0].split(".")[0].capitalize()
    return "Hiring Manager"

def generate_application_email(name, resume_text, jd_text, company, job_title, hr_email):
    hr_first_name = extract_hr_first_name(hr_email)
    prompt = EMAIL_PROMPT.format(
        name=name,
        company=company,
        job_title=job_title,
        hr_email=hr_email,
        hr_first_name=hr_first_name,
        resume_text=resume_text,
        job_description=jd_text
    )
    response = llm.invoke(prompt)
    return response.content.strip()
