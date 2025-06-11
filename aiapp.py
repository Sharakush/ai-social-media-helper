import streamlit as st
import asyncio
from social_media_agent import content_writer_agent, get_transcript, Runner, ItemHelpers
import json

# Set up the Streamlit page
st.set_page_config(
    page_title="Social Media Content Generator",
    page_icon="\ud83d\udcf1",
    layout="wide"
)

# Display the title and info about the app
st.title("📱 Social Media Content Generator")
st.markdown("""
This tool helps create social media content from YouTube video transcripts.
Just enter the video ID and your prompt to generate posts for selected platforms.
""")

# Section to collect user input
st.header("Input Section")
col1, col2 = st.columns(2)

with col1:
    video_id = st.text_input("YouTube Video ID", placeholder="e.g., OZ5OZZZ2cvk")
    st.caption("Enter the part after 'v=' in the YouTube link. For example, in 'https://www.youtube.com/watch?v=OZ5OZZZ2cvk', ID is 'OZ5OZZZ2cvk'.")

with col2:
    user_query = st.text_area(
        "Your Instruction",
        placeholder="e.g., Write a LinkedIn post and Instagram caption using this video",
        height=100
    )

# Let user pick platforms
st.subheader("Choose Social Platforms")
p1, p2, p3 = st.columns(3)
with p1:
    linkedin = st.checkbox("LinkedIn", value=True)
with p2:
    instagram = st.checkbox("Instagram", value=True)
with p3:
    twitter = st.checkbox("Twitter")

# Async function to process the content
async def generate_content(video_id, user_query, platforms):
    try:
        transcript_text = get_transcript(video_id)

        selected = " and ".join(platforms)

        # Prepare the final prompt
        final_prompt = f"Generate {selected} posts based on this video transcript: {transcript_text}"
        if user_query:
            final_prompt = f"{user_query} for {selected} based on this video transcript: {transcript_text}"

        inputs = [{"content": final_prompt, "role": "user"}]
        result = await Runner.run(content_writer_agent, inputs)
        return result, None
    except Exception as err:
        return None, str(err)

# When user clicks generate
if st.button("Generate Content", type="primary", disabled=not video_id):
    if not video_id:
        st.error("Please provide a YouTube video ID")
    else:
        chosen_platforms = []
        if linkedin:
            chosen_platforms.append("LinkedIn")
        if instagram:
            chosen_platforms.append("Instagram")
        if twitter:
            chosen_platforms.append("Twitter")

        if not chosen_platforms:
            st.error("Choose at least one social media platform")
        else:
            with st.spinner("Working on content... Please wait."):
                result, error = asyncio.run(generate_content(video_id, user_query, chosen_platforms))

                if error:
                    st.error(f"Something went wrong: {error}")
                else:
                    st.header("Generated Social Media Posts")
                    output = ItemHelpers.text_message_outputs(result.new_items)
                    posts = json.loads(output).get("response", [])

                    for post in posts:
                        platform = post.get("platform", "Unknown")
                        content = post.get("content", "")

                        with st.expander(f"{platform} Post", expanded=True):
                            st.markdown(f"**Platform:** {platform}")
                            st.text_area(f"{platform} Text", content, height=200)
                            st.download_button(
                                label=f"Download {platform} Content",
                                data=content,
                                file_name=f"{platform.lower()}_post.txt",
                                mime="text/plain"
                            )

# Footer info
st.markdown("---")
st.caption("Created with OpenAI + Streamlit for automated content generation")


