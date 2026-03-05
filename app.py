import streamlit as st
import cv2
import pandas as pd
import os
from datetime import datetime

# --------- File Setup ----------
DATA_FILE = 'visitors.csv'
IMAGE_DIR = 'visitor_photos'

# Fix error if file named 'visitor_photos' already exists
if os.path.exists(IMAGE_DIR):
    if os.path.isfile(IMAGE_DIR):
        os.remove(IMAGE_DIR)
os.makedirs(IMAGE_DIR, exist_ok=True)

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=['Name', 'Email', 'Phone', 'Purpose', 'Timestamp', 'Image'])
    df.to_csv(DATA_FILE, index=False)

# --------- Streamlit Config ---------
st.set_page_config(page_title="Visitor Management System", layout="centered")

# --------- Custom CSS for Premium UI ---------
st.markdown("""
    <style>
        body {
            background-color: #FAF3E0;
        }
        .main {
            background-color: #FFF;
            padding: 2rem;
            border-radius: 10px;
        }
        h1, h2 {
            color: #B8860B;
            text-align: center;
        }
        .stTextInput > div > div > input,
        .stTextArea > div > textarea {
            background-color: #FFF8DC;
            color: #000000;
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #ccc;
        }
        .stButton > button {
            background-color: #B8860B;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
        }
        .visitor-card {
            background-color: #f4f4f4;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
        }
         .stContainer {
        background-color: #FAF3E0 !important;
        border-radius: 10px;
        padding: 10px;
    }   
    </style>
""", unsafe_allow_html=True)

# --------- Photo Capture ----------
def capture_photo(filename):
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if not ret:
        st.error("Failed to access camera.")
        return False
    cv2.imwrite(filename, frame)
    cam.release()
    return True

# --------- Visitor Form ----------
def visitor_form():
    st.title("📝 Visitor Entry Form")

    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    purpose = st.text_input("Purpose of Visit")

    if st.button("📸 Capture & Submit"):
        if name and email and phone and purpose:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            img_path = f"{IMAGE_DIR}/{name}_{timestamp}.jpg"

            if capture_photo(img_path):
                # Save data
                new_data = pd.DataFrame([[name, email, phone, purpose, timestamp, img_path]],
                                        columns=['Name', 'Email', 'Phone', 'Purpose', 'Timestamp', 'Image'])
                new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
                st.success("Visitor Registered Successfully!")
                st.image(img_path, caption="Captured Photo", width=250)
        else:
            st.warning("Please fill all the fields.")

# --------- Admin Panel ----------
def admin_panel():
    st.title("🔒 Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")

    if password == "admin123":
        df = pd.read_csv(DATA_FILE)
        st.dataframe(df)

        if st.button("📁 Export Data to CSV"):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Visitor Log", csv, "visitor_log.csv", "text/csv")

        st.subheader("Visitor Photos")
        for idx, row in df.iterrows():
            with st.container():
                st.markdown(f"<div class='visitor-card'><b>{row['Name']}</b> - {row['Purpose']}<br><small>{row['Timestamp']}</small></div>", unsafe_allow_html=True)
                if os.path.exists(row['Image']):
                    st.image(row['Image'], width=200)
    elif password:
        st.error("Incorrect password!")

# --------- Sidebar Menu ---------
menu = st.sidebar.selectbox("Choose Option", ["Visitor Entry", "Admin Panel"])

if menu == "Visitor Entry":
    visitor_form()
else:
    admin_panel()