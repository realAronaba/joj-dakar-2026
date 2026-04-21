"""
Génère les clés VAPID pour les notifications Web Push.
Exécuter UNE SEULE FOIS : python generate_vapid.py
Puis copier les valeurs dans les variables d'environnement Render.
"""
from pywebpush import Vapid

v = Vapid()
v.generate_keys()

print("=" * 60)
print("Copiez ces valeurs dans vos variables d'environnement Render :")
print("=" * 60)
print(f"\nVAPID_PUBLIC_KEY={v.public_key_urlsafe_b64}")
print(f"\nVAPID_PRIVATE_KEY={v.private_key_urlsafe_b64}")
print("\nVAPID_CONTACT=votre@email.com")
print("=" * 60)
