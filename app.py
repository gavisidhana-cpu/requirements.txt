import streamlit as st
from google import genai
import edge_tts
import asyncio
import os
from moviepy.editor import ColorClip, AudioFileClip, TextClip, CompositeVideoClip

st.set_page_config(page_title="Desi Reel AI", page_icon="🎬")
st.title("🎬 Desi Reel AI - Hindi & Punjabi Reel Maker")

# API Key लेना
api_key = st.secrets.get("GEMINI_API_KEY") or st.text_input("अपनी Gemini API Key डालें:", type="password")

# यूज़र इनपुट
topic = st.text_input("रील का टॉपिक लिखें (जैसे: सफलता के 3 नियम, या पंजाबी मोटिवेशन):")
language = st.selectbox("भाषा चुनें (Language):", ["Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)"])

# आवाज़ (Voice) सेटअप
voice_map = {
    "Hindi (हिंदी)": "hi-IN-MadhurNeural",
    "Punjabi (ਪੰਜਾਬੀ)": "pa-IN-OjasNeural"
}

async def generate_audio(text, voice, filename):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

if st.button("🚀 रील बनाएं (Generate Reel)"):
    if not api_key or not topic:
        st.error("कृपया API Key और टॉपिक दोनों डालें!")
    else:
        try:
            with st.spinner("1/3: AI स्क्रिप्ट लिख रहा है..."):
                client = genai.Client(api_key=api_key)
                lang_name = "Hindi" if "Hindi" in language else "Punjabi"
                prompt = f"Write a short, engaging 30-second Instagram Reel voiceover script in {lang_name} about: '{topic}'. Output ONLY the spoken text without any headings, emojis, or stage directions."
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                script = response.text.strip()
                st.subheader("📝 तैयार स्क्रिप्ट:")
                st.write(script)

            with st.spinner("2/3: AI वॉइसओवर तैयार हो रहा है..."):
                audio_file = "voiceover.mp3"
                asyncio.run(generate_audio(script, voice_map[language], audio_file))
                st.audio(audio_file)

            with st.spinner("3/3: वीडियो रील रेंडर हो रही है..."):
                audio_clip = AudioFileClip(audio_file)
                duration = audio_clip.duration
                
                # 9:16 वर्टिकल रील बैकग्राउंड (1080x1920)
                bg_clip = ColorClip(size=(720, 1280), color=(20, 24, 38), duration=duration)
                video = bg_clip.set_audio(audio_clip)
                
                output_file = "desi_reel.mp4"
                video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")
                
                st.success("🎉 आपकी रील तैयार है!")
                st.video(output_file)
                
                with open(output_file, "rb") as f:
                    st.download_button("⬇️ रील डाउनलोड करें (MP4)", f, file_name="desi_reel.mp4")

        except Exception as e:
            st.error(f"कोई समस्या आई: {e}")
