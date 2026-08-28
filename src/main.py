class OperationLimitExceeded(Exception):
    pass


class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.freq = 1
        self.prev = None
        self.next = None


class LinkedList:
    def __init__(self, initial_node):
        self.head = initial_node
        self.tail = initial_node

    def insert_to_start(self, new_node):
        new_node.next = self.head
        self.head.prev = new_node
        self.head = new_node

    def insert_to_end(self, new_node):
        new_node.prev = self.tail
        self.tail.next = new_node
        self.tail = new_node

    def remove_first_node(self):
        old_node = self.head

        if self.head.next is None:
            self.head = self.tail = None
            old_node.prev = None
            old_node.next = None
            return old_node, False

        else:
            self.head = self.head.next
            self.head.prev = None
            old_node.prev = None
            old_node.next = None
            return old_node, True

    def remove_last_node(self):
        old_node = self.tail
        if self.tail.prev is None:
            self.tail = self.head = None
            old_node.prev = None
            old_node.next = None
            return old_node, False
        else:
            self.tail = self.tail.prev
            self.tail.next = None
            old_node.prev = None
            old_node.next = None
            return old_node, True

    def remove(self, node):
        if node is self.head:
            temp, has_node = self.remove_first_node()
            return has_node
        elif node is self.tail:
            temp, has_node = self.remove_last_node()
            return has_node
        else:
            node.prev.next = node.next
            node.next.prev = node.prev
            node.prev = None
            node.next = None
            return True


class LFUCache:

    def __init__(self, capacity):
        self.capacity = capacity

        if capacity < 1 or capacity > 10000:
            raise ValueError("Capacity must be between 1 and 10000")

        self.__cache = {}
        self.min_frequency = 1
        self.__linked_dict = {}
        self.count = 0

    def add_to_frequency(self, node):
        frequency = node.freq

        if frequency not in self.__linked_dict:
            self.__linked_dict[frequency] = LinkedList(node)

        else:
            self.__linked_dict[frequency].insert_to_end(node)

    def put(self, key, value):
        self.count += 1
        self.count_remain()

        if key in self.__cache:
            node = self.__cache[key]
            node.value = value

            has_node = self.__linked_dict[node.freq].remove(node)

            if not has_node:
                self.__linked_dict.pop(node.freq)

                if self.min_frequency == node.freq:
                    self.min_frequency += 1

            node.freq += 1
            self.add_to_frequency(node)
            return None

        elif self.is_full():
            temp_node, has_node = self.__linked_dict[self.min_frequency].remove_first_node()
            self.__cache.pop(temp_node.key)

            if not has_node:
                self.__linked_dict.pop(self.min_frequency)

        node = Node(key, value)
        self.__cache[key] = node
        self.add_to_frequency(node)
        self.min_frequency = 1

    def get(self, key):
        self.count += 1
        self.count_remain()

        if key not in self.__cache:
            return -1

        else:
            node = self.__cache[key]
            has_node = self.__linked_dict[node.freq].remove(node)

            if not has_node:
                self.__linked_dict.pop(node.freq)

                if self.min_frequency == node.freq:
                    self.min_frequency += 1

            node.freq += 1
            self.add_to_frequency(node)
            return node.value

    def is_full(self):
        return len(self.__cache) == self.capacity

    def count_remain(self):
        if self.count > 200000:
            raise OperationLimitExceeded("Maximum number of operations exceeded")

        return f"Operation remain: {200000 - self.count}"
