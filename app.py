

import streamlit as st
from dotenv import load_dotenv
from utils.parser import parse_file, extract_hr_email_and_company, extract_candidate_details
from utils.emailer import generate_application_email
from utils.gmail_sender import send_email_via_gmail
import re

load_dotenv()
st.set_page_config(page_title="Resume to HR Email Generator", layout="wide")

st.markdown(
    """
    <div style='text-align: center; padding-bottom: 1rem;'>
        <h1>📧 Resume to HR Email Generator</h1>
        <p style='font-size: 18px;'>Upload your resume and paste the job post to generate a tailored application email.</p>
    </div>
    """,
    unsafe_allow_html=True
)
# ✅ Remove "Not Provided" lines from signature block
def filter_signature_block(email_text):
    if "Best regards," not in email_text:
        return email_text
    body, signature = email_text.split("Best regards,", 1)
    signature_lines = signature.strip().splitlines()
    filtered_lines = [line.strip() for line in signature_lines if line.strip().lower() != "not provided"]
    return f"{body.strip()}\n\nBest regards,\n" + "\n".join(filtered_lines)

# ✅ Normalize spacing and formatting
def normalize_email_spacing(text):
    text = text.strip()
    lines = text.splitlines()
    lines = [line.lstrip() for line in lines]
    text = "\n".join(lines)
    text = re.sub(r'([^\n])\n([^\n])', r'\1\n\n\2', text)
    text = re.sub(r'\nBest regards,', r'\n\nBest regards,', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    if "Best regards," in text:
        parts = text.split("Best regards,")
        before = parts[0].rstrip()
        after = parts[1].strip().splitlines()
        after_clean = "\n".join([line.strip() for line in after if line.strip()])
        text = f"{before}\n\nBest regards,\n{after_clean}"
    return text

# Two-column layout
left_col, right_col = st.columns(2)

with left_col:
    st.header("📥 Input")
    resume_file = st.file_uploader("Upload Resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    jd_text_input = st.text_area("Paste -> your Job Post with HR Mail Text", height=250)
    job_title = st.text_input("Job Title (e.g., Data Scientist)")

    if "generate_clicked" not in st.session_state:
        st.session_state.generate_clicked = False

    if st.button("Generate Email", key="generate_email_btn"):
        st.session_state.generate_clicked = True

if st.session_state.generate_clicked and resume_file and jd_text_input.strip() and job_title:
    with st.spinner("Extracting HR contact and company..."):
        hr_email, company = extract_hr_email_and_company(jd_text_input)
        if not hr_email or not company:
            st.error("Could not extract HR email or company name from the job post.")
        else:
            resume_text = parse_file(resume_file)
            name, candidate_email, candidate_phone, candidate_linkedin = extract_candidate_details(resume_text)
            jd_text = jd_text_input.strip()

            raw_email = generate_application_email(
                name,
                candidate_email,
                candidate_phone,
                candidate_linkedin,
                resume_text,
                jd_text,
                company,
                job_title,
                hr_email
            )

            filtered_email = filter_signature_block(raw_email)
            cleaned_email = normalize_email_spacing(filtered_email)

            st.session_state.generated_email = cleaned_email
            st.session_state.edited_email = cleaned_email
            st.session_state.hr_email = hr_email
            st.session_state.company = company
            st.session_state.job_title = job_title
            st.session_state.candidate_info = {
                "name": name,
                "email": candidate_email,
                "phone": candidate_phone,
                "linkedin": candidate_linkedin
            }

with right_col:
    if "generated_email" in st.session_state:
        st.header("📤 Output")

        st.markdown("**Subject Line:**")
        st.code(f"Application for {st.session_state.job_title} at {st.session_state.company}", language="markdown")

        st.markdown("**HR Email ID:**")
        st.code(st.session_state.hr_email, language="markdown")

        st.markdown("**✏️ Edit and Preview Email Body:**")
        edited_email_input = st.text_area(
            "Your email content:",
            value=st.session_state.edited_email,
            height=500,
            key="editable_email_box"
        )
        st.session_state.edited_email = edited_email_input

        


        with st.expander("📤 Send Email via Your Gmail"):
            
            sender_email = st.text_input("Your Gmail Address",placeholder="yourmail@gmail.com")
            app_password = st.text_input("Your Gmail App Password", type="password",placeholder="Password")

            with st.expander("ℹ️ How to Create a Gmail App Password"):
                st.markdown("""
                To send emails from your Gmail account using this app, you need to generate a Gmail App Password. Here's how:

                1. **Enable 2-Step Verification** on your Google account  
                    → Go to [https://myaccount.google.com/security](https://myaccount.google.com/security)  
                    → Turn on 2-Step Verification

                2. **Generate an App Password**  
                    → Visit [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)  
                    → Select **Mail** as the app  
                    → Choose **Other** and type something like “Resume App”  
                    → Click **Generate** and copy the 16-character password

                3. **Paste the App Password above**  
                    → Use it in the field labeled “Your Gmail App Password”  
                    → This password is used only to send your email securely

                🔒 Your credentials are not stored — they’re used only to send your email.
                """)

            if st.button("Send Email", key="send_email_btn"):
                subject_line = f"Application for {st.session_state.job_title} at {st.session_state.company}"
                send_result = send_email_via_gmail(
                    sender_email,
                    app_password,
                    st.session_state.hr_email,
                    subject_line,
                    st.session_state.edited_email,
                    resume_file
                )
                if send_result is True:
                    st.success("✅ Email sent successfully with resume attached!")
                else:
                    st.error(f"❌ Failed to send email: {send_result}")

st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #111;
        color: white;
        text-align: center;
        padding: 10px 0;
        font-size: 15px;
        z-index: 100;
    }
    .footer a {
        color: #1E90FF;
        text-decoration: none;
        margin: 0 8px;
    }
    </style>

    <div class="footer">
        Shashi Kumar Reddy |
        📧 <a href="mailto:shashi.chintalapalli@gmail.com">shashi.chintalapalli@gmail.com</a> |
        🌐 <a href="https://shashi-chintalapalli.github.io/" target="_blank">Portfolio</a> |
        💻 <a href="https://github.com/Shashi-chintalapalli" target="_blank">GitHub</a>
    </div>
    """,
    unsafe_allow_html=True
)
