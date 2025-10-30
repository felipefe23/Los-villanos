from argon2 import PasswordHasher

# Funcionamiento: Crea una instancia global de PasswordHasher (Argon2).
# Esta instancia (ph) se importa en otros archivos para:
# 1. Hashear (proteger) la contraseña cuando un usuario se registra.
# 2. Verificar la contraseña cuando un usuario intenta hacer login.

ph = PasswordHasher()