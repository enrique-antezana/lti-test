#!/usr/bin/env python3
"""
Generate RSA keys for LTI 1.3 testing.

This script generates a private key and extracts the corresponding public key
for use with the LTI 1.3 FastAPI example.
"""

import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


def generate_rsa_keys():
    """Generate RSA private and public keys."""
    
    print("🔑 Generating RSA keys for LTI 1.3...")
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Serialize private key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize public key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Write keys to files
    with open("private.key", "wb") as f:
        f.write(private_pem)
    
    with open("public.key", "wb") as f:
        f.write(public_pem)
    
    print("✅ Keys generated successfully!")
    print("📁 private.key - Keep this secure and don't commit to version control")
    print("📁 public.key - Share this with your LTI platform")
    
    # Display key information
    print(f"\n🔍 Key Details:")
    print(f"   Key Size: {public_key.key_size} bits")
    print(f"   Public Exponent: {public_key.public_numbers().e}")
    
    # Show first few characters of public key for verification
    public_key_str = public_pem.decode('utf-8')
    print(f"\n📋 Public Key Preview:")
    print(f"   {public_key_str[:50]}...")
    
    return True


def check_existing_keys():
    """Check if keys already exist."""
    private_exists = os.path.exists("private.key")
    public_exists = os.path.exists("public.key")
    
    if private_exists and public_exists:
        print("⚠️  Keys already exist!")
        response = input("Do you want to overwrite them? (y/N): ")
        if response.lower() != 'y':
            print("❌ Key generation cancelled.")
            return False
        else:
            print("🔄 Overwriting existing keys...")
    
    return True


def main():
    """Main function."""
    print("🚀 LTI 1.3 RSA Key Generator")
    print("=" * 40)
    
    # Check for existing keys
    if not check_existing_keys():
        return
    
    try:
        # Generate keys
        generate_rsa_keys()
        
        print("\n🎉 Setup complete! You can now:")
        print("   1. Run the FastAPI application: python main.py")
        print("   2. Configure your LTI platform with the public key")
        print("   3. Update the configuration in main.py")
        
    except Exception as e:
        print(f"❌ Error generating keys: {e}")
        print("\n💡 Alternative: Use OpenSSL commands:")
        print("   openssl genrsa -out private.key 2048")
        print("   openssl rsa -in private.key -pubout -out public.key")


if __name__ == "__main__":
    main()
