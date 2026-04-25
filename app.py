import streamlit as st
from openai import OpenAI
import json
import matplotlib.pyplot as plt

# ---------------- API ----------------
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("Add API key in Streamlit secrets")
    st.stop()

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Skill Assessment", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "home"

# ---------------- FUNCTION ----------------
def ask_llm(prompt):
    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return res.choices[0].message.content
    except:
        return "Error"

# ---------------- SKILLS ----------------
skill_options = [
    "AWS","Azure","Agile Methodology","API Development","Android Development",
    "Big Data","Business Analysis","Backend Development","Blockchain",
    "C","C++","C#","Cloud Computing","Cybersecurity","Computer Vision",
    "Data Science","Data Analysis","Deep Learning","Django","Docker","DevOps",
    "ETL Pipelines","Embedded Systems","Enterprise Architecture",
    "Flask","Frontend Development","Firebase","Feature Engineering",
    "Git","GCP (Google Cloud Platform)","GraphQL",
    "HTML","Hadoop","Human-Computer Interaction",
    "IoT (Internet of Things)","Information Security","iOS Development",
    "Java","JavaScript","Jenkins","Jupyter Notebook",
    "Kubernetes","Kotlin",
    "Linux","Log Analysis","Linear Algebra",
    "Machine Learning","Microservices","MongoDB","MySQL",
    "Node.js","NLP (Natural Language Processing)","Network Security",
    "Object-Oriented Programming","OpenCV","Operating Systems",
    "Python","PHP","Playwright",
    "Prompt Engineering – Prompt Optimization",
    "Prompt Engineering Fundamentals – Prompt Design Techniques",
    "Programming & Infrastructure – Config & Experiment Management",
    "Quality Assurance","Quantitative Analysis",
    "React","REST APIs","Reinforcement Learning","R Programming",
    "SQL","Spring Boot","Software Engineering","System Design","Scikit-learn",
    "TensorFlow","TypeScript","Testing & Debugging",
    "UI/UX Design","Unix",
    "Version Control","Vue.js",
    "Web Development","Web Security",
    "XGBoost","YAML","Zero Trust Security"
]

# =====================================================
# 🏠 PAGE 1
# =====================================================
if st.session_state.page == "home":

    st.title("📋 Candidate Skill Assessment")
    st.markdown("### Enter Candidate Details")

    col1, col2 = st.columns(2)

    # ---------- LEFT ----------
    with col1:

        # ✅ FIXED RESUME BLOCK (SINGLE CLEAN SECTION)
        st.markdown("### 📄 Resume")

        resume_text = ""

        uploaded_file = st.file_uploader(
            "Upload Resume (PDF/TXT)",
            type=["pdf", "txt"]
        )

        resume_manual = st.text_area(
            "Or paste your resume here",
            height=200
        )

        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()
            else:
                resume_text = uploaded_file.read().decode("utf-8")

        resume = resume_text if resume_text else resume_manual

        jd = st.text_area("Job Description")

        # ---------- REQUIRED SKILLS ----------
        st.markdown("### 🎯 Required Skills")

        req_input = st.text_input("Search skills", key="req")

        filtered_req = []

        if req_input:
            filtered_req = [
                s for s in skill_options
                if s.lower().startswith(req_input.lower())
            ]
        else:
            st.info("💡 Start typing to see skill suggestions")

        if "selected_required" not in st.session_state:
            st.session_state.selected_required = []

        for skill in filtered_req:
            if st.button(f"➕ {skill}", key=f"req_{skill}"):
                if skill not in st.session_state.selected_required:
                    st.session_state.selected_required.append(skill)

        if st.session_state.selected_required:
            tags = " ".join([
                f"<span style='background:#E8F0FE;padding:6px 10px;border-radius:15px;margin:5px;display:inline-block;'>{s}</span>"
                for s in st.session_state.selected_required
            ])
            st.markdown(tags, unsafe_allow_html=True)

    # ---------- RIGHT ----------
    with col2:

        projects = st.text_area("Projects")

        seniority = st.selectbox("Seniority", ["Beginner", "Intermediate", "Advanced"])
        domain = st.text_input("Domain Context")
        proficiency = st.selectbox("Expected Proficiency", ["Low", "Medium", "High"])

        # ---------- PREFERRED ----------
        st.markdown("### ⭐ Preferred Skills")

        pref_input = st.text_input("Search preferred skills", key="pref")

        filtered_pref = []

        if pref_input:
            filtered_pref = [
                s for s in skill_options
                if s.lower().startswith(pref_input.lower())
            ]
        else:
            st.info("💡 Start typing to see preferred skills")

        if "selected_preferred" not in st.session_state:
            st.session_state.selected_preferred = []

        for skill in filtered_pref:
            if st.button(f"➕ {skill}", key=f"pref_{skill}"):
                if skill not in st.session_state.selected_preferred:
                    st.session_state.selected_preferred.append(skill)

        if st.session_state.selected_preferred:
            tags = " ".join([
                f"<span style='background:#FFF3E0;padding:6px 10px;border-radius:15px;margin:5px;display:inline-block;'>{s}</span>"
                for s in st.session_state.selected_preferred
            ])
            st.markdown(tags, unsafe_allow_html=True)

    # ---------- SUBMIT ----------
    if st.button("📩 Submit Details"):

        st.session_state.data = {
            "resume": resume,
            "jd": jd,
            "required_skills": st.session_state.selected_required,
            "preferred_skills": st.session_state.selected_preferred,
            "projects": projects,
            "seniority": seniority,
            "domain": domain,
            "proficiency": proficiency
        }

        st.success("✅ Details Submitted!")
        st.subheader("📌 Preview")
        st.json(st.session_state.data)

    # ---------- START ----------
    if st.button("🚀 Start AI Assessment"):

        if "data" not in st.session_state:
            st.warning("⚠️ Please submit details first")
        else:
            st.session_state.answers = {}
            st.session_state.q_index = 0
            st.session_state.page = "assessment"
            st.rerun()

    st.caption("⏱ Estimated Time: 30 minutes")

# =====================================================
# 🧠 PAGE 2
# =====================================================
elif st.session_state.page == "assessment":

    st.title("🧠 Basic Cognitive Assessment")

    skills = ["Comprehension", "Logical Thinking", "Decision Making"]

    current = skills[st.session_state.q_index]

    st.progress((st.session_state.q_index + 1) / len(skills))
    st.subheader(f"Assessing: {current}")

    question = ask_llm(f"Ask a beginner level question for {current}")
    st.write("**Question:**", question)

    answer = st.text_area("Your Answer")

    if st.button("Submit Answer"):

        st.session_state.answers[current] = answer

        if st.session_state.q_index < len(skills) - 1:
            st.session_state.q_index += 1
        else:
            st.session_state.page = "results"

        st.rerun()

# =====================================================
# 📊 PAGE 3
# =====================================================
elif st.session_state.page == "results":

    st.title("📊 Results & Learning Plan")

    scores = {}

    for skill, ans in st.session_state.answers.items():

        result = ask_llm(f"""
        Evaluate answer:
        {ans}

        Return JSON:
        {{ "score": number, "feedback": "text" }}
        """)

        try:
            scores[skill] = json.loads(result)
        except:
            scores[skill] = {"score": 5, "feedback": "Default"}

    labels = list(scores.keys())
    values = [scores[s]["score"] for s in labels]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_ylim(0, 10)
    st.pyplot(fig)

    st.subheader("🔍 Skill Gap")
    gaps = [s for s, v in scores.items() if v["score"] < 6]
    st.write(gaps)

    st.subheader("🧭 Learning Plan")

    plan = ask_llm(f"""
    Based on:
    {scores}

    Generate:
    - SMART goals
    - Weekly plan
    - Resources
    """)

    st.write(plan)

    if st.button("🔄 Restart"):
        st.session_state.page = "home"
        st.rerun()