class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.freq = 1
        self.prev = None
        self.next = None

class LinkedList:
    def __init__(self,initial_node):
        self.head = initial_node
        self.tail = initial_node

    def insert_to_start(self,new_node):
        new_node.next = self.head
        self.head.prev = new_node
        self.head = new_node

    def insert_to_end(self,new_node):
        new_node.prev = self.tail
        self.tail.next = new_node
        self.tail = new_node

    def remove_first_node(self):
        old_node = self.head

        if self.head.next is None:
            self.head = self.tail = None
            return old_node, False

        else:
            self.head = self.head.next
            self.head.prev = None
            return old_node, True

    def remove_last_node(self):
        old_node = self.tail
        if self.tail.prev is None:
            self.tail = self.head = None
            return old_node, False
        else:
            self.tail = self.tail.prev
            self.tail.next = None
            return old_node, True

    def remove(self,node):
        if node is self.head:
            self.remove_first_node()
        elif node is self.tail:
            self.remove_last_node()
        else:
            node.prev.next = node.next
            node.next.prev = node.prev

class LFUCache:

    def __init__(self, capacity):
        self.capacity = capacity
        self.__cache = {}
        self.min_frequency = 1
        self.__linked_dict = {}

    def put(self, key, value):
        pass

    def get(self,key):
        pass

    def is_full(self):
        return len(self.__cache) == self.capacity

