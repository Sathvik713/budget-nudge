import streamlit as st
import pandas as pd
from datetime import datetime
from groq import Groq
import io

st.set_page_config(page_title="Budget Nudge", layout="wide")

st.title("🤖 Budget Nudge Agent")
st.markdown("*Upload transactions → AI analyzes → Funny nudge!*")

# CONFIG
GROQ_API_KEY = st.sidebar.text_input("🔑 Groq API Key", type="password", 
                                    help="console.groq.com → API Keys")
MONTHLY_INCOME = st.sidebar.number_input("💰 Monthly Income", 10000, 200000, 60000)
FOOD_CAP_PCT = st.sidebar.slider("🍔 Food Cap %", 5, 25, 10) / 100

# LLM
@st.cache_data
def get_nudge(total_food, cap):
    if not GROQ_API_KEY.startswith("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"):
        return f"🚀 ₹{total_food:.0f} food delivery! 💡 Add Groq key for AI nudges."
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"₹{total_food:.0f} Swiggy/Zomato vs ₹{cap:.0f} cap. Funny nudge + tip."}],
            max_tokens=80
        )
        return chat.choices[0].message.content.strip()
    except:
        return f"₹{total_food:.0f} vs ₹{cap:.0f}! Cook this weekend 🍳"

# UPLOAD
uploaded = st.file_uploader("📁 Upload .txt/.csv", type=['txt','csv'])

if uploaded:
    try:
        # Parse ANY format
        if 'txt' in uploaded.name:
            content = io.StringIO(uploaded.read().decode())
            df = pd.read_csv(content, sep=None, engine='python', 
                           header=None, names=['date','desc','amount'])
        else:
            df = pd.read_csv(uploaded)
        
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df = df.dropna()
        
        st.success(f"✅ {len(df)} transactions loaded!")
        st.dataframe(df.head())
        
        # Analysis
        df['food'] = df['desc'].str.contains('SWIGGY|ZOMATO', case=False, na=False)
        today = datetime.now()
        food_spend = df[df['food'] & 
                       (df['date'].dt.month == today.month)]['amount'].sum()
        cap = MONTHLY_INCOME * FOOD_CAP_PCT
        
        col1, col2 = st.columns(2)
        col1.metric("🍔 Food Delivery", f"₹{food_spend:.0f}")
        col2.metric("🎯 Cap", f"₹{cap:.0f}")
        
        if st.button("🚀 AI Nudge", type="primary"):
            nudge = get_nudge(food_spend, cap)
            st.balloons()
            st.markdown(f"### 💬 **{nudge}**")
            
    except Exception as e:
        st.error(f"Parse error: {e}")
        st.info("**Try:** `2026-02-10 Swiggy 450` (one per line)")
else:
    st.info("👆 Upload transactions.txt")
