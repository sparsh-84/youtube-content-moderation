import streamlit as st
from pytube import YouTube
from utilities import get_yt, transcribe_yt
from streamlit_option_menu import option_menu
import time
import glob
import os
from pathlib import Path
from PIL import Image
from gtts import gTTS
from googletrans import Translator

with st.sidebar:
    selected = option_menu(
        menu_title="main menu",
        options=["content moderation", "text-to-speech"],
        icons=["youtube", "mic"],
        menu_icon="cast",
    )
if selected == "content moderation":
    image = Image.open("moderation.jpg")
    st.image(image, width=500)
    st.markdown("# **Content Moderation App**")

    st.warning("Awaiting URL input in the sidebar.")

    # Sidebar
    st.sidebar.header("Input parameter")

    with st.sidebar.form(key="my_form"):
        URL = st.text_input("Enter URL of YouTube video:")
        submit_button = st.form_submit_button(label="Go")

    # Run custom functions if URL is entered
    if submit_button:
        get_yt(URL)
        transcribe_yt()

        with open("transcription.zip", "rb") as zip_download:
            btn = st.download_button(
                label="Download ZIP",
                data=zip_download,
                file_name="transcription.zip",
                mime="application/zip",
            )

    with st.sidebar.expander("Example URL"):
        st.code("https://www.youtube.com/watch?v=twG4mr6Jov0")
if selected == "text-to-speech":
    image1 = Image.open("speech.jpg")
    st.image(image1, width=500)

    try:
        os.mkdir("temp")
    except:
        pass
    st.title("Text to speech")
    translator = Translator()

    text = st.text_input("Enter text")
    in_lang = st.selectbox(
        "Select your input language",
        ("English", "Hindi", "Bengali", "korean", "Chinese", "Japanese"),
    )
    if in_lang == "English":
        input_language = "en"
    elif in_lang == "Hindi":
        input_language = "hi"
    elif in_lang == "Bengali":
        input_language = "bn"
    elif in_lang == "korean":
        input_language = "ko"
    elif in_lang == "Chinese":
        input_language = "zh-cn"
    elif in_lang == "Japanese":
        input_language = "ja"

    out_lang = st.selectbox(
        "Select your output language",
        ("English", "Hindi", "Bengali", "korean", "Chinese", "Japanese"),
    )
    if out_lang == "English":
        output_language = "en"
    elif out_lang == "Hindi":
        output_language = "hi"
    elif out_lang == "Bengali":
        output_language = "bn"
    elif out_lang == "korean":
        output_language = "ko"
    elif out_lang == "Chinese":
        output_language = "zh-cn"
    elif out_lang == "Japanese":
        output_language = "ja"

    english_accent = st.selectbox(
        "Select your english accent",
        (
            "Default",
            "India",
            "United Kingdom",
            "United States",
            "Canada",
            "Australia",
            "Ireland",
            "South Africa",
        ),
    )

    if english_accent == "Default":
        tld = "com"
    elif english_accent == "India":
        tld = "co.in"

    elif english_accent == "United Kingdom":
        tld = "co.uk"
    elif english_accent == "United States":
        tld = "com"
    elif english_accent == "Canada":
        tld = "ca"
    elif english_accent == "Australia":
        tld = "com.au"
    elif english_accent == "Ireland":
        tld = "ie"
    elif english_accent == "South Africa":
        tld = "co.za"

    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(
            text, src=input_language, dest=output_language
        )
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text

    display_output_text = st.checkbox("Display output text")

    if st.button("convert"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## Your audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown(f"## Output text:")
            print(f" {output_text}")

            st.write(f" {output_text}")

    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Deleted ", f)

    remove_files(7)
