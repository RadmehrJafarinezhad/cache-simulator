
"""
LFU Cache Test Suite
====================

This test suite was generated with the assistance of AI.

It is designed to test the correctness and internal consistency of the
LFUCache implementation, including:

- Basic get() and put() operations
- Updating existing keys
- LFU eviction policy
- LRU tie-breaking between keys with the same frequency
- Frequency changes and movement between frequency lists
- Removal of empty frequency lists
- Capacity = 1 behavior
- Unusual keys and values
- Repeated updates
- Randomized testing against an independent reference implementation
- Randomized GET-heavy and PUT-heavy workloads
- High-frequency access
- Consecutive evictions
- Stress testing
- Operation limit handling
- Internal doubly-linked-list structure validation
- min_frequency consistency

The tests use a ReferenceLFU implementation as an independent model
for randomized comparison. This reference implementation is separate
from LFUCache and is used to detect incorrect eviction, frequency,
value, and cache-state behavior.

How to run
----------

Run the following command from the project root:

    python -m test.test

Project structure:

    cache-simulator/
    ├── src/
    │   ├── __init__.py
    │   └── main.py
    │
    ├── test/
    │   ├── __init__.py
    │   └── test.py
    │
    └── .venv/

The test file expects the LFUCache implementation to be available at:

    src.main

and the following classes to exist:

    LFUCache
    OperationLimitExceeded

A successful run ends with:

    🎉 ALL TESTS PASSED 🎉

If a test fails, the failing test name and the corresponding assertion
error are printed before the exception is raised.
"""

from src.main import LFUCache, OperationLimitExceeded
import random


# ============================================================
# REFERENCE MODEL — LFU + LRU
# ============================================================

class ReferenceLFU:

    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.time = 0

    def get(self, key):

        if key not in self.cache:
            return -1

        self.time += 1

        self.cache[key]["freq"] += 1
        self.cache[key]["time"] = self.time

        return self.cache[key]["value"]

    def put(self, key, value):

        self.time += 1

        # Existing key
        if key in self.cache:

            self.cache[key]["value"] = value
            self.cache[key]["freq"] += 1
            self.cache[key]["time"] = self.time

            return

        # Eviction
        if len(self.cache) >= self.capacity:

            min_freq = min(
                item["freq"]
                for item in self.cache.values()
            )

            candidates = [
                key
                for key, item in self.cache.items()
                if item["freq"] == min_freq
            ]

            # Oldest access among same frequency
            victim = min(
                candidates,
                key=lambda k: self.cache[k]["time"]
            )

            del self.cache[victim]

        self.cache[key] = {
            "value": value,
            "freq": 1,
            "time": self.time
        }


# ============================================================
# INTERNAL STRUCTURE VALIDATOR
# ============================================================

def validate_structure(cache):

    cache_dict = cache._LFUCache__cache
    freq_dict = cache._LFUCache__linked_dict

    # --------------------------------------------------------
    # EMPTY CACHE
    # --------------------------------------------------------

    if not cache_dict:

        assert not freq_dict, \
            "Cache is empty but frequency dictionary is not empty"

        return

    # --------------------------------------------------------
    # Every frequency list
    # --------------------------------------------------------

    seen_nodes = set()
    seen_keys = set()

    total_nodes = 0

    for frequency, linked_list in freq_dict.items():

        assert linked_list.head is not None, (
            f"Frequency {frequency} has no head"
        )

        assert linked_list.tail is not None, (
            f"Frequency {frequency} has no tail"
        )

        # Head / Tail boundary
        assert linked_list.head.prev is None, (
            f"Frequency {frequency}: head.prev is not None"
        )

        assert linked_list.tail.next is None, (
            f"Frequency {frequency}: tail.next is not None"
        )

        current = linked_list.head
        previous = None

        while current is not None:

            # ------------------------------------------------
            # No cycles
            # ------------------------------------------------

            assert id(current) not in seen_nodes, (
                f"Node {current.key} appears multiple times / cycle"
            )

            seen_nodes.add(id(current))

            # ------------------------------------------------
            # prev pointer
            # ------------------------------------------------

            assert current.prev is previous, (
                f"Broken prev pointer for key {current.key}"
            )

            # ------------------------------------------------
            # Frequency correctness
            # ------------------------------------------------

            assert current.freq == frequency, (
                f"Key {current.key}: "
                f"node.freq={current.freq}, "
                f"list frequency={frequency}"
            )

            # ------------------------------------------------
            # Node must exist in cache
            # ------------------------------------------------

            assert current.key in cache_dict, (
                f"Key {current.key} exists in linked list "
                f"but not in cache"
            )

            # ------------------------------------------------
            # Same Node object
            # ------------------------------------------------

            assert cache_dict[current.key] is current, (
                f"Cache contains different Node for key {current.key}"
            )

            # ------------------------------------------------
            # No duplicate keys
            # ------------------------------------------------

            assert current.key not in seen_keys, (
                f"Key {current.key} appears more than once"
            )

            seen_keys.add(current.key)

            # ------------------------------------------------
            # next / prev consistency
            # ------------------------------------------------

            if current.next is not None:

                assert current.next.prev is current, (
                    f"Broken next/prev relation "
                    f"around key {current.key}"
                )

            if current.prev is not None:

                assert current.prev.next is current, (
                    f"Broken prev/next relation "
                    f"around key {current.key}"
                )

            previous = current
            current = current.next

            total_nodes += 1

        # Last node must be tail
        assert previous is linked_list.tail, (
            f"Frequency {frequency}: tail mismatch"
        )

    # --------------------------------------------------------
    # Number of nodes
    # --------------------------------------------------------

    assert total_nodes == len(cache_dict), (
        f"Node count mismatch: "
        f"linked_lists={total_nodes}, "
        f"cache={len(cache_dict)}"
    )

    # --------------------------------------------------------
    # Every cache node must exist in exactly one list
    # --------------------------------------------------------

    assert seen_keys == set(cache_dict.keys()), (
        "Cache keys and linked-list keys do not match"
    )

    # --------------------------------------------------------
    # min_frequency
    # --------------------------------------------------------

    actual_min = min(
        node.freq
        for node in cache_dict.values()
    )

    assert cache.min_frequency == actual_min, (
        f"Wrong min_frequency: "
        f"expected={actual_min}, "
        f"actual={cache.min_frequency}"
    )

    assert cache.min_frequency in freq_dict, (
        f"min_frequency={cache.min_frequency} "
        f"does not exist in linked_dict"
    )


# ============================================================
# COMPARE CACHE WITH REFERENCE
# ============================================================

def compare_with_reference(cache, reference):

    actual_cache = cache._LFUCache__cache
    expected_cache = reference.cache

    # Same keys
    assert set(actual_cache.keys()) == set(expected_cache.keys()), (
        f"Keys mismatch\n"
        f"Expected: {set(expected_cache.keys())}\n"
        f"Actual:   {set(actual_cache.keys())}"
    )

    # Same value + frequency
    for key in expected_cache:

        actual_node = actual_cache[key]
        expected_node = expected_cache[key]

        assert actual_node.value == expected_node["value"], (
            f"Value mismatch for key {key}: "
            f"expected={expected_node['value']}, "
            f"actual={actual_node.value}"
        )

        assert actual_node.freq == expected_node["freq"], (
            f"Frequency mismatch for key {key}: "
            f"expected={expected_node['freq']}, "
            f"actual={actual_node.freq}"
        )

    # min frequency
    if expected_cache:

        expected_min = min(
            item["freq"]
            for item in expected_cache.values()
        )

        assert cache.min_frequency == expected_min, (
            f"min_frequency mismatch: "
            f"expected={expected_min}, "
            f"actual={cache.min_frequency}"
        )


# ============================================================
# BASIC TEST
# ============================================================

def test_basic():

    cache = LFUCache(3)

    assert cache.get(1) == -1

    cache.put(1, "A")
    cache.put(2, "B")
    cache.put(3, "C")

    assert cache.get(1) == "A"
    assert cache.get(2) == "B"
    assert cache.get(3) == "C"

    validate_structure(cache)

    print("✓ BASIC")


# ============================================================
# UPDATE TEST
# ============================================================

def test_update():

    cache = LFUCache(3)

    cache.put(1, 10)
    cache.put(2, 20)

    assert cache._LFUCache__cache[1].freq == 1

    cache.put(1, 100)

    assert cache._LFUCache__cache[1].value == 100
    assert cache._LFUCache__cache[1].freq == 2

    validate_structure(cache)

    print("✓ UPDATE")


# ============================================================
# LFU TEST
# ============================================================

def test_lfu():

    cache = LFUCache(3)

    cache.put(1, "A")
    cache.put(2, "B")
    cache.put(3, "C")

    cache.get(1)
    cache.get(1)

    cache.get(2)

    validate_structure(cache)

    # frequencies:
    #
    # 1 -> 3
    # 2 -> 2
    # 3 -> 1

    cache.put(4, "D")

    assert cache.get(3) == -1
    assert cache.get(1) == "A"
    assert cache.get(2) == "B"
    assert cache.get(4) == "D"

    validate_structure(cache)

    print("✓ LFU")


# ============================================================
# LRU TIE BREAK
# ============================================================

def test_lru_tie():

    cache = LFUCache(3)

    cache.put("A", 1)
    cache.put("B", 2)
    cache.put("C", 3)

    cache.put("D", 4)

    assert cache.get("A") == -1
    assert cache.get("B") == 2
    assert cache.get("C") == 3
    assert cache.get("D") == 4

    validate_structure(cache)

    print("✓ LRU TIE")


# ============================================================
# FREQUENCY MOVEMENT
# ============================================================

def test_frequency_movement():

    cache = LFUCache(10)

    for i in range(10):
        cache.put(i, i)

    for _ in range(20):
        cache.get(0)

    for _ in range(10):
        cache.get(1)

    for _ in range(5):
        cache.get(2)

    for _ in range(2):
        cache.get(3)

    validate_structure(cache)

    assert cache._LFUCache__cache[0].freq == 21
    assert cache._LFUCache__cache[1].freq == 11
    assert cache._LFUCache__cache[2].freq == 6
    assert cache._LFUCache__cache[3].freq == 3
    assert cache._LFUCache__cache[4].freq == 1

    assert cache.min_frequency == 1

    print("✓ FREQUENCY MOVEMENT")


# ============================================================
# EMPTY FREQUENCIES
# ============================================================

def test_empty_frequencies():

    cache = LFUCache(3)

    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(3, 3)

    cache.get(1)
    cache.get(2)
    cache.get(3)

    assert cache.min_frequency == 2

    validate_structure(cache)

    cache.get(1)
    cache.get(2)
    cache.get(3)

    assert cache.min_frequency == 3

    validate_structure(cache)

    cache.put(4, 4)

    assert cache.min_frequency == 1

    validate_structure(cache)

    print("✓ EMPTY FREQUENCIES")


# ============================================================
# CAPACITY ONE
# ============================================================

def test_capacity_one():

    cache = LFUCache(1)

    for i in range(200):

        cache.put(i, i)

        assert cache.get(i) == i

        if i > 0:
            assert cache.get(i - 1) == -1

        validate_structure(cache)

    print("✓ CAPACITY ONE")


# ============================================================
# WEIRD KEYS
# ============================================================

def test_weird_keys():

    cache = LFUCache(10)

    data = [
        (-999999999, -123456789),
        (0, 0),
        (999999999999999, 888888888888888),
        ("hello", "world"),
        ("", ""),
        (None, "none"),
        (True, False),
    ]

    for key, value in data:
        cache.put(key, value)

    for key, value in data:
        assert cache.get(key) == value

    validate_structure(cache)

    print("✓ WEIRD KEYS")


# ============================================================
# REPEATED UPDATE
# ============================================================

def test_repeated_update():

    cache = LFUCache(5)

    cache.put("x", 0)

    for i in range(1, 101):

        cache.put("x", i)

        assert cache.get("x") == i

        validate_structure(cache)

    assert cache._LFUCache__cache["x"].freq == 201

    print("✓ REPEATED UPDATE")


# ============================================================
# RANDOM AGAINST CORRECT REFERENCE
# ============================================================

def test_random():

    random.seed(123456)

    for scenario in range(100):

        capacity = random.randint(1, 20)

        cache = LFUCache(capacity)
        reference = ReferenceLFU(capacity)

        operations = 1000

        for operation in range(operations):

            key = random.randint(-50, 50)

            if random.random() < 0.6:

                value = random.randint(-100000, 100000)

                cache.put(key, value)
                reference.put(key, value)

            else:

                actual = cache.get(key)
                expected = reference.get(key)

                assert actual == expected, (
                    f"\nRandom test failed\n"
                    f"scenario={scenario}\n"
                    f"operation={operation}\n"
                    f"capacity={capacity}\n"
                    f"key={key}\n"
                    f"expected={expected}\n"
                    f"actual={actual}"
                )

            validate_structure(cache)
            compare_with_reference(cache, reference)

    print("✓ RANDOM")


# ============================================================
# RANDOM HEAVY GET
# ============================================================

def test_random_heavy_get():

    random.seed(777)

    for scenario in range(50):

        capacity = random.randint(1, 10)

        cache = LFUCache(capacity)
        reference = ReferenceLFU(capacity)

        for operation in range(1000):

            key = random.randint(0, 20)

            if random.random() < 0.85:

                actual = cache.get(key)
                expected = reference.get(key)

                assert actual == expected, (
                    f"Heavy GET mismatch: "
                    f"scenario={scenario}, "
                    f"operation={operation}, "
                    f"key={key}"
                )

            else:

                value = random.randint(-1000, 1000)

                cache.put(key, value)
                reference.put(key, value)

            validate_structure(cache)
            compare_with_reference(cache, reference)

    print("✓ RANDOM HEAVY GET")


# ============================================================
# RANDOM HEAVY PUT
# ============================================================

def test_random_heavy_put():

    random.seed(888)

    for scenario in range(50):

        capacity = random.randint(1, 15)

        cache = LFUCache(capacity)
        reference = ReferenceLFU(capacity)

        for operation in range(1000):

            key = random.randint(0, 30)
            value = random.randint(-10000, 10000)

            if random.random() < 0.9:

                cache.put(key, value)
                reference.put(key, value)

            else:

                actual = cache.get(key)
                expected = reference.get(key)

                assert actual == expected

            validate_structure(cache)
            compare_with_reference(cache, reference)

    print("✓ RANDOM HEAVY PUT")


# ============================================================
# HIGH FREQUENCY
# ============================================================

def test_high_frequency():

    cache = LFUCache(5)

    cache.put("A", "A")

    for _ in range(10000):

        assert cache.get("A") == "A"

    assert cache._LFUCache__cache["A"].freq == 10001
    assert cache.min_frequency == 10001

    validate_structure(cache)

    print("✓ HIGH FREQUENCY")


# ============================================================
# CONSECUTIVE EVICTIONS
# ============================================================

def test_consecutive_evictions():

    cache = LFUCache(3)

    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(3, 3)

    for _ in range(100):
        cache.get(1)

    for i in range(4, 100):

        cache.put(i, i)

        assert cache.get(1) == 1

        validate_structure(cache)

    print("✓ CONSECUTIVE EVICTIONS")


# ============================================================
# STRESS TEST
# ============================================================

def test_stress():

    random.seed(9999)

    for scenario in range(20):

        capacity = random.randint(1, 100)

        cache = LFUCache(capacity)
        reference = ReferenceLFU(capacity)

        for operation in range(5000):

            key = random.randint(-200, 200)

            if random.random() < 0.5:

                value = random.randint(-1000000, 1000000)

                cache.put(key, value)
                reference.put(key, value)

            else:

                actual = cache.get(key)
                expected = reference.get(key)

                assert actual == expected, (
                    f"Stress mismatch\n"
                    f"scenario={scenario}\n"
                    f"operation={operation}\n"
                    f"key={key}\n"
                    f"expected={expected}\n"
                    f"actual={actual}"
                )

            if operation % 50 == 0:

                validate_structure(cache)
                compare_with_reference(cache, reference)

    validate_structure(cache)

    print("✓ STRESS")


# ============================================================
# OPERATION LIMIT
# ============================================================

def test_operation_limit():

    cache = LFUCache(1)

    for i in range(100000):

        cache.put(i % 2, i)
        cache.get(i % 2)

    assert cache.count == 200000

    try:

        cache.put(999, 999)

    except OperationLimitExceeded:

        pass

    else:

        raise AssertionError(
            "OperationLimitExceeded was not raised"
        )

    print("✓ OPERATION LIMIT")


# ============================================================
# FINAL TEST RUNNER
# ============================================================

def run_all_tests():

    print("=" * 70)
    print("🚀 FINAL LFU + LRU TEST SUITE")
    print("=" * 70)

    tests = [

        test_basic,
        test_update,
        test_lfu,
        test_lru_tie,
        test_frequency_movement,
        test_empty_frequencies,
        test_capacity_one,
        test_weird_keys,
        test_repeated_update,

        test_random,
        test_random_heavy_get,
        test_random_heavy_put,

        test_high_frequency,
        test_consecutive_evictions,
        test_stress,

        test_operation_limit,
    ]

    for test in tests:

        try:

            test()

        except Exception as e:

            print()
            print("=" * 70)
            print("❌ TEST FAILED")
            print("=" * 70)
            print("Test:", test.__name__)
            print("Error:", e)
            print("=" * 70)

            raise

    print()
    print("=" * 70)
    print("🎉 ALL TESTS PASSED 🎉")
    print("LFU + LRU + STRUCTURE + RANDOM + STRESS")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()