import streamlit as st
import speech_recognition as sr
import os
from datetime import datetime
import tempfile

class SpeechRecognitionApp:
    def __init__(self):
        # Initialize recognizer
        self.recognizer = sr.Recognizer()
        # List of supported APIs and languages
        self.recognition_apis = {
            "Google Speech Recognition": self.recognize_with_google,
            "Sphinx (Offline)": self.recognize_with_sphinx
        }
        self.languages = {
            "English (US)": "en-US",
            "Spanish": "es-ES", 
            "French": "fr-FR",
            "German": "de-DE",
            "Chinese (Mandarin)": "zh-CN"
        }
        # Store the last transcription
        self.last_transcription = ""

    def recognize_with_google(self, audio, language):
        try:
            text = self.recognizer.recognize_google(audio, language=language)
            return text
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand the audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"

    def recognize_with_sphinx(self, audio, language):
        try:
            text = self.recognizer.recognize_sphinx(audio)
            return text
        except sr.UnknownValueError:
            return "Sphinx could not understand the audio"
        except sr.RequestError as e:
            return f"Sphinx error: {e}"

    def transcribe_speech(self, api_choice, language_choice, timeout, phrase_time_limit):
        # Configure audio settings
        with sr.Microphone() as source:
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            st.info(f"Speak now in {language_choice}...")

            try:
                # Listen for speech with the provided timeout and phrase time limit
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
                st.info("Processing audio...")
                
                # Select recognition method based on API choice
                recognition_method = self.recognition_apis.get(api_choice, self.recognize_with_google)
                text = recognition_method(audio, self.languages.get(language_choice, "en-US"))
                
                # Store the transcription
                self.last_transcription = text
                
                return text

            except sr.WaitTimeoutError:
                return "No speech detected. Time limit exceeded."
            except Exception as e:
                return f"An unexpected error occurred: {str(e)}"


    def create_download_file(self, text):
        """
        Create a temporary file for download using Streamlit's download functionality
        """
        if not text or text == "No speech detected. Time limit exceeded.":
            st.warning("No valid transcription to save.")
            return None
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', prefix='transcription_') as temp_file:
            temp_file.write(text)
            temp_file_path = temp_file.name
        
        return temp_file_path

def main():
    
    st.title("Advanced Speech Recognition App")
    
    # Initialize the app
    app = SpeechRecognitionApp()
    
    # Create sidebar for configuration
    st.sidebar.header("Speech Recognition Settings")
    
    # API Selection
    api_choice = st.sidebar.selectbox(
        "Choose Speech Recognition API", 
        list(app.recognition_apis.keys())
    )
    
    # Language Selection
    language_choice = st.sidebar.selectbox(
        "Choose Language", 
        list(app.languages.keys())
    )
    
    # Timeout Settings
    timeout = st.sidebar.number_input(
    "Set Timeout (seconds)", 
    min_value=1, 
    max_value=30, 
    value=5,  # Default timeout
    help="Maximum time to wait for speech to start."
    )

    phrase_time_limit = st.sidebar.number_input(
    "Set Phrase Time Limit (seconds)", 
    min_value=1, 
    max_value=60, 
    value=10,  # Default time limit for speech
    help="Maximum duration for each speech input."
    )   
    # Main app interface
    st.write("Configure your settings in the sidebar and click 'Start Recording'")
    
    # Recording button
    if st.button("Start Recording"):
        # Perform speech recognition
        text = app.transcribe_speech(api_choice, language_choice, timeout, phrase_time_limit)
        
        # Display transcription
        st.write("### Transcription:")
        st.write(text)
        
        # Save transcription option
        temp_file_path = app.create_download_file(text)
        
        if temp_file_path:
            with open(temp_file_path, 'r') as file:
                file_contents = file.read()
            
            st.download_button(
                label="Download Transcription",
                data=file_contents,
                file_name=f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            
            # Clean up the temporary file
            os.unlink(temp_file_path)

if __name__ == "__main__":
    main()
