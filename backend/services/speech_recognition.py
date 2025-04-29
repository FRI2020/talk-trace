import speech_recognition as sr
from io import BytesIO
import os,sys
from pydub import AudioSegment
from dashscope.audio.asr import Recognition

def convert_ogg_to_wav(orig_song):
    # Replace the .ogg extension with .wav for the destination file
    dest_song = orig_song.replace('.ogg', '.wav')
    
    # Load the OGG file and export it as WAV
    song = AudioSegment.from_ogg(orig_song)
    song.export(dest_song, format="wav")
    
    return dest_song  



def transcribe_audio_ar(audio_data):
    """
    Transcribe audio from raw bytes using DashScope's Speech Recognition API.
    
    Args:
        audio_data (bytes): Raw audio data in OGG format.
    
    Returns:
        str: Transcribed text in Arabic.
    """
    try:
        # Debugging: Check the type of audio_data
        print(f"Type of audio_data: {type(audio_data)}")

        # Ensure audio_data is bytes
        if isinstance(audio_data, str):
            raise ValueError("Input must be raw bytes, not a string.")

        # Convert OGG to WAV using pydub
        ogg_audio = AudioSegment.from_file(BytesIO(audio_data), format="ogg")
        wav_audio = BytesIO()
        ogg_audio.export(wav_audio, format="wav")
        wav_audio.seek(0)  # Rewind the buffer to the beginning

        # Debugging: Check the type of wav_audio.getvalue()
        print(f"Type of wav_audio.getvalue(): {type(wav_audio.getvalue())}")

        # Initialize the DashScope Recognition API
        recognizer = Recognition(
            callback=None,          # No callback function for now
            format="wav",           # Audio format (WAV)
            sample_rate=16000,      # Sample rate of the audio
            model="paraformer-v2-realtime"
        )
        file = '/app/'
        # Perform speech-to-text transcription with DashScope
        response = recognizer.call(
            file=wav_audio.getvalue(),  # Pass the raw bytes of the WAV file
            language="ar"              # Specify Arabic language
        )

        # Debugging: Check the response
        print(f"Response status code: {response.status_code}")
        print(f"Response message: {response.message}")

        # Check if the request was successful
        if response.status_code == 200:
            transcription = response.output["text"]
            return transcription
        else:
            raise ValueError(f"Error in transcription: {response.message}")

    except Exception as e:
        raise ValueError(f"Error processing audio: {e}")

def transcribe_audio(audio_data):
    """Transcribe audio from raw bytes using Google Speech Recognition."""
    recognizer = sr.Recognizer()

    try:
        # Convert OGG to WAV using pydub
        ogg_audio = AudioSegment.from_file(BytesIO(audio_data), format="ogg")
        wav_audio = BytesIO()
        ogg_audio.export(wav_audio, format="wav")
        wav_audio.seek(0)  # Rewind the buffer to the beginning

        # Transcribe the WAV audio
        with sr.AudioFile(wav_audio) as source:
            audio = recognizer.record(source)
        
        text = recognizer.recognize_google(audio)
        return text

    except sr.UnknownValueError:
        raise ValueError("Speech recognition could not understand the audio.")
    except sr.RequestError as e:
        raise ValueError(f"Speech recognition request failed: {e}")
    except Exception as e:
        raise ValueError(f"Error processing audio: {e}")


def transcribe_audio_save(audio_path):
    """Transcribe audio from an OGG file using Google Speech Recognition."""
    recognizer = sr.Recognizer()

    try:
        # Open the audio file
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)  # Read the entire file
        
        # Perform speech recognition
        text = recognizer.recognize_google(audio_data)  
        return text

    except sr.UnknownValueError:
        raise ValueError("Speech recognition could not understand the audio.")
    except sr.RequestError as e:
        raise ValueError(f"Speech recognition request failed: {e}")