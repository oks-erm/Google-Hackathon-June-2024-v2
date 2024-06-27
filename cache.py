class Cache:
    cache_dict = {}

    def __init__(self):
        pass

    def get(self, key, on_miss, *args, **kwargs):
        data = self.cache_dict.get(key, False)
        if not data:
            print(f"Cache miss for key: {key}")
            data = on_miss(*args, **kwargs)
            self.cache_dict[key] = data

        return data

    def set(self, key, value):
        self.cache_dict[key] = value

    def clear(self):
        self.cache_dict = {}
