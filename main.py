class LFUCache:

    def __init__(self, capacity):
        self.capacity = capacity
        self.__cache = {}
