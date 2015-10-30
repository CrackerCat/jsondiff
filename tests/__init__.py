import unittest

from jsondiff import diff, replace, add, discard, insert, delete, update

from .utils import generate_random_json, perturbate_json


def randomize(n, scenario_generator, seed=12038728732):
    def decorator(test):
        def randomized_test(self):
            from random import Random
            rng = Random(seed)
            for i in range(n):
                scenario = scenario_generator(self, rng)
                try:
                    test(self, scenario)
                except Exception as e:
                    import sys
                    raise type(e), type(e)(e.message + ' with scenario %r' % (scenario,)), sys.exc_info()[2]
        return randomized_test
    return decorator


class JsonDiffTests(unittest.TestCase):

    def test_a(self):

        self.assertEqual({}, diff(1, 1))
        self.assertEqual({}, diff(True, True))
        self.assertEqual({}, diff('abc', 'abc'))
        self.assertEqual({}, diff([1, 2], [1, 2]))
        self.assertEqual({}, diff((1, 2), (1, 2)))
        self.assertEqual({}, diff({1, 2}, {1, 2}))
        self.assertEqual({}, diff({'a': 1, 'b': 2}, {'a': 1, 'b': 2}))
        self.assertEqual({}, diff([], []))
        self.assertEqual({}, diff(None, None))
        self.assertEqual({}, diff({}, {}))
        self.assertEqual({}, diff(set(), set()))

        self.assertEqual(2, diff(1, 2))
        self.assertEqual(False, diff(True, False))
        self.assertEqual('def', diff('abc', 'def'))
        self.assertEqual([3, 4], diff([1, 2], [3, 4]))
        self.assertEqual((3, 4), diff((1, 2), (3, 4)))
        self.assertEqual({3, 4}, diff({1, 2}, {3, 4}))
        self.assertEqual({replace: {'c': 3, 'd': 4}}, diff({'a': 1, 'b': 2}, {'c': 3, 'd': 4}))

        self.assertEqual({'c': 3, 'd': 4}, diff([1, 2], {'c': 3, 'd': 4}))
        self.assertEqual(123, diff({'a': 1, 'b': 2}, 123))

        self.assertEqual({delete: ['b']}, diff({'a': 1, 'b': 2}, {'a': 1}))
        self.assertEqual({'b': 3}, diff({'a': 1, 'b': 2}, {'a': 1, 'b': 3}))
        self.assertEqual({'c': 3}, diff({'a': 1, 'b': 2}, {'a': 1, 'b': 2, 'c': 3}))
        self.assertEqual({delete: ['b'], 'c': 3}, diff({'a': 1, 'b': 2}, {'a': 1, 'c': 3}))

        self.assertEqual({add: {3}}, diff({1, 2}, {1, 2, 3}))
        self.assertEqual({add: {3}, discard: {4}}, diff({1, 2, 4}, {1, 2, 3}))
        self.assertEqual({discard: {4}}, diff({1, 2, 4}, {1, 2}))

        self.assertEqual({insert: [(1, 'b')]}, diff(['a', 'c'], ['a', 'b', 'c']))
        self.assertEqual({insert: [(1, 'b')], delete: [0, 3]}, diff(['x', 'a', 'c', 'x'], ['a', 'b', 'c']))
        self.assertEqual(
            {insert: [(2, 'b')], delete: [0, 4], 1: {'v': 20}},
            diff(['x', 'a', {'v': 11}, 'c', 'x'], ['a', {'v': 20}, 'b', 'c'])
        )
        self.assertEqual(
            {insert: [(2, 'b')], delete: [0, 4],  1: {'v': 20}},
            diff(['x', 'a', {'u': 10, 'v': 11}, 'c', 'x'], ['a', {'u': 10, 'v': 20}, 'b', 'c'])
        )

    def generate_scenario(self, rng):
        a = generate_random_json(rng, sets=True)
        b = perturbate_json(a, rng, sets=True)
        return a, b

    def generate_scenario_no_sets(self, rng):
        a = generate_random_json(rng, sets=False)
        b = perturbate_json(a, rng, sets=False)
        return a, b

    @randomize(1000, generate_scenario_no_sets)
    def test_dump(self, scenario):
        a, b = scenario
        diff(a, b, syntax='compact', dump=True)
        diff(a, b, syntax='explicit', dump=True)
        diff(a, b, syntax='symmetric', dump=True)

    @randomize(1000, generate_scenario)
    def test_compact_syntax(self, scenario):
        a, b = scenario
        d = diff(a, b, syntax='compact')

    @randomize(1000, generate_scenario)
    def test_explicit_syntax(self, scenario):
        a, b = scenario
        diff(a, b, syntax='explicit')

    @randomize(1000, generate_scenario)
    def test_symmetric_syntax(self, scenario):
        a, b = scenario
        diff(a, b, syntax='symmetric')