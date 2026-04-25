import streamlit as st
from openai import OpenAI
import json

# Load API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI Skill Assessment Agent", layout="wide")

st.title("AI Skill Assessment & Personalized Learning Agent")

# Inputs
resume = st.text_area(" Paste Candidate Resume", height=200)
jd = st.text_area(" Paste Job Description", height=200)

# Session state
if "skills" not in st.session_state:
    st.session_state.skills = []
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "current_skill" not in st.session_state:
    st.session_state.current_skill = 0

# Function: Call LLM
def ask_llm(prompt):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content


# STEP 1: Extract Skills
if st.button(" Start Assessment") and resume and jd:
    with st.spinner("Extracting skills..."):
        prompt = f"""
        Extract:
        1. Required skills from this job description
        2. Candidate skills from this resume

        Return ONLY JSON:
        {{
            "required": [],
            "candidate": []
        }}

        JD: {jd}
        Resume: {resume}
        """

        result = ask_llm(prompt)

        try:
            data = json.loads(result)
            st.session_state.skills = data["required"][:5]
            st.success("Skills extracted!")
        except:
            st.error("Error parsing skills. Try again.")


# STEP 2: Assessment
if st.session_state.skills:

    st.subheader(" Skill Assessment")

    skill = st.session_state.skills[st.session_state.current_skill]

    st.write(f"### Assessing: {skill}")

    # Generate question
    question_prompt = f"""
    You are a technical interviewer.
    Ask one question to assess {skill}.
    Keep it clear and not too long.
    """

    question = ask_llm(question_prompt)

    st.write("**Question:**", question)

    answer = st.text_area("Your Answer")

    if st.button("Submit Answer"):

        st.session_state.answers[skill] = answer

        if st.session_state.current_skill < len(st.session_state.skills) - 1:
            st.session_state.current_skill += 1
        else:
            st.session_state.current_skill = -1


# STEP 3: Evaluation
if st.session_state.current_skill == -1 and st.session_state.answers:

    st.subheader("📊 Evaluation Results")

    scores = {}

    for skill, ans in st.session_state.answers.items():
        eval_prompt = f"""
        Evaluate this answer for {skill}.

        Answer: {ans}

        Give:
        - Score out of 10
        - Short feedback

        Return JSON:
        {{
            "score": number,
            "feedback": "text"
        }}
        """

        result = ask_llm(eval_prompt)

        try:
            data = json.loads(result)
            scores[skill] = data
        except:
            scores[skill] = {"score": 5, "feedback": "Could not evaluate"}

    # Display scores
    for skill, data in scores.items():
        st.write(f"### {skill}")
        st.write(f"Score: {data['score']}/10")
        st.write(f"Feedback: {data['feedback']}")

    # STEP 4: Learning Plan
    st.subheader(" Personalized Learning Plan")

    plan_prompt = f"""
    Based on these scores:

    {scores}

    Create a learning plan:
    - Focus on weak skills
    - Include:
        - Topics
        - Resources
        - Time duration
    """

    plan = ask_llm(plan_prompt)

    st.write(plan)