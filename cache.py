# # Description: A simple cache class that can be used to store data in memory or on disk.

# import json


# class Cache:
#     cache_dict = {}
#     cache_file = 'local_cache.json'

#     def __init__(self, disk=False):
#         self.disk = disk
#         if self.disk:
#             self.load()

#     def get(self, key, on_miss, *args, **kwargs):
#         data = self.cache_dict.get(key, False)
#         if not data:
#             print(f"Cache miss for key: {key}")
#             data = on_miss(*args, **kwargs)
#             self.set(key, data)

#         return data

#     def set(self, key, value):
#         self.cache_dict[key] = value
#         if self.disk:
#             self.store()

#     def clear(self):
#         self.cache_dict = {}
#         if self.disk:
#             self.store()

#     def load(self):
#         with open(self.cache_file, 'r') as data:
#             cached = data.read()
#             if cached is not None and isinstance(cached, str):
#                 self.cache_dict = json.loads(cached)

#     def store(self):
#         sterilize = json.dumps(self.cache_dict)
#         with open(self.cache_file, 'w') as f:
#             json.dump(self.cache_dict, f)
