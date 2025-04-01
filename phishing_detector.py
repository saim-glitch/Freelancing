import streamlit as st
import pandas as pd
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import time

# Sample data for demonstration
phishing_examples = [
    "Urgent: Your account will be suspended! Click here to verify your details.",
    "Congratulations! You've won a $1000 Amazon gift card. Claim now!",
    "Security Alert: Unusual login detected. Click to secure your account.",
    "Your PayPal account needs verification. Please update your information.",
    "Limited time offer: Get 50% off all products. Enter your credit card now!"
]

legit_examples = [
    "Your monthly statement is ready. Please find it attached.",
    "Meeting reminder: Team sync at 2pm tomorrow in Conference Room B.",
    "Your order #12345 has been shipped and will arrive on Friday.",
    "Thank you for your application. We'll review your materials and get back to you.",
    "The report you requested is now available in the shared drive."
]

# Load or train a simple model (in a real app, you'd use a pre-trained model)
def get_model():
    try:
        model = joblib.load('phishing_model.joblib')
        vectorizer = joblib.load('vectorizer.joblib')
    except:
        # Create some dummy training data if no model exists
        texts = phishing_examples + legit_examples
        labels = [1]*len(phishing_examples) + [0]*len(legit_examples)
        
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(texts)
        
        model = LogisticRegression()
        model.fit(X, labels)
        
        joblib.dump(model, 'phishing_model.joblib')
        joblib.dump(vectorizer, 'vectorizer.joblib')
    
    return model, vectorizer

model, vectorizer = get_model()

# Initialize session state for gamification
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'badges' not in st.session_state:
    st.session_state.badges = []
if 'detection_history' not in st.session_state:
    st.session_state.detection_history = []

# App title and description
st.title("🕵️ AI Phishing Detector")
st.markdown("""
    Train your eye to spot phishing attempts and protect yourself from scams!
    Our AI helps identify suspicious emails and websites.
""")

# Main app tabs
tab1, tab2, tab3 = st.tabs(["Detect Phishing", "Challenge Mode", "Your Progress"])

with tab1:
    st.header("🔍 Detect Phishing Content")
    user_input = st.text_area("Enter an email or website URL to check:", height=150)
    
    if st.button("Analyze"):
        if user_input:
            with st.spinner("Analyzing..."):
                time.sleep(1)  # Simulate processing time
                
                # Make prediction
                X = vectorizer.transform([user_input])
                prediction = model.predict(X)[0]
                proba = model.predict_proba(X)[0][prediction]
                
                # Display result
                if prediction == 1:
                    st.error("⚠️ This appears to be a phishing attempt!")
                    st.session_state.detection_history.append({
                        'content': user_input[:50] + "...",
                        'type': 'Phishing',
                        'correct': None,
                        'points': 0
                    })
                else:
                    st.success("✅ This looks legitimate!")
                    st.session_state.detection_history.append({
                        'content': user_input[:50] + "...",
                        'type': 'Legitimate',
                        'correct': None,
                        'points': 0
                    })
                
                st.write(f"Confidence: {proba:.0%}")
                
                # Explanation
                st.markdown("""
                **What makes this suspicious/legitimate?**
                - Phishing attempts often create urgency or offer unexpected rewards
                - Legitimate emails usually have specific details about you
                - Check sender addresses carefully - phishing often uses similar-looking domains
                """)
        else:
            st.warning("Please enter some text to analyze")

with tab2:
    st.header("🎯 Phishing Challenge")
    st.markdown("Test your skills! Is this email legitimate or a phishing attempt?")
    
    if 'current_challenge' not in st.session_state or st.button("New Challenge"):
        # Select a random example
        if random.random() > 0.5:
            example = random.choice(phishing_examples)
            correct_answer = "Phishing"
        else:
            example = random.choice(legit_examples)
            correct_answer = "Legitimate"
        
        st.session_state.current_challenge = {
            'text': example,
            'answer': correct_answer,
            'answered': False
        }
    
    if 'current_challenge' in st.session_state:
        challenge = st.session_state.current_challenge
        st.text_area("Email:", value=challenge['text'], height=150, key="challenge_text", disabled=True)
        
        if not challenge['answered']:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Legitimate ✅"):
                    user_answer = "Legitimate"
                    if user_answer == challenge['answer']:
                        st.session_state.score += 10
                        st.success("Correct! You earned 10 points!")
                        if st.session_state.score >= 50 and "Novice Detector" not in st.session_state.badges:
                            st.session_state.badges.append("Novice Detector")
                            st.balloons()
                    else:
                        st.error("Oops! That was actually a phishing attempt.")
                    
                    st.session_state.detection_history.append({
                        'content': challenge['text'][:50] + "...",
                        'type': challenge['answer'],
                        'correct': user_answer == challenge['answer'],
                        'points': 10 if user_answer == challenge['answer'] else 0
                    })
                    st.session_state.current_challenge['answered'] = True
            
            with col2:
                if st.button("Phishing ⚠️"):
                    user_answer = "Phishing"
                    if user_answer == challenge['answer']:
                        st.session_state.score += 10
                        st.success("Correct! You earned 10 points!")
                        if st.session_state.score >= 50 and "Novice Detector" not in st.session_state.badges:
                            st.session_state.badges.append("Novice Detector")
                            st.balloons()
                    else:
                        st.error("Oops! That was actually legitimate.")
                    
                    st.session_state.detection_history.append({
                        'content': challenge['text'][:50] + "...",
                        'type': challenge['answer'],
                        'correct': user_answer == challenge['answer'],
                        'points': 10 if user_answer == challenge['answer'] else 0
                    })
                    st.session_state.current_challenge['answered'] = True
            
            if challenge['answered']:
                st.markdown("**Why this is " + challenge['answer'] + ":**")
                if challenge['answer'] == "Phishing":
                    st.markdown("""
                    - Creates a sense of urgency
                    - Asks for personal information
                    - Offers something too good to be true
                    - Generic greeting instead of personal
                    """)
                else:
                    st.markdown("""
                    - Specific to you (order number, meeting details)
                    - No urgent demands
                    - From a known sender/domain
                    - No requests for sensitive information
                    """)

with tab3:
    st.header("📊 Your Progress")
    
    st.metric("Your Score", st.session_state.score)
    
    st.subheader("🏆 Badges Earned")
    if st.session_state.badges:
        for badge in st.session_state.badges:
            st.markdown(f"- {badge}")
    else:
        st.write("No badges yet. Complete challenges to earn badges!")
    
    st.subheader("📝 Detection History")
    if st.session_state.detection_history:
        history_df = pd.DataFrame(st.session_state.detection_history)
        st.dataframe(history_df)
    else:
        st.write("No detection history yet. Start analyzing content to see your history!")
    
    # Progress to next badge
    if st.session_state.score < 50:
        st.write(f"🔜 {50 - st.session_state.score} points to next badge (Novice Detector)")
    elif st.session_state.score < 100:
        st.write(f"🔜 {100 - st.session_state.score} points to next badge (Expert Detector)")
        if st.session_state.score >= 100 and "Expert Detector" not in st.session_state.badges:
            st.session_state.badges.append("Expert Detector")
            st.balloons()

# Sidebar with tips
with st.sidebar:
    st.header("💡 Phishing Tips")
    st.markdown("""
    **Common phishing signs:**
    - Urgent or threatening language
    - Requests for personal information
    - Unexpected attachments or links
    - Misspellings or odd phrasing
    - Suspicious sender addresses
    
    **Always:**
    - Hover over links before clicking
    - Verify unexpected requests via another channel
    - Keep software updated
    - Use multi-factor authentication
    """)
    
    st.markdown("---")
    st.markdown("**How this works:**")
    st.markdown("""
    This AI analyzes text for phishing indicators:
    - Urgency keywords
    - Reward language
    - Suspicious URLs
    - Generic greetings
    - Requests for information
    """)

# Footer
st.markdown("---")
st.markdown("🛡️ Stay safe online! Always verify suspicious communications.")