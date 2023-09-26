from platform import release
from turtle import title
import requests
import json
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os

# Special thanks to mikhail from cobaltcord for the code makeover of the part that downloads the video/audio :3
# Special thanks to cobaltcord and chatgpt for help
# You don't know what this comment is for :wink:

# Global variables / magic values
VIDEO_CODECS = {
    "vp9": ".webm",
    "av1": ".mp4",
    "h264": ".mp4"
}
COBALT_API_URL = "https://co.wuk.sh/api/json"

KIBIBYTE = 1024
MEBIBYTE = KIBIBYTE * KIBIBYTE

CHUNK_SIZE = KIBIBYTE * 8

# Define variables for the request body values
video_url = ""
video_codec = "h264"
video_quality = "720"
audio_format = "mp3"  # Still can't set it to best
is_audio_only = False
disable_tiktok_watermark = False
is_tiktok_full_audio = False
is_audio_muted = False
dub_lang = False
disableMetadata = False


# Function that makes the size in bytes as an human-readable string
def humanize_size(size_bytes):
    if size_bytes < KIBIBYTE:
        return f"{size_bytes} bytes"

    if size_bytes > KIBIBYTE and MEBIBYTE > size_bytes:
        return f"{size_bytes / KIBIBYTE} KiB"

    return f"{size_bytes / MEBIBYTE} MiB"

def on_select_audio_format(event):
    global audio_format
    audio_format = audio_format_combobox.get()

def on_select_video_codec(event):
    global video_codec
    video_codec = video_codec_combobox.get()
    
def on_audio_only_toggle():
    global is_audio_only
    is_audio_only = audio_only_var.get()

# Function to handle the download button click
def download_video():
    global video_url, video_codec, video_quality, audio_format, is_audio_only, disable_tiktok_watermark, is_tiktok_full_audio, is_audio_muted, dub_lang, disableMetadata

    # Get the video URL from the input field
    video_url = video_url_entry.get()

    if not video_url:
        print("Please enter a video URL.")
        return

    # Determine the file extension based on the selected video codec or audio format
    file_extension = VIDEO_CODECS[video_codec] if not is_audio_only else "." + audio_format

    # Use the file dialog to choose the download location
    file_path = filedialog.asksaveasfilename(
        defaultextension=file_extension,
        filetypes=[(f"{file_extension[1:].upper()} files", "*" + file_extension)]
    )

    if not file_path:
        print("Download canceled.")
        return

    # Define the request body parameters using the variables
    request_body = {
        "url": video_url,
        "vCodec": video_codec,
        "vQuality": video_quality,
        "aFormat": audio_format,
        "isAudioOnly": is_audio_only,
        "isNoTTWatermark": disable_tiktok_watermark,
        "isTTFullAudio": is_tiktok_full_audio,
        "isAudioMuted": is_audio_muted,
        "dubLang": dub_lang,
        "disableMetadata": disableMetadata
    }

    # Define the headers with the "Accept" header set to "application/json"
    headers = {"accept": "application/json"}

    # Send a POST request to the API with the headers
    response = requests.post(COBALT_API_URL, json=request_body, headers=headers)

    if response.status_code != 200:
        print(f"Error: Request failed with status code {response.status_code}")
        print("Response Content:", response.text)

        return

    data = response.json()

    # Process the JSON response here
    print("Response Data:", json.dumps(data, indent=4))

    if "url" not in data:
        print("No file URL found in the API response.")

        return

    file_url = data["url"]

    # Extract the directory path from the chosen file path
    download_dir = os.path.dirname(file_path)

    # Ensure that the download directory exists, create it if necessary
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Download and save the file to the chosen location
    file_response = requests.get(file_url, stream=True)

    if file_response.status_code != 200:
        print(f"Error downloading file: Status code {file_response.status_code}")
        print("Response Content:", file_response.text)

        return

    current_file_size = 0

    # Downloading the file
    with open(file_path, "wb") as file:
        for chunk in file_response.iter_content(chunk_size=CHUNK_SIZE):
            file.write(chunk)
            current_file_size = file.tell()

            if current_file_size % MEBIBYTE == 0:
                current_file_size = humanize_size(current_file_size)
                print(f"Downloaded {current_file_size} of content.")

    current_file_size = humanize_size(current_file_size)
    print(f"File '{file_path}' has been downloaded and saved. File size is {current_file_size}")

# Function to open a new Tkinter window
def open_new_window():
    advWin = tk.Toplevel()
    advWin.title("Advanced Options")
    advWin.geometry("350x350+770+325")
    
    releaseVersion = ttk.Label(advWin, text="Version: Pre-Prerelease C1") # Monika please remember to change this
    releaseVersion.place(x=100, y=5)


def main():
    global video_url_entry, audio_format_combobox, video_codec_combobox

    window = tk.Tk()
    window.title("pyCobalt GUI")
    window.geometry("650x480+600+250")
    window.resizable(False, False)
    

    title_label = ttk.Label(window, text="pyCobalt", font=("Segoe_UI 20"))
    title_label.place(x=270, y=10)

    video_url_label = ttk.Label(window, text="Enter Video URL:")
    video_url_label.place(x=280, y=105)
    
    def paste_from_clipboard():
        clipboard_text = window.clipboard_get()
        video_url_entry.delete(0, tk.END)
        video_url_entry.insert(0, clipboard_text)


    paste_button = ttk.Button(window, text="Paste from Clipboard", command=paste_from_clipboard)
    paste_button.place(x=250, y=380)  # Adjust the coordinates as needed


    video_url_entry = ttk.Entry(window, width=40, font=("Arial 16"))
    video_url_entry.place(x=95, y=150, height=30)

    audio_format_label = ttk.Label(window, text="Select Audio Format:")
    audio_format_label.place(x=95, y=200)

    audio_formats = ["mp3", "wav", "opus", "ogg"]
    audio_format_combobox = ttk.Combobox(window, values=audio_formats)
    audio_format_combobox.set(audio_format)
    audio_format_combobox.bind("<<ComboboxSelected>>", on_select_audio_format)
    audio_format_combobox.place(x=280, y=200)

    video_codec_label = ttk.Label(window, text="Select Video Codec:")
    video_codec_label.place(x=95, y=225)

    video_codecs = list(VIDEO_CODECS.keys())
    video_codec_combobox = ttk.Combobox(window, values=video_codecs)
    video_codec_combobox.set(video_codec)
    video_codec_combobox.bind("<<ComboboxSelected>>", on_select_video_codec)
    video_codec_combobox.place(x=280, y=225)
    
    # Create a Label for video quality
    video_quality_label = ttk.Label(window, text="Select Video Quality:")
    video_quality_label.place(x=95, y=250)

    # Define the video quality options
    video_quality_options = ["360", "480", "720", "1080", "1440", "2160", "max"]

    # Create a Combobox for video quality
    video_quality_combobox = ttk.Combobox(window, values=video_quality_options)
    video_quality_combobox.set(video_quality)
    video_quality_combobox.place(x=280, y=250)

    # Function to handle the selection of video quality
    def on_select_video_quality(event):
        global video_quality
        video_quality = video_quality_combobox.get()

    # Bind the function to the Combobox selection event
    video_quality_combobox.bind("<<ComboboxSelected>>", on_select_video_quality)


    # Create a Checkbutton for audio_only dingle bingle
    audio_only_var = tk.BooleanVar()
    def on_audio_only_toggle():
        global is_audio_only
        is_audio_only = audio_only_var.get()
    audio_only_checkbox = ttk.Checkbutton(window, text="Audio Only", variable=audio_only_var, command=on_audio_only_toggle)
    audio_only_checkbox.place(x=95, y=285)
    
    # Create a Checkbutton for disable_tiktok_watermark
    tiktok_watermark_var = tk.BooleanVar()
    def on_tiktok_watermark_toggle():
        global disable_tiktok_watermark
        disable_tiktok_watermark = tiktok_watermark_var.get()

    tiktok_watermark_checkbox = ttk.Checkbutton(window, text="Hide TikTok Watermark", variable=tiktok_watermark_var, command=on_tiktok_watermark_toggle)
    tiktok_watermark_checkbox.place(x=280, y=285)
    
    # Create a Checkbutton for is_tiktok_full_audio
    is_tiktok_full_audio_var = tk.BooleanVar()
    def is_tiktok_full_audio_toggle():
        global is_tiktok_full_audio
        is_tiktok_full_audio = is_tiktok_full_audio_var.get()
        
    # Create a Checkbutton for is_audio_muted
    audio_muted_var = tk.BooleanVar()
    def on_audio_muted_toggle():
        global is_audio_muted
        is_audio_muted = audio_muted_var.get()

    audio_muted_checkbox = ttk.Checkbutton(window, text="Mute Audio", variable=audio_muted_var, command=on_audio_muted_toggle)
    audio_muted_checkbox.place(x=280, y=315)


    is_tiktok_full_audio_checkbox = ttk.Checkbutton(window, text="Get Original TikTok Audio", variable=is_tiktok_full_audio_var, command=is_tiktok_full_audio_toggle)
    is_tiktok_full_audio_checkbox.place(x=95, y=315)
    
    # Create a Checkbutton for dub_lang
    dub_lang_var = tk.BooleanVar()
    def on_dub_lang_toggle():
        global dub_lang
        dub_lang = dub_lang_var.get()

    dub_lang_checkbox = ttk.Checkbutton(window, text="Dubbed Language", variable=dub_lang_var, command=on_dub_lang_toggle)
    dub_lang_checkbox.place(x=95, y=345)

    # Create a Checkbutton for disableMetadata
    disable_metadata_var = tk.BooleanVar()
    def on_disable_metadata_toggle():
        global disableMetadata
        disableMetadata = disable_metadata_var.get()

    disable_metadata_checkbox = ttk.Checkbutton(window, text="Disable Metadata", variable=disable_metadata_var, command=on_disable_metadata_toggle)
    disable_metadata_checkbox.place(x=280, y=345)

    download_button = ttk.Button(window, text="Download Media", command=download_video)
    download_button.place(x=95, y=380)

    notelabel = ttk.Label(window, text="h264 tops up at 1080p, AV1 supports 8K and HDR but has little player support and VP9 tops up at 4K and wih HDR")
    notelabel.place(x=30, y=415)

    open_window_button = ttk.Button(window, text="Advanced Options", command=open_new_window)
    open_window_button.place(x=420, y=380)


    window.mainloop()

if __name__ == "__main__":
    main()