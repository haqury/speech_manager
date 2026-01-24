"""
Audio recording module using SoundDevice instead of PyAudio.
This module provides audio recording functionality compatible with Python 3.13+
"""
import numpy as np
import sounddevice as sd
import speech_recognition as sr
from typing import Optional, Tuple, List, Dict
import threading
import queue
import time


def get_available_microphones() -> List[Dict[str, any]]:
    """
    Получает список доступных микрофонов в системе.
    
    Returns:
        Список словарей с информацией о микрофонах:
        [{'index': 0, 'name': 'Microphone', 'channels': 2}, ...]
    """
    devices = sd.query_devices()
    microphones = []
    
    for idx, device in enumerate(devices):
        # Только устройства с входами (микрофоны)
        if device['max_input_channels'] > 0:
            microphones.append({
                'index': idx,
                'name': device['name'],
                'channels': device['max_input_channels'],
                'sample_rate': int(device['default_samplerate'])
            })
    
    return microphones


def get_default_microphone_index() -> int:
    """
    Получает индекс микрофона по умолчанию.
    
    Returns:
        Индекс микрофона по умолчанию
    """
    try:
        default_device = sd.query_devices(kind='input')
        # Ищем этот device в списке всех устройств
        devices = sd.query_devices()
        for idx, device in enumerate(devices):
            if device['name'] == default_device['name']:
                return idx
        return 0
    except Exception:
        return 0


class AudioRecorder:
    """
    Audio recorder using SoundDevice for better Python 3.13+ compatibility.
    
    This replaces PyAudio-based sr.Microphone() with a SoundDevice implementation.
    """
    
    def __init__(
        self, 
        sample_rate: int = 16000,
        channels: int = 1,
        dtype: str = 'int16',
        device: Optional[int] = None,
        energy_threshold: int = 300,
        pause_threshold: float = 0.8,
        on_speech_start: Optional[callable] = None,
        on_speech_end: Optional[callable] = None,
        on_volume_update: Optional[callable] = None
    ):
        """
        Initialize audio recorder.
        
        Args:
            sample_rate: Sample rate in Hz (default 16000)
            channels: Number of audio channels (default 1 for mono)
            dtype: Data type for audio samples
            device: Device index (None for default)
            energy_threshold: Minimum audio energy to consider as speech
            pause_threshold: Seconds of silence to mark end of phrase
            on_speech_start: Callback function when speech detected
            on_speech_end: Callback function when speech ends
            on_volume_update: Callback function for volume updates (called with energy value)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.device = device
        self.energy_threshold = energy_threshold
        self.pause_threshold = pause_threshold
        self.on_speech_start = on_speech_start
        self.on_speech_end = on_speech_end
        self.on_volume_update = on_volume_update
        
        # Recording state
        self.is_recording = False
        self.should_stop = False  # Флаг для остановки записи по горячей клавише
        self.audio_queue = queue.Queue()
        
    def get_energy(self, audio_data: np.ndarray) -> float:
        """
        Calculate the energy (RMS) of audio data.
        
        Args:
            audio_data: Audio samples as numpy array
            
        Returns:
            RMS energy value
        """
        return np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
    
    def record_audio(
        self, 
        duration: Optional[float] = None,
        phrase_time_limit: Optional[float] = None
    ) -> sr.AudioData:
        """
        Record audio from microphone.
        
        Args:
            duration: Fixed duration in seconds (None for auto-detection)
            phrase_time_limit: Maximum phrase duration in seconds
            
        Returns:
            speech_recognition.AudioData object
        """
        if duration is not None:
            # Fixed duration recording
            return self._record_fixed_duration(duration)
        else:
            # Voice activity detection recording
            return self._record_with_vad(phrase_time_limit)
    
    def _record_fixed_duration(self, duration: float) -> sr.AudioData:
        """Record audio for a fixed duration."""
        print(f"Recording for {duration} seconds...")
        
        audio_data = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype,
            device=self.device
        )
        sd.wait()  # Wait for recording to complete
        
        # Convert to bytes for speech_recognition
        audio_bytes = audio_data.tobytes()
        
        return sr.AudioData(
            audio_bytes,
            self.sample_rate,
            2  # sample_width for int16
        )
    
    def _record_with_vad(self, phrase_time_limit: Optional[float] = None) -> sr.AudioData:
        """
        Record audio with Voice Activity Detection.
        
        Automatically detects speech start/end based on energy threshold.
        """
        recorded_frames = []
        silent_chunks = 0
        started_speaking = False
        max_chunks = None
        
        if phrase_time_limit:
            # Calculate max chunks based on time limit
            chunk_duration = 0.1  # 100ms chunks
            max_chunks = int(phrase_time_limit / chunk_duration)
        
        chunk_size = int(self.sample_rate * 0.1)  # 100ms chunks
        
        print("Listening... (speak now)")
        
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                device=self.device,
                blocksize=chunk_size
            ) as stream:
                
                chunk_count = 0
                self.is_recording = True
                self.should_stop = False
                
                while True:
                    # Проверяем флаг остановки
                    if self.should_stop:
                        print("Recording stopped by hotkey")
                        # Если речь уже началась, вызываем callback окончания
                        if started_speaking and self.on_speech_end:
                            try:
                                self.on_speech_end()
                            except Exception as e:
                                print(f"Error in on_speech_end callback: {e}")
                        self.is_recording = False
                        break
                    
                    # Read audio chunk
                    audio_chunk, overflowed = stream.read(chunk_size)
                    
                    if overflowed:
                        print("Warning: Audio buffer overflow")
                    
                    # Calculate energy
                    energy = self.get_energy(audio_chunk)
                    
                    # Update volume visualizer
                    if self.on_volume_update:
                        try:
                            # Normalize energy to 0-100 range for visualization
                            normalized_volume = min(100, int((energy / self.energy_threshold) * 50))
                            self.on_volume_update(normalized_volume)
                        except Exception as e:
                            pass  # Ignore visualization errors
                    
                    # Check if speech detected
                    if energy > self.energy_threshold:
                        if not started_speaking:
                            print("Speech detected!")
                            started_speaking = True
                            # Вызываем callback при начале речи
                            if self.on_speech_start:
                                try:
                                    self.on_speech_start()
                                except Exception as e:
                                    print(f"Error in on_speech_start callback: {e}")
                        
                        recorded_frames.append(audio_chunk)
                        silent_chunks = 0
                    elif started_speaking:
                        # Silence after speech started
                        recorded_frames.append(audio_chunk)
                        silent_chunks += 1
                        
                        # Check if pause threshold reached
                        silence_duration = silent_chunks * 0.1
                        if silence_duration >= self.pause_threshold:
                            print("End of phrase detected")
                            # Вызываем callback при окончании речи
                            if self.on_speech_end:
                                try:
                                    self.on_speech_end()
                                except Exception as e:
                                    print(f"Error in on_speech_end callback: {e}")
                            break
                    
                    chunk_count += 1
                    
                    # Check phrase time limit
                    if max_chunks and chunk_count >= max_chunks:
                        print("Phrase time limit reached")
                        break
                    
                    # Safety timeout (30 seconds)
                    if chunk_count > 300:
                        print("Recording timeout")
                        break
        
        except Exception as e:
            print(f"Recording error: {e}")
            raise
        finally:
            self.is_recording = False
        
        if not recorded_frames:
            # Return empty audio if nothing recorded
            empty_audio = np.zeros((int(0.1 * self.sample_rate), self.channels), dtype=self.dtype)
            return sr.AudioData(
                empty_audio.tobytes(),
                self.sample_rate,
                2
            )
        
        # Concatenate all frames
        audio_data = np.concatenate(recorded_frames, axis=0)
        
        # Convert to bytes
        audio_bytes = audio_data.tobytes()
        
        print(f"Recorded {len(audio_data) / self.sample_rate:.2f} seconds")
        
        return sr.AudioData(
            audio_bytes,
            self.sample_rate,
            2  # sample_width for int16
        )
    
    @staticmethod
    def list_devices():
        """List available audio input devices."""
        print("\nAvailable audio devices:")
        print(sd.query_devices())
    
    def test_recording(self, duration: float = 3.0):
        """
        Test recording functionality.
        
        Args:
            duration: Test duration in seconds
        """
        print(f"Testing recording for {duration} seconds...")
        try:
            audio = self.record_audio(duration=duration)
            print(f"✅ Recording successful! Size: {len(audio.frame_data)} bytes")
            return True
        except Exception as e:
            print(f"❌ Recording failed: {e}")
            return False


# Context manager support for compatibility with sr.Microphone() style
class MicrophoneStream:
    """
    Context manager wrapper for AudioRecorder to mimic sr.Microphone() interface.
    
    Usage:
        with MicrophoneStream() as source:
            audio = source.listen(phrase_time_limit=5)
    """
    
    def __init__(self, **kwargs):
        self.recorder = AudioRecorder(**kwargs)
    
    def stop_recording(self):
        """Останавливает текущую запись."""
        if self.recorder:
            self.recorder.should_stop = True
    
    def is_recording(self) -> bool:
        """Проверяет, идет ли сейчас запись."""
        return self.recorder.is_recording if self.recorder else False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def listen(
        self, 
        timeout: Optional[float] = None,
        phrase_time_limit: Optional[float] = None
    ) -> sr.AudioData:
        """
        Record audio (mimics sr.Recognizer.listen() interface).
        
        Args:
            timeout: Not used (for compatibility)
            phrase_time_limit: Maximum phrase duration
            
        Returns:
            AudioData object
        """
        return self.recorder.record_audio(phrase_time_limit=phrase_time_limit)


if __name__ == "__main__":
    # Test the recorder
    print("Audio Recorder Test")
    print("=" * 50)
    
    # List devices
    AudioRecorder.list_devices()
    
    # Test recording
    recorder = AudioRecorder()
    print("\nTest 1: Fixed duration recording (3 seconds)")
    recorder.test_recording(duration=3.0)
    
    print("\nTest 2: Voice activity detection")
    print("Speak something...")
    try:
        audio = recorder.record_audio(phrase_time_limit=10)
        print(f"✅ VAD recording successful! Size: {len(audio.frame_data)} bytes")
    except Exception as e:
        print(f"❌ VAD recording failed: {e}")
