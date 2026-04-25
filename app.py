import streamlit as st
from openai import OpenAI
import json
import matplotlib.pyplot as plt
import time

# ---------------- CLIENT ----------------
client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)
# ---------------- LLM FUNCTION ----------------
def ask_llm(prompt):
    try:
        res = client.chat.completions.create(
            model="anthropic/claude-3-haiku",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return res.choices[0].message.content.strip()

    except Exception as e:
        st.error(f"LLM Error: {e}")  # shows real issue

        prompt_lower = prompt.lower()  # ✅ FIXED

        # Question fallback
        if "generate" in prompt_lower or "question" in prompt_lower:
            return "Explain the concept with a real-world example."

        # Evaluation fallback
        elif "evaluate" in prompt_lower:
            return json.dumps({
                "score": 5,
                "feedback": "Fallback evaluation"
            })

        # Plan fallback
        elif "plan" in prompt_lower:
            return "Week 1: Learn → Week 2: Practice → Week 3: Build → Week 4: Revise"

        return "Fallback response"
# ---------------- CONFIG ----------------
st.set_page_config(page_title="SkillScope AI", layout="wide")
if "page" not in st.session_state:
    st.session_state.page = "home"

# ---------------- SKILLS ----------------
skill_options = [
    "AWS","Azure","Agile Methodology","API Development","Android Development",
    "Big Data","Business Analysis","Backend Development","Blockchain",
    "C","C++","C#","Cloud Computing","Cybersecurity","Computer Vision",
    "Data Science","Data Analysis","Deep Learning","Django","Docker","DevOps",
    "ETL Pipelines","Embedded Systems","Enterprise Architecture",
    "Flask","Frontend Development","Firebase","Feature Engineering",
    "Git","GCP (Google Cloud Platform)",
    "HTML","Hadoop",
    "IoT (Internet of Things)","Information Security","iOS Development",
    "Java","JavaScript",
    "Kubernetes","Kotlin",
    "Linux","Log Analysis","Linear Algebra",
    "Machine Learning","Microservices","MongoDB","MySQL",
    "Node.js","NLP (Natural Language Processing)","Network Security",
    "Object-Oriented Programming","OpenCV","Operating Systems",
    "Python","PHP",
    "Programming & Infrastructure – Config & Experiment Management",
    "Quality Assurance","Quantitative Analysis",
    "React","REST APIs","Reinforcement Learning","R Programming",
    "SQL","Spring Boot","Software Engineering","System Design","Scikit-learn",
    "TensorFlow","Testing & Debugging",
    "UI/UX Design","Unix",
    "Version Control",
    "Web Development","Web Security",
    "XGBoost","YAML","Zero Trust Security"
]

# =====================================================
# 🏠 PAGE 1
# =====================================================
if st.session_state.page == "home":

    st.title("🎯 SkillScope — Candidate Profile")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📄 Resume")

        resume_text = ""
        uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "txt"])

        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                import PyPDF2
                pdf = PyPDF2.PdfReader(uploaded_file)
                for p in pdf.pages:
                    resume_text += p.extract_text()
            else:
                resume_text = uploaded_file.read().decode("utf-8")

        jd = st.text_area("Job Description", height=150)

        # -------- ANALYZE --------
        if st.button("🔍 Analyze Resume & JD"):
            if resume_text and jd:
                with st.spinner("Analyzing..."):
                    resume_skills = ask_llm(f"""
                    Extract key technical skills from this resume.
                    Return ONLY a comma-separated list.
                    Resume:
                    {resume_text}
                    """)

                    jd_skills = ask_llm(f"""
                    Extract required skills from this job description.
                    Return ONLY a comma-separated list.
                    Job Description:
                    {jd}
                    """)

                resume_skills = [s.strip() for s in resume_skills.split(",")]
                jd_skills = [s.strip() for s in jd_skills.split(",")]

                st.session_state.resume_skills = resume_skills
                st.session_state.jd_skills = jd_skills

                st.success("Analysis complete!")

        # -------- MATCH ANALYSIS --------
        if "resume_skills" in st.session_state and "jd_skills" in st.session_state:

            st.subheader("📌 Skill Match Analysis")

            resume_skills = st.session_state.resume_skills
            jd_skills = st.session_state.jd_skills

            matched = list(set(resume_skills) & set(jd_skills))
            missing = list(set(jd_skills) - set(resume_skills))

            st.write("✅ Matching Skills:", matched)
            st.write("❌ Missing Skills:", missing)

            if st.button("⚡ Use JD Skills for Assessment"):
                st.session_state.selected_required = jd_skills
                st.success("JD skills added for assessment ✅")
        st.markdown("### 🎯 Required Skills")
        query = st.text_input("Search skills")

        if "selected_required" not in st.session_state:
            st.session_state.selected_required = []

        if query:
            for s in skill_options:
                if s.lower().startswith(query.lower()):
                    if st.button(f"➕ {s}", key=s):
                        if s not in st.session_state.selected_required:
                            st.session_state.selected_required.append(s)

        st.markdown(" ".join([
            f"<span style='background:#E8F0FE;padding:6px;border-radius:12px;margin:3px'>{s}</span>"
            for s in st.session_state.selected_required
        ]), unsafe_allow_html=True)

    with col2:
        projects = st.text_area("Projects")
        seniority = st.selectbox("Seniority", ["Beginner","Intermediate","Advanced"])
        domain = st.selectbox("Domain", ["Software Engineer","Data Scientist","AI Engineer","Other"])

        if domain == "Other":
            domain = st.text_input("Enter your domain")

        proficiency = st.selectbox("Expected Proficiency", ["Low","Medium","High"])

        st.markdown("### ⭐ Preferred Skills")

        pref_query = st.text_input("Search preferred")

        if "selected_preferred" not in st.session_state:
            st.session_state.selected_preferred = []

        if pref_query:
            for s in skill_options:
                if s.lower().startswith(pref_query.lower()):
                    if st.button(f"➕ {s}", key=f"pref_{s}"):
                        if s not in st.session_state.selected_preferred:
                            st.session_state.selected_preferred.append(s)

        st.markdown(" ".join([
            f"<span style='background:#FFF3E0;padding:6px;border-radius:12px;margin:3px'>{s}</span>"
            for s in st.session_state.selected_preferred
        ]), unsafe_allow_html=True)

    if st.button("🚀 Start Assessment"):
        if not st.session_state.selected_required:
            st.warning("Select skills first")
        else:
            st.session_state.settings = {
                "domain": domain,
                "seniority": seniority,
                "proficiency": proficiency,
                "difficulty": "Medium",
                "time_limit": 900
            }
            st.session_state.page = "assessment"
            st.rerun()

# =====================================================
# 🧠 PAGE 2
# =====================================================
elif st.session_state.page == "assessment":

    st.title("🧠 Skill Assessment")

    skills = st.session_state.selected_required
    settings = st.session_state.get("settings", {})
    time_limit = settings.get("time_limit", 900)

    categories = ["Comprehension","Application","Decision Making","Logical Reasoning","Scenario"]

    if "questions" not in st.session_state:
        st.session_state.questions = []
        st.session_state.answers = {}
        st.session_state.q_index = 0
        st.session_state.time_left = time_limit

        for i, skill in enumerate(skills):
            category = categories[i % len(categories)]

            q = ask_llm(f"""
            Generate a {category} question for {skill}.
            Make it practical and scenario-based.
            """)

            st.session_state.questions.append({
                "skill": skill,
                "question": q,
                "category": category
            })

    total = len(st.session_state.questions)
    current = st.session_state.questions[st.session_state.q_index]

    st.progress((st.session_state.q_index + 1) / total)

    st.subheader(f"Skill: {current['skill']}")
    st.write(current["question"])

    answer = st.text_area("Your Answer")

    st.write(f"⏱️ Time left: {st.session_state.time_left}s")

    if st.button("Next"):

        if not answer.strip():
            st.session_state.answers[current["skill"]] = "No answer"
        else:
            st.session_state.answers[current["skill"]] = answer

        if st.session_state.q_index < total - 1:
            st.session_state.q_index += 1
            st.session_state.time_left = time_limit
        else:
            st.session_state.page = "results"

        st.rerun()

    # Timer
    if st.session_state.time_left > 0:
        time.sleep(1)
        st.session_state.time_left -= 1
        st.rerun()

# =====================================================
# 📊 PAGE 3
# =====================================================
elif st.session_state.page == "results":

    st.title("📊 Results")

    scores = {}

    for skill, ans in st.session_state.answers.items():

        if ans.strip() == "" or ans.lower() == "no answer":
            scores[skill] = {"score": 0, "feedback": "No answer"}
            continue

        result = ask_llm(f"""
        Evaluate answer

        Skill: {skill}
        Answer: {ans}

        Return ONLY JSON:
        {{
        "score": number,
        "feedback": "text"
        }}
        """)

        try:
            scores[skill] = json.loads(result)
        except:
            scores[skill] = {"score": 5, "feedback": result}

    # -------- PIE CHART --------
    labels = list(scores.keys())
    values = [scores[s]["score"] for s in labels]

    fig, ax = plt.subplots()

    filtered_labels = [l for l, v in zip(labels, values) if v > 0]
    filtered_values = [v for v in values if v > 0]

    if filtered_values:
        ax.pie(filtered_values, labels=filtered_labels, autopct='%1.1f%%')
        ax.set_title("Skill Score Distribution")
        st.pyplot(fig)
    else:
        st.warning("No valid scores to display")

    # -------- SKILL GAPS --------
    st.subheader("🔍 Skill Gaps")

    gaps = sorted(
        [s for s in scores if scores[s]["score"] < 6],
        key=lambda x: scores[x]["score"]
    )

    if gaps:
        for skill in gaps:
            st.markdown(f"- ❌ **{skill}** (Score: {scores[skill]['score']})")
    else:
        st.success("No major skill gaps 🎉")

    # -------- LEARNING PLAN --------
    st.subheader("🧭 Learning Plan")
    if gaps:
        plan = ask_llm(f"""
        Create a structured 4-week learning plan.
        Weak skills:
        {gaps}
        Also suggest:
        - Adjacent skills the candidate can learn next
        - Resources (courses, docs, practice)
        - Time estimates
        Keep it structured week-wise.
        """)
        st.write(plan)
    else:
        st.success("You're doing great! No major gaps 🎉")