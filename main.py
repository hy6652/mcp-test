import os, requests

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

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

    print(f"{API_URL=}")
    print(f"{API_KEY=}")
    # 1. Search > get video ids
    search_url = f"{API_URL}search?part=snippet&q={requests.utils.quote(query)}&type=video&maxResults=5&key={API_KEY}"

    search_response = requests.get(search_url)
    search_response.raise_for_status()
    print(search_response.raise_for_status())
    search_data = search_response.json()

    print(search_data)
    video_ids = [item['id']['videoId'] for item in search_data.get('items', [])]

    if not video_ids:
        print("No video ids")
        return []
   
    # 2. video ids > get video details
    video_details_url = f"{API_URL}videos?part=snippet,statistics&id={','.join(video_ids)}&key={API_KEY}"

    video_response = requests.get(video_details_url)
    video_response.raise_for_status()
    print(video_response.json())

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
            "url": f"https://www.youtube.com/watch?v={item.get('id', '')}",
        }
        videos.append(video_card)

    if not videos:
        print("No video details")
        return []

    return videos

def main():
    print("Hello, MCP Server")
    mcp.run()
    # get_search_result("c# mcp")

if __name__ == "__main__":
    main()
