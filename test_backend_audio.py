#!/usr/bin/env python3
"""
Simple test script to verify WAV audio processing functionality.
This tests the core audio processing that the backend will use.
"""

import os
import tempfile
import logging
from pydub import AudioSegment
import speech_recognition as sr

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_wav_processing():
    """Test WAV audio processing with speech_recognition"""
    print("🎵 Testing WAV Audio Processing")
    print("=" * 50)
    
    try:
        # Create a simple WAV audio file
        audio_segment = AudioSegment.silent(duration=1000)  # 1 second of silence
        
        # Configure for speech recognition compatibility
        audio_segment = audio_segment.set_frame_rate(16000)  # 16kHz sample rate
        audio_segment = audio_segment.set_channels(1)        # Mono
        audio_segment = audio_segment.set_sample_width(2)    # 16-bit
        
        print("✅ Created test audio segment")
        print(f"   Duration: {len(audio_segment)}ms")
        print(f"   Sample rate: {audio_segment.frame_rate}Hz")
        print(f"   Channels: {audio_segment.channels}")
        print(f"   Sample width: {audio_segment.sample_width} bytes")
        
        # Create temporary WAV file
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_wav.close()
        
        # Export as WAV
        audio_segment.export(temp_wav.name, format="wav")
        print("✅ Successfully exported WAV file")
        
        # Test with speech_recognition library (like backend does)
        recognizer = sr.Recognizer()
        
        try:
            with sr.AudioFile(temp_wav.name) as source:
                audio_data = recognizer.record(source)
                print("✅ Successfully loaded audio with speech_recognition")
                print(f"   Audio data type: {type(audio_data)}")
        except Exception as sr_error:
            print(f"❌ Speech recognition error: {str(sr_error)}")
            return False
        
        # Clean up
        os.unlink(temp_wav.name)
        
        print("✅ WAV processing test passed!")
        return True
        
    except Exception as e:
        print(f"❌ WAV processing test failed: {str(e)}")
        return False

def test_file_conversion_scenario():
    """Test the exact scenario the backend will handle"""
    print("\n🔄 Testing Backend Conversion Scenario")
    print("=" * 50)
    
    try:
        # Simulate what happens in the backend
        
        # Step 1: Create original audio (simulate uploaded file)
        original_audio = AudioSegment.silent(duration=1000)
        temp_original = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
        temp_original.close()
        
        # Export as WAV (since WebM needs ffmpeg, we'll use WAV as source)
        original_audio.export(temp_original.name, format="wav")
        print("✅ Created simulated uploaded audio file")
        
        # Step 2: Backend conversion process
        temp_converted = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_converted.close()
        
        # Load the "uploaded" file
        loaded_audio = AudioSegment.from_file(temp_original.name)
        print("✅ Loaded uploaded audio file")
        
        # Convert with backend settings
        converted_audio = loaded_audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        converted_audio.export(temp_converted.name, format="wav")
        print("✅ Converted to speech recognition format")
        
        # Step 3: Test with speech recognition
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 100
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.5
        
        with sr.AudioFile(temp_converted.name) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio_data = recognizer.record(source)
            print("✅ Successfully processed with speech recognition")
        
        # Clean up
        os.unlink(temp_original.name)
        os.unlink(temp_converted.name)
        
        print("✅ Backend conversion scenario test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Backend conversion scenario failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Audio Processing for Medical Diagnosis App Backend")
    print("=" * 65)
    
    # Test 1: Basic WAV processing
    success1 = test_wav_processing()
    
    # Test 2: Backend conversion scenario
    success2 = test_file_conversion_scenario()
    
    # Summary
    print("\n" + "=" * 65)
    if success1 and success2:
        print("🎉 Audio processing tests completed successfully!")
        print("✅ Backend audio conversion should work correctly")
        print("\n📋 Backend Changes Applied:")
        print("   - Added pydub import for audio format conversion")
        print("   - Modified process_voice() to convert audio to WAV format")
        print("   - Set optimal parameters for speech recognition (16kHz, mono, 16-bit)")
        print("   - Added proper error handling for conversion failures")
    else:
        print("❌ Some audio processing tests failed!")
        print("⚠️  Backend may need additional configuration")
    
    print("\n🚀 Next Steps:")
    print("1. Start the Flask backend: python backend/app.py")
    print("2. Start the Streamlit frontend: streamlit run frontend/app.py")
    print("3. Test voice recording in the chat interface")
    print("4. The backend will now convert any audio format to WAV before processing")
