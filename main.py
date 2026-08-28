class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.freq = 1

class LFUCache:

    def __init__(self, capacity):
        self.capacity = capacity
        self.__cache = {}
        self.min_frequency = 1
        self.__linked_dict = {}

    def put(self, key, value):
        if key in self.__cache:
            self.__linked_dict_config("put", key, value)
            return

        if self.is_full():
            unused_nodes = self.__linked_dict[self.min_frequency]

            unused_key = unused_nodes[0].key
            del self.__cache[unused_key]
            unused_nodes.pop(0)
            if not self.__linked_dict[self.min_frequency]:
                del self.__linked_dict[self.min_frequency]
                self.min_frequency += 1

        node = Node(key, value)
        self.__cache[key] = node
        self.__linked_dict[1].append(node)

    def get(self, key):
        if key not in self.__cache:
            return -1

        self.__linked_dict_config("get", key)
        return self.__cache[key].value

    def __linked_dict_config(self, config,key,value = None):
        node = self.__cache[key]
        self.__linked_dict[node.freq].remove(node)

        if not self.__linked_dict[node.freq]:
            del self.__linked_dict[node.freq]

        node.freq += 1
        if config == "put":
            node.value = value
            self.__linked_dict[node.freq].append(node)
            return None
        else:
            self.__linked_dict[node.freq].append(node)
            return self.__linked_dict[node.freq]


    def is_full(self):
        return len(self.__cache) == self.capacity


cache = LFUCache(2)

cache.put(1, 1)
cache.put(2, 2)

cache.get(1)

cache.put(3, 3)

print(cache.get(1))
print(cache.get(2))
print(cache.get(3))
