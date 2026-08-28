# LFU Cache

A Python implementation of an **LFU (Least Frequently Used) Cache** with **LRU tie-breaking**.

The cache stores key-value pairs and removes the least frequently used item when its capacity is reached. If multiple items have the same frequency, the least recently used item among them is removed.

## Features

* `get(key)` and `put(key, value)` operations
* LFU eviction policy
* LRU tie-breaking for items with equal frequency
* Frequency tracking for every cached item
* Doubly linked lists for managing items by frequency
* Configurable cache capacity
* Operation limit protection
* Validation of cache capacity

## Project Structure

```text
cache-simulator/
├── src/
│   ├── __init__.py
│   └── main.py
│
├── test/
│   ├── __init__.py
│   └── test.py
│
├── .gitignore
└── README.md
```

## Requirements

* Python 3.x

No external Python packages are required.

## Usage

Import the `LFUCache` class:

```python
from src.main import LFUCache

cache = LFUCache(3)
```

### `put(key, value)`

Adds a key-value pair to the cache.

```python
cache.put("A", 100)
cache.put("B", 200)
```

If the key already exists, its value is updated and its frequency is increased.

```python
cache.put("A", 150)
```

### `get(key)`

Returns the value associated with the key.

```python
value = cache.get("A")
```

If the key does not exist, `-1` is returned.

```python
cache.get("X")
# -1
```

A successful `get()` also increases the frequency of the corresponding item.

## Eviction Policy

When the cache is full and a new item is added, an item must be removed.

The cache uses the following rules:

1. Find the item with the lowest frequency.
2. If multiple items have the same frequency, remove the least recently used item among them.
3. Insert the new item with an initial frequency of `1`.

For example:

```text
A → frequency 3
B → frequency 1
C → frequency 1
```

If the cache is full and a new item is inserted, either `B` or `C` must be removed.

The one that was accessed less recently is selected.

## Cache Capacity

The capacity must be between `1` and `10000`.

```python
cache = LFUCache(10)
```

Invalid capacities raise `ValueError`:

```python
LFUCache(0)
LFUCache(10001)
```

## Operation Limit

The implementation supports a maximum of **200,000 operations**.

Both `get()` and `put()` count as one operation.

When the limit is exceeded, `OperationLimitExceeded` is raised.

```python
from src.main import LFUCache, OperationLimitExceeded
```

Example:

```python
try:
    cache.get("A")
except OperationLimitExceeded:
    print("Operation limit exceeded")
```

## Internal Structure

The implementation uses three main components:

### `Node`

Each cached item is represented by a `Node` containing:

* `key`
* `value`
* `freq`
* `prev`
* `next`

The `prev` and `next` references are used to form a doubly linked list.

### `LinkedList`

Each frequency can have its own doubly linked list.

The class provides operations for:

* Inserting at the beginning
* Inserting at the end
* Removing the first node
* Removing the last node
* Removing a specific node

### `LFUCache`

The cache maintains:

```text
__cache
```

A dictionary that maps keys to their corresponding `Node` objects.

It also maintains:

```text
__linked_dict
```

A dictionary that maps each frequency to a `LinkedList`.

For example:

```text
frequency 1 → LinkedList
frequency 2 → LinkedList
frequency 3 → LinkedList
```

The cache also stores:

```text
min_frequency
```

which represents the minimum frequency currently present in the cache.

## Testing

The project includes a test suite covering:

* Basic cache operations
* Updating existing keys
* LFU eviction
* LRU tie-breaking
* Frequency movement
* Empty frequency lists
* Capacity of one
* Different key and value types
* Repeated updates
* Randomized testing
* GET-heavy workloads
* PUT-heavy workloads
* High-frequency access
* Consecutive evictions
* Stress testing
* Operation limit handling
* Internal linked-list consistency

The test suite also contains an independent `ReferenceLFU` model for comparing the behavior of the implementation against a separate reference implementation.

### Running the Tests

Run the following command from the project root:

```powershell
python -m test.test
```

A successful run ends with:

```text
🎉 ALL TESTS PASSED 🎉
```

If a test fails, the test name and the corresponding error are printed.

## Error Handling

The implementation can raise:

### `ValueError`

Raised when the cache capacity is outside the allowed range.

```text
Capacity must be between 1 and 10000
```

### `OperationLimitExceeded`

Raised when more than 200,000 cache operations are performed.

```text
Maximum number of operations exceeded
```

## Example

```python
from src.main import LFUCache

cache = LFUCache(2)

cache.put("A", 10)
cache.put("B", 20)

print(cache.get("A"))
# 10

cache.put("C", 30)

print(cache.get("B"))
# -1

print(cache.get("A"))
# 10

print(cache.get("C"))
# 30
```

In this example, `A` was accessed after insertion, increasing its frequency. When `C` was inserted into the full cache, `B` was therefore the item selected for eviction.

## License

MIT

```
```
