import jwt
import time


def generate_token():
    # Установите время жизни токена (в секундах)
    expiration_time = time.time() + 3600  # Например, 1 час

    # Создайте токен с использованием HS256 алгоритма и секретного ключа 'secret'
    token = jwt.encode(
        {
            "exp": expiration_time,
            "user_id": '86830a5a-4b8c-4ea3-91f6-a2b6e03bdc50'
        },
        'secret',
        algorithm='HS256'
    )

    return token


# Генерировать токен
generated_token = generate_token()

# Вывести сгенерированный токен
print(generated_token)
