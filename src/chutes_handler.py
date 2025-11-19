import aiohttp
import base64
import logging
import json
import os

logger = logging.getLogger(__name__)

async def transcribe_with_chutes(audio_path, api_token, model="chutes-whisper-large-v3", language=None):
    """
    Transcribe audio using Chutes API.
    
    Args:
        audio_path (str): Path to the audio file.
        api_token (str): Chutes API token.
        model (str): Model name (default: chutes-whisper-large-v3).
        language (str): Language code (optional).

    Returns:
        dict: Transcription result (e.g., {'text': '...', 'segments': [...]}) or None if failed.
    """
    url = f"https://{model}.chutes.ai/transcribe"
    
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return None

    try:
        with open(audio_path, "rb") as audio_file:
            audio_content = audio_file.read()
            audio_b64 = base64.b64encode(audio_content).decode('utf-8')

        # If language is 'auto', send None (null in JSON) to let the model detect it
        if language == "auto":
            language = None

        payload = {
            "language": language,
            "audio_b64": audio_b64
        }

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

        logger.info(f"Sending request to Chutes API: {url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("Chutes API transcription successful.")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Chutes API failed with status {response.status}: {error_text}")
                    return None

    except Exception as e:
        logger.error(f"Error during Chutes API transcription: {e}")
        return None

def format_timestamp(seconds, separator=','):
    """
    Format seconds to HH:MM:SS,mmm (SRT) or HH:MM:SS.mmm (VTT)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02}{separator}{millis:03}"

def save_chutes_outputs(result, output_dir, base_filename):
    """
    Save Chutes API result to .txt, .srt, and .vtt files.
    """
    created_files = {}
    
    # Save TXT
    text = result.get('text', '')
    if text:
        txt_path = os.path.join(output_dir, f"{base_filename}.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        created_files['txt'] = txt_path

    segments = result.get('segments', [])
    if segments:
        # Save SRT
        srt_path = os.path.join(output_dir, f"{base_filename}.srt")
        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, start=1):
                start = format_timestamp(segment['start'], ',')
                end = format_timestamp(segment['end'], ',')
                text = segment['text'].strip()
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
        created_files['srt'] = srt_path

        # Save VTT
        vtt_path = os.path.join(output_dir, f"{base_filename}.vtt")
        with open(vtt_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for segment in segments:
                start = format_timestamp(segment['start'], '.')
                end = format_timestamp(segment['end'], '.')
                text = segment['text'].strip()
                f.write(f"{start} --> {end}\n{text}\n\n")
        created_files['vtt'] = vtt_path

    return created_files

