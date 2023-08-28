import streamlit as st
import os
from time import sleep
import requests
from pytube import YouTube
from zipfile import ZipFile
import json as js
import matplotlib.pyplot as plt
import pandas as pd

bar = st.progress(0)

# 1. API
# api_key = st.secrets['api_key']

# 2. Retrieving audio file from YouTube video


def get_yt(inputURL):
    video = YouTube(
        inputURL,
        use_oauth=True,
        allow_oauth_cache=True,
    )

    yt = video.streams.filter(only_audio=True).first()  # retrieving only the audio
    # stream = yt.streams.get_by_itag(22)
    # stream.download()
    yt.download()

    st.info("2. Audio file has been retrieved from YouTube video")
    bar.progress(10)


# 3. Upload YouTube audio file to AssemblyAI


def transcribe_yt():
    current_dir = os.getcwd()

    for file in os.listdir(current_dir):
        if file.endswith(".mp4"):
            mp4_file = os.path.join(current_dir, file)
            # print(mp4_file)
    filename = mp4_file  # audio file assigned to filename variable
    bar.progress(20)

    def read_file(filename, chunk_size=5242880):  # reading the audio
        with open(filename, "rb") as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data

    # upload the audio the assembly AI server
    headers = {"authorization": "468045779dd641008387972a87563241"}
    response = requests.post(
        "https://api.assemblyai.com/v2/upload",
        headers=headers,
        data=read_file(filename),
    )
    audio_url = response.json()["upload_url"]
    st.info("3. YouTube audio file has been uploaded to AssemblyAI")
    bar.progress(30)

    # 4. Transcribe uploaded audio file
    endpoint = "https://api.assemblyai.com/v2/transcript"

    json = {
        "audio_url": audio_url,
        "content_safety": True,
        "filter_profanity": True,
        "summarization": True,
        "summary_model": "informative",
        "summary_type": "bullets",
    }

    headers = {
        "authorization": "468045779dd641008387972a87563241",
        "content-type": "application/json",
    }

    transcript_input_response = requests.post(endpoint, json=json, headers=headers)

    st.info("4. Transcribing uploaded file")
    bar.progress(40)

    # 5. Extract transcript ID
    transcript_id = transcript_input_response.json()["id"]
    st.info("5. Extract transcript ID")
    bar.progress(50)

    # 6. Retrieve transcription results
    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    headers = {
        "authorization": "468045779dd641008387972a87563241",
    }
    transcript_output_response = requests.get(endpoint, headers=headers)
    st.info("6. Retrieve transcription results")
    bar.progress(60)

    # Check if transcription is complete

    st.warning("Transcription is processing ...")
    while transcript_output_response.json()["status"] != "completed":
        sleep(1)
        transcript_output_response = requests.get(endpoint, headers=headers)

    bar.progress(100)

    # 7. Print transcribed text
    st.header("Output")

    with st.expander("Show Text"):
        st.code(transcript_output_response.json()["text"])

    # 8. Save transcribed text to file

    # Save as TXT file
    yt_txt = open("yt.txt", "w")
    yt_txt.write(transcript_output_response.json()["text"])
    yt_txt.close()

    # 9. Write JSON to app
    with st.expander("Show Full Results"):
        st.write(transcript_output_response.json())

    # 10. Write content_safety_labels
    with st.expander("Show content_safety_labels"):
        st.write(transcript_output_response.json()["content_safety_labels"])

    with st.expander("Summary of content_safety_labels"):
        st.write(transcript_output_response.json()["content_safety_labels"]["summary"])

    # Save as SRT file
    srt_endpoint = endpoint + "/srt"
    srt_response = requests.get(srt_endpoint, headers=headers)
    with open("yt.srt", "w") as _file:
        _file.write(srt_response.text)

    zip_file = ZipFile("transcription.zip", "w")
    zip_file.write("yt.txt")
    zip_file.write("yt.srt")
    zip_file.close()
    data = transcript_output_response.json()["content_safety_labels"]["summary"]
    json_string = js.dumps(data)
    st.download_button(
        label="Download JSON",
        file_name="data.json",
        mime="application/json",
        data=json_string,
    )
    obj = js.loads(json_string)
    read_content = obj
    st.write(read_content)
    for i in read_content:
        plt.bar(i, read_content[i])
    plt.xlabel("Safety labels", fontweight="bold")
    plt.ylabel("Severity(scale of 0-1)", fontweight="bold")
    st.pyplot()
    st.set_option("deprecation.showPyplotGlobalUse", False)
    count = 0
    for i in read_content:
        if read_content[i] > 0.6:
            count = count + 1
    if count >= len(read_content) / 2:
        st.info(
            "The above content may not be suitable for certain age groups, viewer discretion is advised"
        )
    else:
        st.info("The content is safe to view")
    # courses = []
    # values = []
    # for value in list:
    #    st.write(value)
    # courses[i] = list(i)
    # values[i] = list(list[i])
    # plt.bar(courses[i], values[i], color="maroon", width=0.4)
    # plt.show()
    # x = type(value)
    # st.write(x)
    # st.json(json_string, expanded=True)
    # label = []
    # myjsonfile = open(r"C:\Users\samar\Downloads\data (1).json", "w+")
    # jsondata = myjsonfile.read()
    # obj = js.loads(jsondata)
    # list = obj["summary"]
    ## for i in range(len(list)):
    ##    label.append(list[i])
    # st.write(list)
    ## st.write(output)
    ## Delete processed files
    for file in os.listdir(current_dir):
        if file.endswith(".mp4"):
            os.remove(file)
        if file.endswith(".txt"):
            os.remove(file)
        if file.endswith(".srt"):
            os.remove(file)
