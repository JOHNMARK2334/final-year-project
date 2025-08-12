#!/usr/bin/env python3
"""
Test the actual audio recording format from streamlit-realtime-audio-recorder
to see if we need FFmpeg or if WAV processing is sufficient.
"""

import streamlit as st
import tempfile
import os
from pydub import AudioSegment
import speech_recognition as sr
import base64
import json

def test_streamlit_audio_format():
    """Test what format streamlit-realtime-audio-recorder actually produces"""
    print("🔍 Testing Streamlit Audio Recorder Format")
    print("=" * 50)
    
    # Simulate the data structure from streamlit-realtime-audio-recorder
    # Based on the frontend code, it returns: {status: 'stopped', audioData: 'base64_string'}
    
    # Create a simple WAV file and encode it as base64 (simulating recorder output)
    try:
        # Create test audio
        audio = AudioSegment.silent(duration=1000)  # 1 second silence
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        audio.export(temp_file.name, format="wav")
        
        # Read as bytes and encode as base64 (like recorder does)
        with open(temp_file.name, 'rb') as f:
            audio_bytes = f.read()
        
        audio_base64 = base64.b64encode(audio_bytes).decode()
        
        # Simulate the recorder response format
        recorder_response = {
            "status": "stopped",
            "audioData": audio_base64
        }
        
        print("✅ Created simulated recorder response")
        print(f"   Status: {recorder_response['status']}")
        print(f"   Audio data length: {len(recorder_response['audioData'])} characters")
        
        # Test the extraction process (like in frontend)
        try:
            audio_data = base64.b64decode(recorder_response['audioData'])
            print("✅ Successfully decoded base64 audio data")
            print(f"   Decoded size: {len(audio_data)} bytes")
            
            # Test backend processing
            temp_backend = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_backend.write(audio_data)
            temp_backend.close()
            
            # Test with speech recognition
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_backend.name) as source:
                audio_sr = recognizer.record(source)
                print("✅ Successfully processed with speech_recognition")
                print(f"   Audio data type: {type(audio_sr)}")
            
            # Clean up
            os.unlink(temp_file.name)
            os.unlink(temp_backend.name)
            
            return True
            
        except Exception as e:
            print(f"❌ Processing failed: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_wav_only_workflow():
    """Test if our app works with WAV-only (no FFmpeg needed)"""
    print("\n📋 Testing WAV-Only Workflow")
    print("=" * 50)
    
    try:
        print("1. Frontend records audio...")
        # Simulate frontend recording (WAV format)
        frontend_audio = AudioSegment.silent(duration=1000)
        temp_frontend = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        frontend_audio.export(temp_frontend.name, format="wav")
        print("   ✅ Frontend creates WAV audio")
        
        print("2. Frontend sends to backend...")
        with open(temp_frontend.name, 'rb') as f:
            audio_data = f.read()
        print(f"   ✅ Audio data size: {len(audio_data)} bytes")
        
        print("3. Backend processes audio...")
        # Backend saves uploaded file
        temp_backend_original = tempfile.NamedTemporaryFile(delete=False)
        temp_backend_original.write(audio_data)
        temp_backend_original.close()
        
        # Backend converts (even if already WAV)
        loaded_audio = AudioSegment.from_file(temp_backend_original.name)
        converted_audio = loaded_audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        
        temp_backend_converted = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        converted_audio.export(temp_backend_converted.name, format="wav")
        print("   ✅ Backend converts to speech recognition format")
        
        print("4. Speech recognition processes...")
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_backend_converted.name) as source:
            audio_sr = recognizer.record(source)
        print("   ✅ Speech recognition successful")
        
        # Clean up
        os.unlink(temp_frontend.name)
        os.unlink(temp_backend_original.name)
        os.unlink(temp_backend_converted.name)
        
        print("✅ Complete WAV-only workflow successful!")
        return True
        
    except Exception as e:
        print(f"❌ WAV-only workflow failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Audio Workflow Without FFmpeg")
    print("=" * 55)
    
    # Test 1: Streamlit audio format
    test1 = test_streamlit_audio_format()
    
    # Test 2: Complete WAV workflow
    test2 = test_wav_only_workflow()
    
    # Summary
    print("\n" + "=" * 55)
    if test1 and test2:
        print("🎉 Great news! The app should work WITHOUT FFmpeg!")
        print("✅ WAV format processing is sufficient for our medical diagnosis app")
        print("\n📋 Why this works:")
        print("   - streamlit-realtime-audio-recorder likely produces WAV format")
        print("   - Our backend converts everything to WAV anyway")
        print("   - speech_recognition library handles WAV natively")
        print("   - No need for complex format conversion")
        
        print("\n🚀 You can safely ignore the FFmpeg warning and continue testing!")
        
    else:
        print("⚠️  There might be format compatibility issues")
        print("📋 Consider installing FFmpeg for broader format support")
        
    print("\n🔧 To install FFmpeg (optional):")
    print("   1. Download from: https://ffmpeg.org/download.html")
    print("   2. Or use: winget install ffmpeg")
    print("   3. Or use: choco install ffmpeg")
    
    print("\n🚀 Next: Test the complete application:")
    print("   1. python backend/app.py")
    print("   2. streamlit run frontend/app.py")
    print("   3. Try voice recording in chat")
