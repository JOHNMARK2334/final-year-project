#!/usr/bin/env python3
"""
Quick Audio Test Script
Run this to verify audio fixes are working
"""

def test_imports():
    """Test all critical imports"""
    try:
        import streamlit as st
        print("✅ Streamlit import: OK")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        from streamlit_realtime_audio_recorder import audio_recorder
        print("✅ Audio recorder import: OK")
    except ImportError as e:
        print(f"❌ Audio recorder import failed: {e}")
        return False
    
    try:
        from frontend.used.chat_page import extract_audio_data, AUDIO_CONFIG, process_audio_data
        print("✅ Chat page functions import: OK")
        print(f"   Audio config: {AUDIO_CONFIG}")
    except ImportError as e:
        print(f"❌ Chat page import failed: {e}")
        return False
    
    return True

def test_backend():
    """Test backend connectivity"""
    try:
        import requests
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend connectivity: OK")
            return True
        else:
            print(f"⚠️ Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend not reachable - make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_audio_data_extraction():
    """Test audio data extraction with sample data"""
    try:
        from frontend.used.chat_page import extract_audio_data
        import base64
        
        # Test with base64 string (common format)
        test_data = base64.b64encode(b"fake_audio_data").decode()
        result = extract_audio_data(test_data)
        if result == b"fake_audio_data":
            print("✅ Audio data extraction (base64): OK")
        else:
            print("❌ Audio data extraction (base64): Failed")
            return False
            
        # Test with dict format (common from recorder)
        dict_data = {"audioData": test_data}
        result = extract_audio_data(dict_data)
        if result == b"fake_audio_data":
            print("✅ Audio data extraction (dict): OK")
        else:
            print("❌ Audio data extraction (dict): Failed")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Audio data extraction test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎤 Audio Fix Verification Test")
    print("=" * 40)
    
    # Run tests
    imports_ok = test_imports()
    backend_ok = test_backend()
    extraction_ok = test_audio_data_extraction()
    
    print("\n" + "=" * 40)
    print("Test Summary:")
    print(f"Imports: {'✅ Pass' if imports_ok else '❌ Fail'}")
    print(f"Backend: {'✅ Pass' if backend_ok else '❌ Fail'}")
    print(f"Audio Processing: {'✅ Pass' if extraction_ok else '❌ Fail'}")
    
    if all([imports_ok, backend_ok, extraction_ok]):
        print("\n🎉 All tests passed! Audio functionality should work correctly.")
        print("\nTo test the UI:")
        print("1. Run: streamlit run frontend/app.py")
        print("2. Navigate to the chat page")
        print("3. Click the microphone icon and speak")
        print("4. For debugging: streamlit run frontend/test_audio_debug.py --server.port 8502")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
        if not backend_ok:
            print("   - Start the backend: cd backend && python app.py")
        if not imports_ok:
            print("   - Install dependencies: pip install -r requirements.txt")
