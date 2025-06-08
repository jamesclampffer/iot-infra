"""
Utilities for processing data efficiently and getting it ready for other tools
"""

import collections
import pickle
import sys
import types
import typing


# This is expensive to do, try to stash results rather than call
# repeatedly.
def flatten_schema(record: dict, drilldown=lambda x: x) -> dict:
    """
    Take a dictionary that represents a heirarchal data representation and
    flatten it into a single dimension.

    A drilldown function can be used to indicate which node ot

    NOTE: None will be used in places where type coercion fails, or the data
    on the leaf nodes of the hierarchy aren't scalars.

    Schema will be encoded by using a dot to indicate each level of hierarchy.
    {'a':1, b:{ 'she': 'sells', 'sea': 'shells' }}
    ->
    {'a': 1, 'b.she': 'sells', 'b.sea': 'shells'}
    """

    assert type(record) == dict, "Expected a dictionary, got {}".format(type(record))
    q = []
    for key, val in record.items():
        q.append((key, val))

    leaves = {}
    while len(q) > 0:
        curr = q.pop(0)
        k, v = curr
        if dict == type(v):
            for subk, subv in v.items():
                q.append((k + "." + subk, subv))
        elif type(v) in (list, tuple, set):
            # no varlen that requires ordinal reference.
            # Use an OLAP db if you want to do that well..
            leaves[k] = None
        else:
            # Leaf node, add to output.
            leaves[k] = v

    return leaves


class PickledDataBlock:
    __slots__ = "fname", "unpickled", "data_vector", "is_dense", "schema"

    def __init__(self, picked_file: str):
        """
        Assume a dictionary base structure with some metadata. One of
        the properties will contain a vector of samples.
        """
        self.fname = picked_file
        self.unpickled = None

        try:
            with open(self.fname, "rb") as f:
                self.unpickled = pickle.load(f)
        except FileNotFoundError as err:
            raise err
        except pickle.UnpicklingError as err:
            # if it's a versioning thing it's going to keep happening
            assert False, "Unpickling error: {}".format(err)

        # Idea is make the vectorized form and then discard this
        # Original structure can still be rebuilt, but vertorized is
        # nicer to work with for predicated scans.
        self.data_vector = self.unpickled["samples"]
        assert (
            len(self.data_vector) > 0
        ), "fatal: Empty block prevents schema extraction"

        vec, fields, is_dense = self._initialize_data(self.data_vector)

        self.data_vector = vec
        self.schema = fields
        self.is_dense = is_dense

    def _union_all_keys(self, data: list, drilldown=lambda x : x) -> tuple[set, bool]:
        keyunion = set()
        # initialize with first item for dense check.
        dense = True
        for itemattr in drilldown(self.data_vector[0]):
            keyunion.add(itemattr)

        # Run through whole set, going over one element a second time
        # idempotent. And negligable amortized cost << simplicity.
        for item in self.data_vector:
            item = drilldown(item)
            for itemattr in item:
                if itemattr not in keyunion:
                    dense = False
                    keyunion.add(itemattr)
        return (keyunion, dense)

    def _initialize_data(
        self, data_vector: list[dict], allow_missing=True
    ) -> tuple[list[dict], list, bool]:
        """
        Normalize all elements into flattened form.

        Parameters
        allow_missing:
        If true then element schemata don't have to
        match - it could actually be disjoint.

        If false then ground-truth is established by the first element and
        the rest must match it exactly, including data types.

        Knowning the schema is the same a dense representation can be
        materialized.
        """
        assert allow_missing == True, "schema enfocement not implemented yet"

        outvec = []
        colunion, is_dense = self._union_all_keys(data_vector, lambda x : x['status_data'])

        for nested in data_vector:
            outvec.append(flatten_schema(nested, lambda x : x['sample']))

        return (outvec, [c for c in colunion], is_dense)

    def __get__(self, idx: int) -> dict:
        """
        Fetch item by 0-based index.
        """
        # alias to avoid some dictionary lookups
        vec = self.data_vector

        # May regret returning null on invalid, however according to
        # the asserts in the constructor it can only mean out of bounds
        if type(idx) == int and (idx < 0 or idx > len(vec)):
            return None
        return vec[idx]

    @property
    def dense(self) -> bool:
        return self.is_dense

    @property
    def cols(self) -> list:
        return self.schema

    @property
    def len(self) -> int:
        """
        Return the number of samples in the block.
        """
        return len(self.data_vector)


datamanip_utils = types.SimpleNamespace()

# Indirection between API and implementation.
datamanip_utils.PickledDataBlock = PickledDataBlock
datamanip_utils.flatten_schema = flatten_schema


# Bare minimum , fix mocks first
class SmokeTest:
    def test_flatten_schema():
        """
        Smoke test.
        """
        t1a = flatten_schema({"a": 1, "b": {"she": "sells", "sea": "shells"}})
        t1b = {"a": 1, "b.she": "sells", "b.sea": "shells"}
        print(t1a)
        print(t1b)
        assert t1a == t1b, "Flatten schema failed"

        t2 = flatten_schema({"a": 1, "b": {"she": None, "sea": None}}) == {
            "a": 1,
            "b.she": None,
            "b.sea": None,
        }
        t3 = flatten_schema({"a": 1, "b": {"she": [1, 2], "sea": [3, 4]}}) == {
            "a": 1,
            "b.she": None,
            "b.sea": None,
        }
        assert t2, "Flatten schema failed on None values"
        assert t3, "Flatten schema failed on list values"

    def run_pickle_test():
        x = PickledDataBlock("client\sample_data\sample_data.pickle")

        # quick check for a read using prior info about the file.
        y = x.len
        assert type(y) == int, "Expected int"
        assert y == 5391, "Expected 5291 samples in the data block"

    def run_projection_test():
        x = PickledDataBlock("client\sample_data\sample_data.pickle")
        print(x.cols)
        print(x.dense)

    def run_schema_tests():
        SmokeTest.test_flatten_schema()
        SmokeTest.run_projection_test()

    def test_data():
        SmokeTest.run_pickle_test()


if __name__ == "__main__":
    SmokeTest.run_schema_tests()
    print("Schema tests passed.")
    SmokeTest.test_data()
    print("Data tests passed.")
