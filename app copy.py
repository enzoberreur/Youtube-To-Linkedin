import streamlit as st
import requests
import json
import time
import re

# 🔑 Make Webhook URL (Replace with your actual webhook URL from Make)
MAKE_WEBHOOK_URL = "https://hook.eu2.make.com/7troe5wj1k92ydltc39rv7l6ipj7okso"

# 🚀 Streamlit App Title
st.title("📝 YouTube to LinkedIn Generator")

# 📩 Input for YouTube Link
youtube_link = st.text_input("🔗 Enter a YouTube Link:", "")

# 📌 Function to trigger Make scenario and clean JSON response
def trigger_make_scenario(youtube_link):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "youtube_link": youtube_link
    }
    try:
        response = requests.post(MAKE_WEBHOOK_URL, headers=headers, json=payload)
        if response.status_code == 200:
            raw_response = response.text
            cleaned_response = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', raw_response)
            return json.loads(cleaned_response)
        else:
            st.error(f"❌ Failed to trigger scenario. Status code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"🚨 An error occurred: {e}")
        return None

# 🎯 Main Logic to Generate Article
if st.button("Generate Article"):
    if youtube_link:
        with st.spinner("⏳ Generating article, please wait... This may take up to 60 seconds."):
            trigger_response = trigger_make_scenario(youtube_link)
            if trigger_response:
                article_text = trigger_response.get("article_text", "No article text received.")

                
                safe_article_text = article_text.replace("\t", "    ").replace("\r", "").replace("\n", "\n")

                st.subheader("📰 Generated Advice:")
                st.markdown(safe_article_text, unsafe_allow_html=True)
                
            else:
                st.error("❌ Failed to receive a response from the Make scenario.")
    else:
        st.warning("⚠️ Please enter a valid YouTube link.")
