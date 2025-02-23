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

# 📝 Input for User Comment
user_comment = st.text_area("💬 Add a comment or specify details about the desired result (e.g., 'Focus on this subject of the video')")

# 🌐 Input for Language Selection
language = st.text_input("🌍 Enter the desired language for the post:", "English")

# 📌 Function to trigger Make scenario and clean JSON response
def trigger_make_scenario(youtube_link, user_comment, language):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "youtube_link": youtube_link,
        "user_comment": user_comment,
        "language": language
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
            trigger_response = trigger_make_scenario(youtube_link, user_comment, language)
            if trigger_response:
                article_text = trigger_response.get("article_text", "No article text received.")
                image_url = trigger_response.get("image_url", None)
                rate = trigger_response.get("rate", "No rate received.")
                
                safe_article_text = article_text.replace("\t", "    ").replace("\r", "").replace("\n", "\n")

                st.subheader("📰 Generated Article:")
                st.markdown(safe_article_text, unsafe_allow_html=True)

                if image_url:
                    st.subheader("🖼️ Generated Image:")
                    st.image(image_url)
                else:
                    st.warning("⚠️ No image received from Make.")

                st.subheader("📊 Article Rating:")
                st.write(f"Rating: {rate}/20")
                
            else:
                st.error("❌ Failed to receive a response from the Make scenario.")
    else:
        st.warning("⚠️ Please enter a valid YouTube link.")
