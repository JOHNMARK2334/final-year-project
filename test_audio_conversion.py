#!/usr/bin/env python3
"""
Test script to verify audio format conversion functionality in the backend.
This script tests the pydub audio conversion without requiring the full Flask app.
"""

import os
import tempfile
import logging
from pydub import AudioSegment
import base64

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_audio_conversion():
    """Test audio format conversion using pydub"""
    print("🎵 Testing Audio Format Conversion")
    print("=" * 50)
    
    # Test 1: Create a simple audio file and convert it
    try:
        # Generate a simple tone (1 second, 440Hz) 
        audio_segment = AudioSegment.silent(duration=1000)  # 1 second of silence
        tone = AudioSegment.from_mono_audiosegments(
            AudioSegment.from_file(
                "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmUaBjaH1O7OeykEIXHA7dqUQQ4PVK7m77RdGAg+ltryv2gaBzZ+z+zQfScDHmq86+OZUQ0LTqXh8LVgHQU2jdXuzXkpBSF7xu7glEEODlOq5O+zXRkNPJPY88VlGAU6f8/s0H4oBiJtuOzimlEKDCumruKyYRwFJInY8c13JwUfcsft2Z1CDg9Wr+j1s10KCz+V2/PFZhgGNn/Q6s1+Jgcfa7vo4ppRAg0up+LxtGIcBzaP1/L==",
                format="wav"
            )
        )
        
        print("✅ Successfully created test audio segment")
        
        # Test 2: Test various conversion scenarios
        temp_files = []
        
        try:
            # Create a temporary file for testing
            temp_original = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
            temp_files.append(temp_original.name)
            temp_original.close()
            
            # Export as WebM (simulating frontend audio)
            audio_segment.export(temp_original.name, format="webm")
            print("✅ Created simulated WebM audio file")
            
            # Test conversion to WAV
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_files.append(temp_wav.name)
            temp_wav.close()
            
            # Load and convert (this is what the backend will do)
            loaded_audio = AudioSegment.from_file(temp_original.name)
            converted_audio = loaded_audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
            converted_audio.export(temp_wav.name, format="wav")
            
            print("✅ Successfully converted WebM to WAV")
            print(f"   Original duration: {len(loaded_audio)}ms")
            print(f"   Converted duration: {len(converted_audio)}ms")
            print(f"   Sample rate: {converted_audio.frame_rate}Hz")
            print(f"   Channels: {converted_audio.channels}")
            print(f"   Sample width: {converted_audio.sample_width} bytes")
            
            # Test 3: Verify file sizes
            original_size = os.path.getsize(temp_original.name)
            converted_size = os.path.getsize(temp_wav.name)
            
            print(f"   Original file size: {original_size} bytes")
            print(f"   Converted file size: {converted_size} bytes")
            
            if converted_size > 0:
                print("✅ Converted file has valid size")
            else:
                print("❌ Converted file is empty!")
                return False
                
        except Exception as e:
            print(f"❌ Conversion test failed: {str(e)}")
            return False
            
        finally:
            # Clean up temp files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass
                    
        print("✅ All audio conversion tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Audio conversion test failed: {str(e)}")
        return False

def test_supported_formats():
    """Test which audio formats pydub can handle"""
    print("\n🎵 Testing Supported Audio Formats")
    print("=" * 50)
    
    # List of common audio formats to test
    formats = ['mp3', 'wav', 'webm', 'ogg', 'flac', 'm4a']
    
    for fmt in formats:
        try:
            # Create a simple test audio
            audio = AudioSegment.silent(duration=100)  # 100ms silence
            
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(suffix=f'.{fmt}', delete=False)
            temp_file.close()
            
            # Try to export
            audio.export(temp_file.name, format=fmt)
            
            # Try to load back
            loaded = AudioSegment.from_file(temp_file.name)
            
            print(f"✅ {fmt.upper()}: Supported")
            
            # Clean up
            os.unlink(temp_file.name)
            
        except Exception as e:
            print(f"❌ {fmt.upper()}: Not supported ({str(e)})")

if __name__ == "__main__":
    print("🧪 Testing Audio Conversion for Medical Diagnosis App")
    print("=" * 60)
    
    # Test 1: Basic conversion functionality
    success = test_audio_conversion()
    
    # Test 2: Supported formats
    test_supported_formats()
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 Audio conversion tests completed successfully!")
        print("✅ Backend should now be able to handle audio format conversion")
    else:
        print("❌ Audio conversion tests failed!")
        print("⚠️  Backend may have issues with audio processing")
    
    print("\nNext steps:")
    print("1. Run the Flask backend: python backend/app.py")
    print("2. Run the Streamlit frontend: streamlit run frontend/app.py")
    print("3. Test voice recording functionality in the chat")
