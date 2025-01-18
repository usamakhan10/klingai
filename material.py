import requests
import os
import time
from tqdm import tqdm

start_url = "https://www.klingai.com/api/works"
params = {
    "contentType": "",
    "pageNum": {},
    "pageSize": {},
    "sortType": "recommend",
    "match": "",
    "isCommunity": "true",
}
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en",
    "priority": "u=1, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "Referer": "https://www.klingai.com/community/material",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}




def get_videos(page_num=1, page_size=20):
    videos_url = []
    # Make the GET request
    params["pageNum"] = page_num
    params["pageSize"] = page_size
    response = requests.get(start_url, headers=headers, params=params)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Extract the videos from the response
        videos = data["data"]
        for video_num, video in enumerate(videos):
            url = video["resource"]["resource"]
            videos_url.append(url)
        # Return the videos
        return videos_url
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        return []


def download_video(url, title):
    # Clean the title to make it a valid filename
    valid_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip()
    if len(valid_title) > 100:
        valid_title = valid_title[:100] + "..."
    filename = f"{valid_title}.mp4"

    os.makedirs("videos", exist_ok=True)
    try:
        print(f"Downloading video: {valid_title}")
        # Send a GET request to the video URL
        response = requests.get(url, stream=True)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Get the total file size from headers
            total_size = int(response.headers.get("content-length", 0))
            chunk_size = 1024

            # Save the video file with tqdm progress bar
            with open(f"videos/{filename}", "wb") as video_file, tqdm(
                desc=f"Downloading {valid_title}",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        video_file.write(chunk)
                        progress_bar.update(len(chunk))
        else:
            print(f"Failed to download video. HTTP Status Code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    new_videos = [1]
    videos = set()
    page_num = 1
    while len(new_videos) > 0:
        new_videos = get_videos(page_size=20, page_num=page_num)
        videos = videos.union(set(new_videos))
        time.sleep(0.1)
        page_num += 1
    print(f"Found {len(videos)} videos")
    for vid_num,video in enumerate(videos,start=1):
        download_video(video, f"video_{vid_num}")   
        print(f"Downloaded {vid_num}/{len(videos)} videos")
    print(f"Downloaded {len(videos)} videos")
    
if __name__ == "__main__":
    main()