import streamlit as st
from dotenv import load_dotenv
from utils.parser import parse_file, extract_hr_email_and_company
from utils.emailer import generate_application_email
from utils.gmail_sender import send_email_via_gmail

load_dotenv()

st.set_page_config(page_title="Resume to HR Email Generator", layout="centered")

st.title("📧 Resume to HR Email Generator")
st.markdown("Upload your resume and paste the job post to generate a tailored application email.")

# Inputs
resume_file = st.file_uploader("Upload Resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
jd_text_input = st.text_area("Paste Job Post Text", height=250)
job_title = st.text_input("Job Title (e.g., Data Scientist)")

# Track button click
if "generate_clicked" not in st.session_state:
    st.session_state.generate_clicked = False

if st.button("Generate Email", key="generate_email_btn"):
    st.session_state.generate_clicked = True

# Generate email only if button was clicked and inputs are valid
if st.session_state.generate_clicked and resume_file and jd_text_input.strip() and job_title:
    with st.spinner("Extracting HR contact and company..."):
        hr_email, company = extract_hr_email_and_company(jd_text_input)
        if not hr_email or not company:
            st.error("Could not extract HR email or company name from the job post.")
        else:
            resume_text = parse_file(resume_file)
            jd_text = jd_text_input.strip()
            email = generate_application_email("Shashi Kumar Reddy", resume_text, jd_text, company, job_title, hr_email)

            # Store in session state
            st.session_state.generated_email = email
            st.session_state.hr_email = hr_email
            st.session_state.company = company
            st.session_state.job_title = job_title

# Display Outputs
if "generated_email" in st.session_state:
    st.subheader("📤 Email Preview")

    st.markdown("**Subject Line:**")
    st.code(f"Application for {st.session_state.job_title} at {st.session_state.company}", language="markdown")

    st.markdown("**HR Email ID:**")
    st.code(st.session_state.hr_email, language="markdown")

    st.markdown("**Generated Email Body:**")
    email_text = st.session_state.generated_email
    dynamic_height = min(800, max(200, len(email_text) // 4))  # adjust automatically

    st.text_area(
    label="Generated Email Body",
    value=email_text,
    height=dynamic_height,
    label_visibility="collapsed"
    )

    st.download_button("📥 Download Email", st.session_state.generated_email, file_name="application_email.txt")

    # Optional Gmail Send Section
    with st.expander("📤 Send Email via Gmail (Optional)"):
        sender_email = st.text_input("Your Gmail Address")
        app_password = st.text_input("Your Gmail App Password", type="password")
        if st.button("Send Email", key="send_email_btn"):
            subject_line = f"Application for {st.session_state.job_title} at {st.session_state.company}"
            send_result = send_email_via_gmail(
                sender_email,
                app_password,
                st.session_state.hr_email,
                subject_line,
                st.session_state.generated_email,
                resume_file  # ✅ Pass the uploaded resume file
            )
            if send_result is True:
                st.success("✅ Email sent successfully with resume attached!")
            else:
                st.error(f"❌ Failed to send email: {send_result}")
