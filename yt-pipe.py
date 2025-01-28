import os
import subprocess
import requests
import json

def install_latest_nightly():
    """Install the latest nightly build of yt-dlp using pip."""
    command = ["pip", "install", "-U", "--pre", "yt-dlp[default]"]
    subprocess.run(command, check=True)
    print("yt-dlp nightly build installed successfully.")

def download_youtube_video(url, output_path):
    """Download a YouTube video using yt-dlp and save it locally."""
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "video.webm")
    command = [
        "yt-dlp",
        "-f", "bestvideo+bestaudio",
        "--merge-output-format", "webm",
        "-o", output_file,
        url
    ]
    subprocess.run(command, check=True)
    return output_file

def send_to_gemini_api(video_path, api_url):
    """Send the video to the GEMINI API and get event timestamps."""
    with open(video_path, 'rb') as video_file:
        response = requests.post(api_url, files={'file': video_file})
        response.raise_for_status()
        return response.json()  # Assuming the API returns JSON with timestamps

def process_video_with_ffmpeg(video_path, timestamps, output_dir):
    """Cut the video into snippets based on timestamps and slow down to 1 FPS using FFmpeg."""
    os.makedirs(output_dir, exist_ok=True)

    for i, event in enumerate(timestamps):
        start = event['start']
        end = event['end']
        output_file = os.path.join(output_dir, f"snippet_{i+1}.webm")

        # Extract snippet and slow down to 1 FPS
        command = [
            "ffmpeg",
            "-i", video_path,
            "-ss", str(start),
            "-to", str(end),
            "-vf", "fps=1",
            "-c:v", "libvpx",
            "-pix_fmt", "yuv420p",
            output_file
        ]

        subprocess.run(command, check=True)

if __name__ == "__main__":
    # Ensure yt-dlp is up-to-date
    install_latest_nightly()

    # Input values
    youtube_url = input("Enter the YouTube URL: ")
    output_directory = "output"
    gemini_api_url = "https://gemini-api.example.com/extract"  # Replace with actual API URL

    try:
        # Step 1: Download YouTube video
        print("Downloading video...")
        video_path = download_youtube_video(youtube_url, output_directory)
        print(f"Video downloaded to {video_path}")

        # Step 2: Send video to GEMINI API
        print("Sending video to GEMINI API...")
        timestamps = send_to_gemini_api(video_path, gemini_api_url)
        print("Timestamps received:", timestamps)

        # Step 3: Process video
        print("Processing video snippets...")
        process_video_with_ffmpeg(video_path, timestamps, output_directory)
        print(f"Video snippets saved to {output_directory}")

    except Exception as e:
        print(f"An error occurred: {e}")
