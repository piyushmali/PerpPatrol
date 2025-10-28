#!/usr/bin/env python3
"""
Test WOOFi Pro ed25519 authentication
"""

import os
import time

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_signature_generation():
    """Test the signature generation"""
    api_key = os.getenv('WOOFI_API_KEY', '')
    api_secret = os.getenv('WOOFI_API_SECRET', '')
    
    print(f"🔑 API Key: {api_key[:20]}...")
    print(f"🔐 API Secret: {api_secret[:20]}...")
    
    try:
        if api_key.startswith('ed25519:'):
            print("✅ Detected ed25519 key format")
            
            # Test imports
            from nacl.signing import SigningKey
            import base58
            print("✅ Required libraries imported successfully")
            
            # Test signature generation
            timestamp = str(int(time.time() * 1000))
            method = "GET"
            path = "/v1/client/info"
            body = ""
            
            # The API secret is the private key in base58 format
            private_key_bytes = base58.b58decode(api_secret)
            signing_key = SigningKey(private_key_bytes)
            
            # Create the message to sign
            message = f"{timestamp}{method.upper()}{path}{body}"
            print(f"📝 Message to sign: {message}")
            
            # Sign the message
            signed = signing_key.sign(message.encode())
            
            # Return the signature in base58 format
            signature = base58.b58encode(signed.signature).decode()
            print(f"✅ Signature generated: {signature[:20]}...")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing WOOFi Pro Authentication...")
    print("-" * 50)
    
    success = test_signature_generation()
    
    if success:
        print("\n🎉 Authentication test PASSED!")
        print("✅ Your API credentials should work with WOOFi Pro")
    else:
        print("\n❌ Authentication test FAILED!")
        print("⚠️ There might be an issue with your API credentials or setup")
