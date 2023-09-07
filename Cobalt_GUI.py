import requests
import json
import tkinter as tk
from tkinter import filedialog
import os

# Function to handle the download button click
def download_video():
    global file_path_entry, video_url_entry

    # Get the directory path and video URL from the input fields
    download_dir = directory_path.get()
    video_url = video_url_entry.get()

    if not download_dir or not video_url:
        print("Please enter a directory path and a video URL.")
        return

    # Use the file dialog to choose the download location
    file_path = filedialog.asksaveasfilename(
        initialdir=download_dir,
        defaultextension=".mp4",
        filetypes=[("MP4 files", "*.mp4")]
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

    # Define the request body parameters
    request_body = {
        "url": video_url,
        "vCodec": "h264",
        "vQuality": "720",
        "aFormat": "mp3",
        "isAudioOnly": False,
        "isNoTTWatermark": False,
        "isTTFullAudio": False,
        "isAudioMuted": False,
        "dubLang": False
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
window.title("Video Downloader")

# Label and Entry for Directory Path
directory_path_label = tk.Label(window, text="Enter Directory Path:")
directory_path_label.pack()
directory_path = tk.StringVar()
directory_path_entry = tk.Entry(window, textvariable=directory_path)
directory_path_entry.pack()

# Label and Entry for Video URL
video_url_label = tk.Label(window, text="Enter Video URL:")
video_url_label.pack()
video_url_entry = tk.Entry(window)
video_url_entry.pack()

# Download Button
download_button = tk.Button(window, text="Download Video", command=download_video)
download_button.pack()

# Start the tkinter main loop
window.mainloop()

