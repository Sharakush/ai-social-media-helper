# --------------------------------------------------------------
# Step 0: Import necessary libraries and modules
# --------------------------------------------------------------
import asyncio
import os
from youtube_transcript_api import YouTubeTranscriptApi
from agents import Agent, Runner, WebSearchTool, function_tool, ItemHelpers, trace
from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List

# --------------------------------------------------------------
# Step 1: Load environment variables
# --------------------------------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --------------------------------------------------------------
# Step 2: Define the tool that generates social media posts
# --------------------------------------------------------------
@function_tool
def create_social_post(transcript: str, platform: str):
    print(f"Creating content for: {platform}")

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.responses.create(
        model="gpt-4o",
        input=[
            {"role": "user", "content": f"Here is the transcript:\n{transcript}\n\n"
                                         f"Please write a post for {platform} using the transcript above."}
        ],
        max_output_tokens=2500
    )

    return response.output_text

# --------------------------------------------------------------
# Step 3: Define the agent that manages content creation
# --------------------------------------------------------------
@dataclass
class Post:
    platform: str
    content: str

content_creator = Agent(
    name="Content Creator Agent",
    instructions="""
        You are a creative social media strategist.
        Based on a given video transcript and platform, you generate catchy and relevant posts.
        Utilize web search when necessary to enrich the content.
    """,
    model="gpt-4o-mini",
    tools=[create_social_post, WebSearchTool()],
    output_type=List[Post],
)

# --------------------------------------------------------------
# Step 4: Function to fetch YouTube video transcript
# --------------------------------------------------------------
def fetch_transcript(video_id: str, preferred_langs: list = None) -> str:
    if preferred_langs is None:
        preferred_langs = ["en"]

    try:
        transcript_data = YouTubeTranscriptApi().fetch(video_id, languages=preferred_langs)
        return " ".join(snippet.text for snippet in transcript_data)

    except Exception as e:
        from youtube_transcript_api._errors import (
            CouldNotRetrieveTranscript, VideoUnavailable,
            InvalidVideoId, NoTranscriptFound, TranscriptsDisabled
        )

        if isinstance(e, NoTranscriptFound):
            err = f"No transcript available for video {video_id} in languages: {preferred_langs}"
        elif isinstance(e, VideoUnavailable):
            err = f"The video {video_id} is not accessible."
        elif isinstance(e, InvalidVideoId):
            err = f"The provided video ID '{video_id}' is invalid."
        elif isinstance(e, TranscriptsDisabled):
            err = f"Transcripts are disabled for video {video_id}."
        elif isinstance(e, CouldNotRetrieveTranscript):
            err = f"Unable to get transcript: {str(e)}"
        else:
            err = f"Unknown error: {str(e)}"

        print("Transcript Error:", err)
        raise Exception(err) from e

# --------------------------------------------------------------
# Step 5: Async function to execute the workflow
# --------------------------------------------------------------
async def main():
    video_id = "OZ5OZZZ2cvk"
    transcript = fetch_transcript(video_id)

    message = f"Create LinkedIn and Instagram posts from this transcript: {transcript}"
    
    task_input = [{"content": message, "role": "user"}]

    with trace("Generating social media content"):
        result = await Runner.run(content_creator, task_input)
        final_output = ItemHelpers.text_message_outputs(result.new_items)
        print("Final Generated Output:\n", final_output)

if __name__ == "__main__":
    asyncio.run(main())









