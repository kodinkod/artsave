import requests
import random

class MetMuseumClient:
    BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"

    def __init__(self):
        self.object_ids = self._load_object_ids()

    def _load_object_ids(self):
        """Запрашивает список всех objectID в коллекции"""
        url = f"{self.BASE_URL}/objects"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["objectIDs"]

    def get_object(self, object_id):
        """Получает данные об объекте по ID"""
        url = f"{self.BASE_URL}/objects/{object_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_random_object(self):
        """Возвращает случайный объект (с изображением, если возможно)"""
        while True:
            object_id = random.choice(self.object_ids)
            obj = self.get_object(object_id)
            if obj.get("primaryImageSmall"):  # Только с изображением
                return obj

# Пример использования
if __name__ == "__main__":
    client = MetMuseumClient()
    artwork = client.get_random_object()

    print("🎨 Title:", artwork.get("title"))
    print("👨‍🎨 Artist:", artwork.get("artistDisplayName"))
    print("📅 Date:", artwork.get("objectDate"))
    print("🖼 Image:", artwork.get("primaryImageSmall"))
