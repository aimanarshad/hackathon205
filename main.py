







import streamlit as st
import pandas as pd
import google.generativeai as genai
import json

# Load CSV file
doctors_df = pd.read_csv("generated_doctors.csv")

# Gemini API key (replace with your actual key)
genai.configure(api_key="AIzaSyC6PGA4sJostUymohIW6iMRi_ckvqaQErU")
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Page Config
st.set_page_config(page_title="🧠 Smart Doctor Finder", layout="centered", page_icon="🩺")

# --- HEADER SECTION ---
st.markdown("""
    <h1 style='text-align: center; color: #4A90E2;'>🤖 GenAI-Powered Doctor Discovery & Query Assistant</h1>
    <p style='text-align: center; font-size:18px;'>Powered by Google Gemini – Just describe your symptoms and let AI recommend the right doctor!</p>
    <hr style='border: 1px solid #ccc;' />
""", unsafe_allow_html=True)

# --- USER INPUT ---
st.markdown("### 📝 Describe your Health Issue")
user_symptom = st.text_input("💬 Example: 'Chest pain and shortness of breath'")

# Process input with Gemini
if user_symptom:
    with st.spinner("🔍 Gemini is analyzing your symptoms..."):
        prompt = f"""
        A user described their symptoms as:
        "{user_symptom}"

        Based on this, suggest the most relevant medical specialty from this list:
        - Cardiologist
        - Neurologist
        - Dermatologist
        - Orthopedic
        - ENT
        - Pediatrician
        - Psychiatrist
        - Urologist
        - Gynecologist
        - General Physician

        Respond ONLY in JSON format like:
        {{
          "specialty": "Cardiologist",
          "reason": "Because chest pain and breath issues usually relate to heart function."
        }}
        """
        try:
            gemini_response = model.generate_content(prompt)
            cleaned_response = gemini_response.text.strip("```json").strip("```").strip()
            first_json_block = cleaned_response.split("}\n")[0] + "}"
            response_json = json.loads(first_json_block)

            specialty = response_json["specialty"]
            reason = response_json["reason"]

            # Filter doctors by specialty
            match_df = doctors_df[doctors_df["specialty"].str.lower() == specialty.lower()]

            if match_df.empty:
                st.warning(f"No doctors found for specialty: **{specialty}**.")
            else:
                st.success(f"✅ Recommended Specialty: **{specialty}**")
                st.markdown(f"<span style='color:gray'>🧠 Gemini’s Reasoning: <i>{reason}</i></span>", unsafe_allow_html=True)

                # --- FILTER SECTION ---
                st.markdown("### 🔍 Refine Your Search")

                with st.container():
                    col1, col2 = st.columns(2)
                    with col1:
                        selected_city = st.selectbox("🏙️ City", options=["All"] + sorted(match_df["city"].dropna().unique()))
                        selected_gender = st.selectbox("👤 Gender", options=["All"] + sorted(match_df["gender"].dropna().unique()))
                    with col2:
                        selected_avail = st.selectbox("📅 Availability", options=["All"] + sorted(match_df["availability"].dropna().unique()))
                        selected_emergency = st.selectbox("🚨 Emergency Support", options=["All"] + sorted(match_df["emergency_available"].dropna().unique()))

                # Apply filters
                filtered_df = match_df.copy()
                if selected_city != "All":
                    filtered_df = filtered_df[filtered_df["city"] == selected_city]
                if selected_gender != "All":
                    filtered_df = filtered_df[filtered_df["gender"] == selected_gender]
                if selected_avail != "All":
                    filtered_df = filtered_df[filtered_df["availability"] == selected_avail]
                if selected_emergency != "All":
                    filtered_df = filtered_df[filtered_df["emergency_available"] == selected_emergency]

                # --- DISPLAY DOCTORS ---
                st.markdown("### 🩺 Available Doctors")
                if filtered_df.empty:
                    st.error("❌ No matching doctors found.")
                else:
                    for _, row in filtered_df.iterrows():
                        st.markdown(f"""
                            <div style='background-color: #f1f6fb; padding: 15px; border-radius: 10px; margin-bottom: 15px ; color:blue'>
                                <h4 style='color:#2c3e50;'>👨‍⚕️ {row['doctor_name']} ({row['specialty']})</h4>
                                <ul style='line-height: 1.6;'>
                                    <li><strong>🏥 Hospital:</strong> {row['hospital']}</li>
                                    <li><strong>🏙️ City:</strong> {row['city']}</li>
                                    <li><strong>👤 Gender:</strong> {row['gender']}</li>
                                    <li><strong>📅 Availability:</strong> {row['availability']}</li>
                                    <li><strong>⏳ Experience:</strong> {row['experience']} years</li>
                                    <li><strong>🚨 Emergency:</strong> {row['emergency_available']}</li>
                                </ul>
                            </div>
                        """, unsafe_allow_html=True)

        except Exception as e:
            st.error("❌ Gemini failed to respond or returned invalid data.")
            st.exception(e)
