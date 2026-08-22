class LFUCache:

    def __init__(self, capacity):
        self.capacity = capacity
        self.__cache = {}
        self.last_used = 3

    def put(self, key, value):

        if key in self.__cache:
            self.__cache[key]["value"] = value
            self.__cache[key]["frequency"] += 1
            self.__cache[key]["last_used"] = self.last_used

        elif self.is_full():

            temp = [(key, value["frequency"], value["last_used"]) for key,value in self.__cache.items()]
            temp.sort(key=lambda x: (x[1], x[2]))

            del self.__cache[temp[0][0]]

            self.__cache[key] = {"value": value, "frequency": 1, "last_used": self.last_used}

        else:

            self.__cache[key] = {"value": value, "frequency": 1, "last_used": self.last_used}

        self.last_used += 1

    def is_full(self):
        return len(self.__cache) == self.capacity


cache = LFUCache(2)

cache.put(1, 1)
cache.put(2, 2)
cache.put(3, 3)
