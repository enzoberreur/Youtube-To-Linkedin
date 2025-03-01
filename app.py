import streamlit as st
import requests
import json
import re
import pandas as pd

# 🔑 Make Webhook URL (Replace with your actual webhook URL)
MAKE_WEBHOOK_URL = "https://hook.eu2.make.com/7troe5wj1k92ydltc39rv7l6ipj7okso"

# 🚀 Streamlit App Title
st.title("TikTok Creative Insight")

# 📩 File uploader for video
uploaded_file = st.file_uploader("📤 Upload a video (MP4)")

# ==========================
# Helper Functions
# ==========================

def send_video_to_make(video_file):
    """Send uploaded video to your Make scenario and return the JSON response."""
    files = {"video": (video_file.name, video_file, "video/mp4")}
    try:
        response = requests.post(MAKE_WEBHOOK_URL, files=files)
        if response.status_code == 200:
            raw_response = response.text
            # Remove any non-UTF-8 characters that could break JSON parsing
            cleaned_response = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', raw_response)
            return json.loads(cleaned_response)
        else:
            st.error(f"❌ Failed to send video. Status code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"🚨 An error occurred: {e}")
        return None

def to_bullet_points(items):
    """
    Convert a list of strings into a single HTML string with bullet points.
    Example: ['Point A', 'Point B'] -> '<ul><li>Point A</li><li>Point B</li></ul>'
    """
    if not items:
        return ""
    html_list = "".join(f"<li>{p}</li>" for p in items)
    return f"<ul>{html_list}</ul>"

def style_table(df):
    """
    Apply custom CSS styling to a DataFrame using Pandas Styler.
    Color-codes the "Score" column based on value.
    Removes unnecessary index column.
    Makes "Criterion" column bold.
    """
    # Remove index manually before styling
    df = df.reset_index(drop=True)  # Ensures no index is displayed

    # Define a function for coloring based on score
    def color_score(val):
        """Apply color formatting based on score range."""
        try:
            val = float(val)  # Ensure it's a number
            if val >= 8:
                return "background-color: #c8e6c9; color: black;"  # Green for high scores
            elif 5 <= val < 8:
                return "background-color: #fff9c4; color: black;"  # Yellow for medium scores
            else:
                return "background-color: #ffccbc; color: black;"  # Red for low scores
        except ValueError:
            return ""  # No color for non-numeric values

    # Define a function to make the Criterion column bold
    def bold_criterion(val):
        """Apply bold formatting to the Criterion column."""
        return "font-weight: bold;" if isinstance(val, str) else ""

    # Convert DataFrame to Styler
    styler = df.style

    # Apply color function to the Score column (if it exists)
    if "Score" in df.columns:
        styler.applymap(color_score, subset=["Score"])

    # Apply bold formatting to the Criterion column
    if "Criterion" in df.columns:
        styler.applymap(bold_criterion, subset=["Criterion"])

    # Set general table styles
    styler.set_properties(
        **{
            'white-space': 'pre-wrap',  # Allow line breaks within cells
            'vertical-align': 'top',    # Align text to the top
            'border-color': '#ddd',     # Table border color
            'border-style': 'solid',
            'border-width': '1px',
            'padding': '8px',
        }
    )

    # Header styling
    styler.set_table_styles([
        {'selector': 'th', 'props': [
            ('background-color', '#f9f9f9'),
            ('color', '#333'),
            ('font-weight', 'bold'),
            ('text-align', 'center'),
            ('border-bottom', '1px solid #ddd'),
        ]},
        {'selector': 'td', 'props': [
            ('text-align', 'left'),
            ('vertical-align', 'top'),
        ]}
    ], overwrite=False)

    # Convert to HTML and REMOVE INDEX COLUMN
    return styler.hide(axis="index").to_html() 


def display_global_assessment(ga_data):
    """Build and display a styled table for the 'globalAssessment' section."""
    # Convert bullet lists into HTML bullet points or multiline strings
    final_score = ga_data.get('finalScore', {})
    major_strengths = to_bullet_points(ga_data.get('majorStrengths', []))
    major_weaknesses = to_bullet_points(ga_data.get('majorWeaknesses', []))
    priority_recs_list = ga_data.get('priorityRecommendations', [])
    # Make them bullet points or numbered lines
    priority_recs_html = "".join(f"{r}<br>" for r in priority_recs_list)
    viral_prob = ga_data.get('estimatedViralProbability', {})
    viral_probability_text = f"{viral_prob.get('percentage', 'N/A')}% – {viral_prob.get('justification', '')}"

    data = [
        {"Criterion": "Final Score", "Value": f"{final_score.get('scoreValue', 'N/A')} / 10"},
        {"Criterion": "Major Strengths", "Value": major_strengths},
        {"Criterion": "Major Weaknesses", "Value": major_weaknesses},
        {"Criterion": "Priority Recommendations", "Value": priority_recs_html},
        {"Criterion": "Estimated Viral Probability", "Value": viral_probability_text},
    ]
    df = pd.DataFrame(data)
    html_table = style_table(df)
    st.markdown(html_table, unsafe_allow_html=True)

def display_detailed_analysis(da_data):
    """Build and display styled tables for each subsection in the 'detailedAnalysis'."""
    # VISUAL QUALITY
    st.subheader("2.1 Visual Quality")
    show_subanalysis(da_data.get("visualQuality", []))

    # AUDIO QUALITY
    st.subheader("2.2 Audio Quality")
    show_subanalysis(da_data.get("audioQuality", []))

    # TEXT ELEMENTS
    st.subheader("2.3 Text Elements")
    show_subanalysis(da_data.get("textElements", []))

    # VIRAL POTENTIAL
    st.subheader("2.4 Viral Potential")
    show_subanalysis(da_data.get("viralPotential", []))

def show_subanalysis(items_list):
    """
    Convert a list of criterion items (each a dict) into a styled DataFrame,
    then render in Streamlit.
    """
    if not items_list:
        st.write("No data available.")
        return

    # Build rows for the DataFrame
    rows = []
    for item in items_list:
        row = {
            "Criterion": item.get("criterion", ""),
            "Score": item.get("score", 0),
            # Use bullet points for lists
            "Strengths": to_bullet_points(item.get("strengths", [])),
            "Weaknesses": to_bullet_points(item.get("weaknesses", [])),
            "Recommendations": to_bullet_points(item.get("recommendations", [])),
        }
        rows.append(row)

    df = pd.DataFrame(rows, columns=["Criterion", "Score", "Strengths", "Weaknesses", "Recommendations"])
    html_table = style_table(df)
    st.markdown(html_table, unsafe_allow_html=True)

def display_analysis(analysis_data):
    """
    Main display function:
    1. Global Assessment
    2. Detailed Analysis
    """
    # 1. GLOBAL ASSESSMENT
    st.header("Global Assessment")
    ga_data = analysis_data.get("globalAssessment", {})
    display_global_assessment(ga_data)

    st.markdown("---")

    # 2. DETAILED ANALYSIS
    st.header("Detailed Analysis")
    da_data = analysis_data.get("detailedAnalysis", {})
    display_detailed_analysis(da_data)

# ==========================
# Main App Logic
# ==========================

# 🎯 Process the uploaded video
if uploaded_file and st.button("Analyze Video"):
    with st.spinner("⏳ Uploading video and analyzing... This may take up to 60 seconds."):
        response = send_video_to_make(uploaded_file)

        if response:
            # If your Make scenario returns the entire JSON in a single field, adjust accordingly.
            # For example, if the entire JSON is under the key 'analysis_json':
            # analysis_data = response.get("analysis_json", {})
            #
            # Otherwise, if the response itself is the JSON structure:
            analysis_data = response

            # Display the analysis in a styled format
            display_analysis(analysis_data)
        else:
            st.error("❌ Failed to receive a response from the Make scenario.")
