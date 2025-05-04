from pymongo import MongoClient
from contextlib import contextmanager

class MongoManager:
    def __init__(self, uri, db_name):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None

    @contextmanager
    def get_collection(self, collection_name):
        """Контекстный менеджер для работы с коллекцией MongoDB."""
        try:
            if not self.client:
                # Подключаемся к MongoDB при первом использовании
                self.client = MongoClient(self.uri)
                self.db = self.client[self.db_name]
            collection = self.db[collection_name]
            yield collection  # Передаем коллекцию в контекст
        finally:
            # Закрываем соединение с MongoDB, когда контекст завершен
            if self.client:
                self.client.close()

# Пример использования
if __name__ == "__main__":
    mongo_uri = "mongodb://mongoadmin:mongoadmin@localhost:27017/"
    db_name = "test_db"

    # Используем контекстный менеджер для работы с коллекцией
    manager = MongoManager(mongo_uri, db_name)
    with manager.get_collection("test_collection") as collection:
        # Пример работы с коллекцией: вставка документа
        result = collection.insert_one({"name": "Alice", "age": 30})
        print(f"Inserted document with _id: {result.inserted_id}")

        # Пример чтения данных
        document = collection.find_one({"name": "Alice"})
        print(f"Found document: {document}")
