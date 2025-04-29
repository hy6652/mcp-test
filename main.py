import os, requests, logging

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

load_dotenv()
API_URL = os.getenv("YOUTUBE_API_URL")
API_KEY = os.getenv("YOUTUBE_API_KEY")

mcp = FastMCP("youtube_search_agent")

@mcp.tool()
def get_search_result(query: str) -> list:
    """
    Search the vedios from youtube with the user's question.

    Args:
        query (str): The query to search for.

    Returns:
        list: A list of dictionaries containing video details.
    """

    logging.info(f"Received query: {query}")

    # 1. Search > get video ids
    search_url = f"{API_URL}search?part=snippet&q={requests.utils.quote(query)}&type=video&maxResults=5&key={API_KEY}"

    search_response = requests.get(search_url)
    search_response.raise_for_status()
    search_data = search_response.json()

    video_ids = [item['id']['videoId'] for item in search_data.get('items', [])]

    if not video_ids:
        print("No video ids")
        return []
   
    # 2. video ids > get video details
    video_details_url = f"{API_URL}videos?part=snippet,statistics&id={','.join(video_ids)}&key={API_KEY}"

    video_response = requests.get(video_details_url)
    video_response.raise_for_status()

    details_data = video_response.json()

    videos = []
    for item in details_data.get('items', []):
        snippet = item.get('snippet', {})
        statistics = item.get('statistics', {})
        thumbnails = snippet.get('thumbnails', {})
        high_thumbnail = thumbnails.get('high', {}) 
        view_count = statistics.get('viewCount')
        like_count = statistics.get('likeCount')

        video_card = {
            "title": snippet.get('title', 'N/A'),
            "publishedDate": snippet.get('publishedAt', ''),
            "channelName": snippet.get('channelTitle', 'N/A'),
            "channelId": snippet.get('channelId', ''),
            "thumbnailUrl": high_thumbnail.get('url', ''),
            "viewCount": int(view_count) if view_count is not None else None,
            "likeCount": int(like_count) if like_count is not None else None,
            "url": f"https://www.youtube.com/watch?v={safe_text(item.get('id', ''))}",
        }
        videos.append(video_card)

    if not videos:
        print("No video details")
        return []

    return videos

def safe_text(text):
    if text is None:
        return ''
    return str(text).encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
    # get_search_result("c# mcp")

if __name__ == "__main__":
    mcp.run()
