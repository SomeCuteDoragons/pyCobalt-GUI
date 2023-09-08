import requests
import json
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
import os
import re

# Define variables for the request body values
video_url = ""
vCodec = "h264"
vQuality = "720"
aFormat = "mp3"  # Please don't set to best :)
isAudioOnly = False
isNoTTWatermark = False
isTTFullAudio = False
isAudioMuted = False
dubLang = False

# Function to extract the file extension from the Content-Disposition header
def extract_file_extension(response):
    content_disposition = response.headers.get('Content-Disposition')
    if content_disposition:
        match = re.search(r'filename="(.+)"', content_disposition)
        if match:
            filename = match.group(1)
            _, file_extension = os.path.splitext(filename)
            return file_extension.lower()
    return None

# Function to handle the download button click
def download_video():
    global video_url, vCodec, vQuality, aFormat, isAudioOnly, isNoTTWatermark, isTTFullAudio, isAudioMuted, dubLang

    # Get the video URL from the input field
    video_url = video_url_entry.get()

    if not video_url:
        print("Please enter a video URL.")
        return

    # Determine the file extension based on the selected video codec or audio format
    if not isAudioOnly:
        if vCodec.lower() in ("h264", "av1"):
            file_extension = ".mp4"
        elif vCodec.lower() == "vp9":
            file_extension = ".webm"
        else:
            print(f"Invalid vCodec value: {vCodec}")
            return
    else:
        if aFormat.lower() == "mp3":
            file_extension = ".mp3"
        elif aFormat.lower() == "ogg":
            file_extension = ".ogg"
        elif aFormat.lower() == "wav":
            file_extension = ".wav"
        elif aFormat.lower() == "opus":
            file_extension = ".opus"
        else:
            print(f"Invalid aFormat value: {aFormat}")
            return

    # Use the file dialog to choose the download location
    file_path = filedialog.asksaveasfilename(
        defaultextension=file_extension,
        filetypes=[(f"{file_extension[1:].upper()} files", "*" + file_extension)]
    )

    if not file_path:
        print("Download canceled.")
        return

    # Define the base URL for the Cobalt API
    base_url = "https://co.wuk.sh"

    # Define the endpoint for the POST request
    endpoint = "/api/json"

    # Construct the full API URL
    api_url = base_url + endpoint

    # Define the request body parameters using the variables
    request_body = {
        "url": video_url,
        "vCodec": vCodec,
        "vQuality": vQuality,
        "aFormat": aFormat,
        "isAudioOnly": isAudioOnly,
        "isNoTTWatermark": isNoTTWatermark,
        "isTTFullAudio": isTTFullAudio,
        "isAudioMuted": isAudioMuted,
        "dubLang": dubLang
    }

    # Define the headers with the "Accept" header set to "application/json"
    headers = {
        "Accept": "application/json"
    }

    # Send a POST request to the API with the headers
    response = requests.post(api_url, json=request_body, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()

        # Process the JSON response here
        print("Response Data:", json.dumps(data, indent=4))

        # Check if the response contains a file URL
        if 'url' in data:
            file_url = data['url']

            # Extract the directory path from the chosen file path
            download_dir = os.path.dirname(file_path)

            # Ensure that the download directory exists, create it if necessary
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)

            # Download and save the file to the chosen location
            file_response = requests.get(file_url)

            if file_response.status_code == 200:
                with open(file_path, 'wb') as file:
                    file.write(file_response.content)

                print(f"File '{file_path}' has been downloaded and saved.")
            else:
                print(f"Error downloading file: Status code {file_response.status_code}")
                print("Response Content:", file_response.text)
        else:
            print("No file URL found in the API response.")
    else:
        print(f"Error: Request failed with status code {response.status_code}")
        print("Response Content:", response.text)


# Create the tkinter window
window = tk.Tk()
window.title("pyCobalt Downloader")
window.geometry("640x480")

# Label and Entry for Video URL
video_url_label = tk.Label(window, text="Enter Video URL:")
video_url_label.pack()
video_url_entry = tk.Entry(window)
video_url_entry.pack()

# Download Button
download_button = tk.Button(window, text="Download Media", command=download_video)
download_button.pack()

# Start the tkinter main loop
window.mainloop()
