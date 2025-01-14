import streamlit as st
from llm_util import get_and_show_llm_response
import json


# Initialize Anthropic client
if 'client' not in st.session_state:
    from anthropic import Anthropic
    st.session_state.client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])


# wide page
st.set_page_config(layout="wide")

def init_state():
    if 'email_text' not in st.session_state:
        st.session_state.email_text = """Hi team,

I'd like to schedule a brainstorming session for next Tuesday at 11am. I think it's important we move quickly on this project, so please plan to attend. The session will be in the main conference room.

Best,
Alex"""
    if 'questions_dismissed' not in st.session_state:
        st.session_state.questions_dismissed = set()

def analyze_context(email_text: str) -> str:
    """Get contextual analysis from LLM"""
    prompt = f"""Analyze this email to identify key context:
    {email_text}
    
    Identify and describe in plain language:
    1. The sender's apparent role and position
    2. The type of decision/action being communicated
    3. The apparent urgency/timeline
    4. Key stakeholders who might be affected
    5. Relevant organizational context that can be inferred
    
    Format as a bulleted list."""
    
    return get_and_show_llm_response(
        prompt=prompt,
        key="context",
        step_name="Context Analysis",
    )

def generate_reflection_questions(email_text: str, context: str) -> dict:
    """Generate grouped reflection questions based on email and context"""
    prompt = f"""Given this email and context analysis, generate reflection questions grouped by purpose.
    
    Email:
    {email_text}
    
    Context Analysis:
    {context}
    
    Generate 2-3 questions for each of these purposes:
    - Clarity: Questions about what might be unclear or need more detail
    - Impact: Questions about how this might affect different stakeholders
    - Process: Questions about how the decision was made or will be implemented
    - Access: Questions about whether everyone can participate fully
    - Other: Any other questions that come to mind
    
    Format the output as JSON with this structure:
    {{
        "Clarity": ["question 1", "question 2"],
        "Impact": ["question 1", "question 2"],
        "Process": ["question 1", "question 2"],
        "Access": ["question 1", "question 2"],
        "Other": ["question 1", "question 2"]
    }}
    """
    
    response = get_and_show_llm_response(
        prompt=prompt,
        key="questions",
        step_name="Generated Questions",
        editable=False,  # Since we need to parse as JSON
        show=False
    )
    return json.loads(response)

def main():
    st.title("Reflective Email Analysis")
    init_state()
    
    # Two-column layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Email Draft")
        email_text = st.text_area(
            "Edit your email",
            st.session_state.email_text,
            height=200
        ) or ""
        analyze = st.button("Analyze for Reflection")
    
    with col2:
        st.subheader("Reflection Support")
        if analyze or 'context' in st.session_state:
            context = analyze_context(email_text)
            
            questions = generate_reflection_questions(email_text, context)
            
            # Display questions grouped by purpose
            for purpose, question_list in questions.items():
                with st.expander(f"{purpose} Questions", expanded=True):
                    for q in question_list:
                        # Create unique key for each question
                        q_key = f"{purpose}_{q}"
                        if q_key not in st.session_state.questions_dismissed:
                            cols = st.columns([8, 1])
                            with cols[0]:
                                st.write(q)
                            with cols[1]:
                                if st.button("✕", key=f"dismiss_{q_key}"):
                                    st.session_state.questions_dismissed.add(q_key)
                                    st.rerun()
            
            # Optional: Writer's own reflection
            st.divider()
            st.subheader("Your Reflection")
            st.text_area(
                "What changes would you like to make based on these reflections?",
                height=100,
                key="writer_reflection"
            )

if __name__ == "__main__":
    main()