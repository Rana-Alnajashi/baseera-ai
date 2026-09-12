import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from tavily import TavilyClient
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def tavily_search(query: str, max_results: int = 3) -> str:
    """Search the web for real-time market data, company news, and reports."""
    try:
        response = tavily_client.search(
            query=query, 
            search_depth="advanced", 
            max_results=max_results,
            include_raw_content=True
        )
        
        results_str = ""
        for result in response.get("results", []):
            title = result.get("title") or "No Title"
            url = result.get("url") or "No URL"
            content = result.get("raw_content") or result.get("content") or ""
            results_str += f"Source: {title} ({url})\nContent: {content[:2000]}\n\n"
            
        return results_str if results_str.strip() else "No relevant results found."
    except Exception as e:
        return f"Error executing search: {str(e)}"

@tool
def extract_youtube_transcript(video_id: str) -> str:
    """Extracts the text transcript from a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'ar'])
        formatted_text = TextFormatter().format_transcript(transcript)
        return formatted_text[:3000]
    except Exception as e:
        return f"Error extracting video transcript: {str(e)}"

baseera_tools = [tavily_search, extract_youtube_transcript]