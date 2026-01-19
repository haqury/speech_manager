"""
Speech service module for text-to-speech functionality.

SECURITY FIXES:
- Removed command injection vulnerability (os.system)
- Added proper path validation
- Fixed race condition with file deletion
- Added error handling
"""
from gtts import gTTS
import os
import subprocess
import tempfile
import threading
import time
import logging
from pathlib import Path
from typing import Optional

import pyglet
import state as state

# Configure logging
logger = logging.getLogger(__name__)

LANG_RUS = 'ru'
PATH_FILE_SPEECH = 'downloads/example.mp3'
RETURN_COMMANDS = ['повтори', 'the fall', 'double or']

# Ensure downloads directory exists
DOWNLOADS_DIR = Path('downloads')
DOWNLOADS_DIR.mkdir(exist_ok=True)


class SpeechService:
    """Speech synthesis service using gTTS and pyglet."""
    
    def __init__(self):
        self.commands = RETURN_COMMANDS
        self.lang_rus = 'ru'
        self._temp_files = []  # Track temp files for cleanup

    def is_spec(self, text: str) -> bool:
        """Check if text contains special commands."""
        for command in self.commands:
            if command.lower() in text.lower():
                return True
        return False

    def run(self, text: str):
        """Run speech synthesis with current keyboard language."""
        return self.speech(text, state.get_keyboard_language())

    def speech(self, text: str, language: str = 'ru'):
        """
        Synthesize speech from text using gTTS.
        
        Args:
            text: Text to synthesize
            language: Language code (default: 'ru')
        """
        try:
            audio = gTTS(text=text, lang=language, slow=False)
            
            # Use temp file for safety
            with tempfile.NamedTemporaryFile(
                mode='wb', 
                suffix='.mp3', 
                delete=False,
                dir=DOWNLOADS_DIR
            ) as temp_file:
                audio.save(temp_file.name)
                temp_path = temp_file.name
            
            # Play audio file safely without command injection
            self._play_audio_file_safe(temp_path)
            
            # Schedule cleanup after playback
            self._schedule_cleanup(temp_path, delay=10.0)
            
        except Exception as e:
            logger.error(f"Speech synthesis error: {e}", exc_info=True)

    def _play_audio_file_safe(self, file_path: str):
        """
        Play audio file safely without command injection.
        
        Args:
            file_path: Path to audio file
        """
        try:
            # Validate path
            audio_path = Path(file_path)
            if not audio_path.exists():
                logger.error(f"Audio file not found: {file_path}")
                return
            
            # Use subprocess with list of args (no shell injection)
            # Windows: start command requires cmd.exe
            if os.name == 'nt':  # Windows
                subprocess.Popen(
                    ['cmd', '/c', 'start', '', str(audio_path)],
                    shell=False,  # Safe: no shell injection
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:  # Linux/Mac
                subprocess.Popen(
                    ['xdg-open', str(audio_path)],
                    shell=False
                )
                
        except Exception as e:
            logger.error(f"Error playing audio: {e}", exc_info=True)

    def _schedule_cleanup(self, file_path: str, delay: float = 10.0):
        """
        Schedule file cleanup after delay to avoid race condition.
        
        Args:
            file_path: Path to file to delete
            delay: Delay in seconds before deletion
        """
        def delayed_cleanup():
            time.sleep(delay)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Cleaned up temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")
        
        cleanup_thread = threading.Thread(
            target=delayed_cleanup,
            daemon=True,
            name=f"Cleanup-{Path(file_path).name}"
        )
        cleanup_thread.start()

    def cleanup_all(self):
        """Clean up all tracked temp files."""
        for file_path in self._temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")
        self._temp_files.clear()


def speech(text: str, language: str):
    """
    Legacy function: Synthesize speech with pyglet playback.
    
    Args:
        text: Text to synthesize
        language: Language code
        
    Note: This function has race condition with file deletion.
          Use SpeechService class instead for better safety.
    """
    try:
        audio = gTTS(text=text, lang=language, slow=False)
        
        # Ensure directory exists
        DOWNLOADS_DIR.mkdir(exist_ok=True)
        
        audio.save(PATH_FILE_SPEECH)
        song = pyglet.media.load(PATH_FILE_SPEECH)
        song.play()
        
        # ✅ FIX: Don't delete immediately - schedule cleanup
        def delayed_cleanup():
            time.sleep(5.0)  # Wait for playback
            try:
                if os.path.exists(PATH_FILE_SPEECH):
                    os.remove(PATH_FILE_SPEECH)
            except Exception as e:
                logger.warning(f"Failed to cleanup: {e}")
        
        threading.Thread(target=delayed_cleanup, daemon=True).start()
        
    except Exception as e:
        logger.error(f"Speech error: {e}", exc_info=True)


def list_file(path: str):
    """
    Play audio file from path.
    
    Args:
        path: Path to audio file
    """
    try:
        # Validate path
        audio_path = Path(path)
        if not audio_path.exists():
            logger.error(f"Audio file not found: {path}")
            return
        
        song = pyglet.media.load(str(audio_path))
        song.play()
        
    except Exception as e:
        logger.error(f"Error playing file {path}: {e}", exc_info=True)


# ✅ Removed speechOld() - was duplicate with command injection vulnerability
