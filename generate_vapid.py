"""Génère les clés VAPID pour les notifications Web Push."""
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding, PublicFormat, PrivateFormat, NoEncryption
)

private_key = ec.generate_private_key(ec.SECP256R1())
public_key  = private_key.public_key()

vapid_public  = base64.urlsafe_b64encode(
    public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
).rstrip(b'=').decode()

vapid_private = base64.urlsafe_b64encode(
    private_key.private_bytes(Encoding.DER, PrivateFormat.PKCS8, NoEncryption())
).rstrip(b'=').decode()

print("=" * 60)
print("Ajoutez ces 3 variables dans Render > Environment :")
print("=" * 60)
print(f"\nVAPID_PUBLIC_KEY={vapid_public}")
print(f"\nVAPID_PRIVATE_KEY={vapid_private}")
print("\nVAPID_CONTACT=votre@email.com")
print("=" * 60)
