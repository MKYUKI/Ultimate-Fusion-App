# app.py

import streamlit as st
from streamlit_option_menu import option_menu
from database import get_db, authenticate_user, add_user, user_exists, email_exists, get_user, log_activity
from helpers import (
    notify,
    synthesize_speech_chunk,
    classify_image,
    clear_exif_data,
    download_image,
    plot_exif_statistics,
    detect_language
)
import pandas as pd
from PIL import Image
import os
import io
import json

# ログイン状態の管理
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = False
    st.session_state['username'] = None

# ユーザー認証
def login(db):
    st.sidebar.header("Login")
    with st.sidebar.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            user = authenticate_user(username, password, db)
            if user:
                st.session_state['authentication_status'] = True
                st.session_state['username'] = username
                log_activity(user.id, "User logged in.", db)
                notify("Login successful!", type="success")
            else:
                st.sidebar.error("Invalid username or password.")
                notify("Invalid username or password.", type="error")

def register(db):
    st.sidebar.header("Register")
    with st.sidebar.form("registration_form"):
        new_username = st.text_input("Username")
        new_name = st.text_input("Name")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            if not new_username or not new_name or not new_password or not new_email:
                st.sidebar.error("Please fill in all fields.")
                notify("Please fill in all fields.", type="error")
            elif not is_valid_email(new_email):
                st.sidebar.error("Please enter a valid email address.")
                notify("Please enter a valid email address.", type="error")
            elif new_password != confirm_password:
                st.sidebar.error("Passwords do not match.")
                notify("Passwords do not match.", type="error")
            elif user_exists(new_username, db):
                st.sidebar.error("This username already exists. Please choose another one.")
                notify("This username already exists. Please choose another one.", type="error")
            elif email_exists(new_email, db):
                st.sidebar.error("This email address is already registered. Please use another email address.")
                notify("This email address is already registered. Please use another email address.", type="error")
            else:
                user = add_user(new_username, new_name, new_password, new_email, db)
                log_activity(user.id, "User registered.", db)
                st.sidebar.success("Registration completed. Please log in.")
                notify("Registration completed. Please log in.", type="success")

def is_valid_email(email: str) -> bool:
    import re
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

def main():
    st.set_page_config(page_title="Ultimate Fusion App", layout="wide", initial_sidebar_state="expanded")
    
    # スタイルの適用
    with open('styles/custom.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # ユーザー認証
    db = next(get_db())
    if not st.session_state['authentication_status']:
        login(db)
        register(db)
        if not st.session_state['authentication_status']:
            st.warning("Please log in or register to continue.")
            st.stop()
    
    username = st.session_state['username']
    user = get_user(username, db)
    
    # サイドバーのメニュー
    selected = option_menu(
        menu_title="Main Menu",
        options=["Dashboard", "EXIF Analysis", "Text-to-Speech", "GPT Conversation", "Image Classification", "Profile", "Feedback", "Logout"],
        icons=["speedometer2", "file-earmark", "speaker", "chat-dots", "image", "person-circle", "envelope", "box-arrow-right"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
    )
    
    # メニュー項目に応じたコンテンツの表示
    if selected == "Dashboard":
        st.title("Dashboard")
        st.write("Welcome to the Ultimate Fusion App Dashboard!")
        # ここにダッシュボードのコンテンツを追加
    
    elif selected == "EXIF Analysis":
        st.title("EXIF Data Analysis")
        uploaded_file = st.file_uploader("Upload an image to analyze EXIF data", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            exif_data = image.getexif()
            if exif_data:
                exif_dict = {
                    ExifTags.TAGS.get(tag, tag): value
                    for tag, value in exif_data.items()
                }
                exif_df = pd.DataFrame(list(exif_dict.items()), columns=["Attribute", "Value"])
                st.dataframe(exif_df)
                
                # 統計情報と視覚化
                stats = get_exif_statistics(exif_df)
                st.subheader("EXIF Statistics")
                plot_exif_statistics(pd.DataFrame(stats))
                
                # EXIFデータの除去
                if st.button("Remove EXIF Data"):
                    image_no_exif = clear_exif_data(image)
                    st.image(image_no_exif, caption="Image without EXIF Data", use_column_width=True)
                    download_image(image_no_exif)
                    log_activity(user.id, "Removed EXIF data from an image.", db)
                    notify("EXIF data removed and image is ready for download.", type="success")
            else:
                st.warning("No EXIF data found in the uploaded image.")
                notify("No EXIF data found in the uploaded image.", type="info")
    
    elif selected == "Text-to-Speech":
        st.title("Text-to-Speech (TTS)")
        text_input = st.text_area("Enter text to convert to speech", height=200)
        lang_code = st.selectbox("Select Language", ["en-US", "ja-JP", "fr-FR", "es-ES"])
        gender = st.selectbox("Select Gender", ["default", "male", "female"])
        if st.button("Convert to Speech"):
            if text_input.strip() == "":
                st.error("Please enter some text.")
                notify("Please enter some text.", type="error")
            else:
                audio_content = synthesize_speech_chunk(text_input, lang_code, gender)
                st.audio(audio_content, format="audio/mp3")
                # ダウンロードボタン
                st.download_button(
                    label="Download Audio",
                    data=audio_content,
                    file_name="speech.mp3",
                    mime="audio/mp3",
                )
                log_activity(user.id, "Converted text to speech.", db)
                notify("Text successfully converted to speech.", type="success")
    
    elif selected == "GPT Conversation":
        st.title("GPT Conversation")
        user_input = st.text_input("You: ")
        if st.button("Send"):
            if user_input.strip() == "":
                st.error("Please enter a message.")
                notify("Please enter a message.", type="error")
            else:
                # GPTとの対話処理（モックアップ）
                # 実際のAPI呼び出しをここに実装
                response = "This is a mock response from GPT."
                st.write(f"GPT: {response}")
                log_activity(user.id, f"Sent message: {sanitize_input(user_input)}", db)
                notify("Message sent to GPT.", type="success")
    
    elif selected == "Image Classification":
        st.title("AI Image Classification")
        uploaded_file = st.file_uploader("Upload an image for classification", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            if st.button("Classify Image"):
                # 画像の保存
                image_path = f"uploads/{uploaded_file.name}"
                os.makedirs("uploads", exist_ok=True)
                image.save(image_path)
                
                # 画像分類
                replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
                classification_result = classify_image(image_path, replicate_api_token)
                
                if "error" not in classification_result:
                    st.json(classification_result)
                    log_activity(user.id, f"Classified image: {uploaded_file.name}", db)
                    notify("Image classified successfully.", type="success")
                else:
                    st.error("Image classification failed.")
                    log_activity(user.id, f"Image classification failed for: {uploaded_file.name}", db)
                    notify("Image classification failed.", type="error")
    
    elif selected == "Profile":
        st.title("User Profile")
        st.subheader(f"Username: {user.username}")
        st.subheader(f"Name: {user.name}")
        st.subheader(f"Email: {user.email}")
        # 外部リンクの管理などの追加機能をここに実装
        # 例:
        st.write("External Links:")
        st.markdown("""
            - [GitHub](https://github.com/)
            - [YouTube](https://www.youtube.com/)
            - [PayPal](https://www.paypal.com/)
        """)
    
    elif selected == "Feedback":
        st.title("Feedback")
        feedback_input = st.text_area("Enter your feedback", height=150)
        if st.button("Submit Feedback"):
            if feedback_input.strip() == "":
                st.error("Please enter your feedback.")
                notify("Please enter your feedback.", type="error")
            else:
                # フィードバックの追加
                from database import add_feedback
                add_feedback(user.id, sanitize_input(feedback_input), db)
                log_activity(user.id, "Submitted feedback.", db)
                st.success("Feedback submitted successfully.")
                notify("Feedback submitted successfully.", type="success")
    
    elif selected == "Logout":
        st.session_state['authentication_status'] = False
        st.session_state['username'] = None
        st.experimental_rerun()
    
def sanitize_input(user_input: str) -> str:
    import html
    return html.escape(user_input)

if __name__ == "__main__":
    main()
