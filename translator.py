import json
from googletrans import Translator

# Путь к translations.json
file_path = "translations.json"

# Ключ, который будем переводить
target_key = "instructions"

# Базовый язык, из которого переводим
source_lang = "ru"

# Список целевых языков (по ключам)
languages = ["en", "uk", "hi", "id", "pt", "vi", "fr"]

# Загружаем файл
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Текст, который будем переводить
base_text = data[source_lang][target_key]

# Инициализация переводчика
translator = Translator()

# Перевод и обновление
for lang in languages:
    translated = translator.translate(base_text, src='ru', dest=lang).text
    data[lang][target_key] = translated

# Сохраняем обратно
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("✔️ Переводы обновлены.")
