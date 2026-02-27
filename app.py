import streamlit as st
import pandas as pd
from datetime import datetime
from groq import Groq
import io

st.set_page_config(page_title="Budget Nudge", layout="wide")
st.title("🤖 Budget Nudge Agent")

# 🔥 PASTE YOUR KEY HERE (Line 11)
GROQ_API_KEY = "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"  # ← YOUR KEY

# Sidebar (optional override)
st.sidebar.title("⚙️ Settings")
api_key_input = st.sidebar.text_input("🔑 API Key (optional override)", 
                                     value="", type="password")
if api_key_input:
    GROQ_API_KEY = api_key_input

income = st.sidebar.number_input("💰 Monthly Income", 10000, 200000, 60000)
food_pct = st.sidebar.slider("🍔 Food Cap %", 5, 25, 10) / 100

# Test API key
try:
    client = Groq(api_key=GROQ_API_KEY)
    st.sidebar.success("✅ **Groq Connected!** Ready for AI nudges.")
except:
    st.sidebar.error("❌ **Invalid API Key** - Demo mode only.")

# LLM Function
@st.cache_data(ttl=600)
def get_nudge(total_food, cap):
    if not GROQ_API_KEY or not GROQ_API_KEY.startswith("gsk_"):
        return f"🚀 **Demo:** ₹{total_food:.0f} food delivery detected! 💡 Paste real Groq key above."
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"₹{total_food:.0f} Swiggy/Zomato vs ₹{cap:.0f} cap. Funny nudge + 1 tip."}],
            max_tokens=80
        )
        return f"🤖 **AI Nudge:** {response.choices[0].message.content.strip()}"
    except Exception as e:
        return f"⚠️ ₹{total_food:.0f} vs ₹{cap:.0f} | Error: {str(e)[:50]}"

# File Upload
uploaded = st.file_uploader("📁 Upload transactions.txt/csv", type=['txt','csv'])

if uploaded:
    with st.spinner("Parsing..."):
        try:
            # Auto-parse
            if uploaded.name.endswith('.txt'):
                content = io.StringIO(uploaded.read().decode('utf-8'))
                df = pd.read_csv(content, sep=None, engine='python', 
                               names=['date','desc','amount'])
            else:
                df = pd.read_csv(uploaded)
            
            # Clean
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            df = df.dropna()
            
            st.success(f"✅ Loaded **{len(df)}** transactions!")
            st.dataframe(df, use_container_width=True)
            
            # Analysis - Swiggy vs Zomato breakdown
            df['food'] = df['desc'].str.contains('SWIGGY|ZOMATO', case=False)
            today = datetime.now()
            food_df = df[df['food'] & 
                        (df['date'].dt.month == today.month)]
            
            # CIRCULAR CHART DATA
            swiggy_spend = food_df[df['desc'].str.contains('SWIGGY', case=False)]['amount'].sum()
            zomato_spend = food_df[df['desc'].str.contains('ZOMATO', case=False)]['amount'].sum()
            other_food = food_df['amount'].sum() - swiggy_spend - zomato_spend
            
            chart_data = pd.DataFrame({
                'Platform': ['Swiggy', 'Zomato', 'Other Food'],
                'Amount': [swiggy_spend, zomato_spend, other_food]
            })
            
            total_food = food_df['amount'].sum()
            cap = income * food_pct
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("🍔 Food Total", f"₹{total_food:.0f}")
            col2.metric("🎯 Cap", f"₹{cap:.0f}")
            status = "🚨 Overspend!" if total_food > cap else "✅ Good!"
            col3.metric("Status", status)
            
            # 🔥 CIRCULAR CHART (NEW!)
            st.subheader("📊 Swiggy vs Zomato Breakdown")
            st.markdown("**Percentage Chart**")
            
            col_chart1, col_chart2 = st.columns([3, 1])
            with col_chart1:
                st.bar_chart(chart_data.set_index('Platform'), height=300)
            
            with col_chart2:
                st.metric("🥇 Biggest Spender", 
                         f"{'Swiggy' if swiggy_spend > zomato_spend else 'Zomato'}")
            
            # Food delivery table
            st.subheader("🍕 Food Transactions")
            st.dataframe(food_df[['date', 'desc', 'amount']].sort_values('date'), 
                        use_container_width=True)
            
            # AI BUTTON
            if st.button("🚀 **Generate AI Nudge**", type="primary"):
                st.balloons()
                nudge = get_nudge(total_food, cap)
                st.markdown("### " + nudge)
                
        except Exception as e:
            st.error(f"❌ {e}")
            st.info("**Sample:** `2026-02-10 Swiggy 450`")
else:
    st.info("👆 Upload file to get AI nudge + charts!")
