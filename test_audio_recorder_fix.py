#!/usr/bin/env python3
"""
Quick test for the audio recorder parameter fix
"""

def test_audio_recorder_parameters():
    """Test that audio_recorder accepts the correct parameters"""
    try:
        from streamlit_realtime_audio_recorder import audio_recorder
        import inspect
        
        # Get function signature
        sig = inspect.signature(audio_recorder)
        params = list(sig.parameters.keys())
        
        print("✅ Available parameters:", params)
        
        # Check required parameters are available
        required_params = ['interval', 'threshold', 'silenceTimeout']
        missing_params = [p for p in required_params if p not in params]
        
        if missing_params:
            print(f"❌ Missing parameters: {missing_params}")
            return False
        else:
            print("✅ All required parameters available")
            
        # Test that 'key' parameter is NOT in the list (this was causing the error)
        if 'key' in params:
            print("⚠️  Warning: 'key' parameter is available but we're not using it")
        else:
            print("✅ 'key' parameter correctly excluded (not supported)")
            
        # Test actual function call
        try:
            result = audio_recorder(interval=50, threshold=-60, silenceTimeout=1000)
            print("✅ Function call successful with correct parameters")
            return True
        except TypeError as e:
            print(f"❌ Function call failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking parameters: {e}")
        return False

def test_audio_extraction():
    """Test the updated audio extraction function"""
    try:
        from frontend.used.chat_page import extract_audio_data
        import base64
        
        # Test with correct format
        test_audio_data = base64.b64encode(b"fake_audio_data").decode()
        test_input = {
            'status': 'stopped',
            'audioData': test_audio_data
        }
        
        result = extract_audio_data(test_input)
        
        if result == b"fake_audio_data":
            print("✅ Audio extraction works correctly")
            return True
        else:
            print(f"❌ Audio extraction failed. Expected b'fake_audio_data', got {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing audio extraction: {e}")
        return False

def test_config():
    """Test the updated configuration"""
    try:
        from frontend.used.chat_page import AUDIO_CONFIG
        
        required_keys = ['interval', 'threshold', 'silenceTimeout']
        missing_keys = [k for k in required_keys if k not in AUDIO_CONFIG]
        
        if missing_keys:
            print(f"❌ Missing config keys: {missing_keys}")
            return False
        else:
            print("✅ Audio configuration is correct")
            print(f"   Config: {AUDIO_CONFIG}")
            return True
            
    except Exception as e:
        print(f"❌ Error checking config: {e}")
        return False

if __name__ == "__main__":
    print("🎤 Testing Audio Recorder Parameter Fix")
    print("=" * 50)
    
    param_test = test_audio_recorder_parameters()
    extraction_test = test_audio_extraction()
    config_test = test_config()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Parameters: {'✅ Pass' if param_test else '❌ Fail'}")
    print(f"Extraction: {'✅ Pass' if extraction_test else '❌ Fail'}")
    print(f"Config: {'✅ Pass' if config_test else '❌ Fail'}")
    
    if all([param_test, extraction_test, config_test]):
        print("\n🎉 All tests passed! The audio recorder error should be fixed.")
        print("\nYou can now test the audio functionality:")
        print("1. Run: streamlit run frontend/app.py")
        print("2. Navigate to chat and try the microphone")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
