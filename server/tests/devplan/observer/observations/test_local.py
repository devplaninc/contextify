import os
import unittest
from typing import List

from dev_observer.api.types.observations_pb2 import ObservationKey, Observation
from dev_observer.observations.local import LocalObservationsProvider


class TestLocalObservationsProvider(unittest.IsolatedAsyncioTestCase):
    async def test_list_files(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        o = LocalObservationsProvider(root_dir=os.path.join(current_dir, "test_data"))
        result = await o.list("repos")
        self.assertEqual(len(result), 2)
        k0 = result[0]
        k1 = result[1]
        self.assertEqual(ObservationKey(kind="repos", name="a.md", key="a.md"), k0)
        self.assertEqual(ObservationKey(kind="repos", name="c.md", key="b/c.md"), k1)
        o0 = await o.get(k0)
        self.assertEqual(Observation(key=k0, content=b'test_a'), o0)
        o1 = await o.get(k1)
        self.assertEqual(Observation(key=k1, content=b'test_c'), o1)

    async def test_list_files_with_path_filter(self):
        """Test the new path filtering functionality"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        o = LocalObservationsProvider(root_dir=os.path.join(current_dir, "test_data"))
        
        # Test without path filter (should return all files)
        result_all = await o.list("repos")
        self.assertEqual(len(result_all), 2)
        
        # Test with path filter "b" (should only return files under b/ directory)
        result_b = await o.list("repos", path="b")
        self.assertEqual(len(result_b), 1)
        self.assertEqual(result_b[0].key, "b/c.md")
        self.assertEqual(result_b[0].name, "c.md")
        self.assertEqual(result_b[0].kind, "repos")
        
        # Test with path filter "a" (should return a.md file)
        result_a = await o.list("repos", path="a")
        self.assertEqual(len(result_a), 1)
        self.assertEqual(result_a[0].key, "a.md")
        self.assertEqual(result_a[0].name, "a.md")
        self.assertEqual(result_a[0].kind, "repos")
        
        # Test with non-existent path filter (should return empty list)
        result_empty = await o.list("repos", path="nonexistent")
        self.assertEqual(len(result_empty), 0)
        
        # Test with path filter "b/c" (should return the specific file)
        result_bc = await o.list("repos", path="b/c")
        self.assertEqual(len(result_bc), 1)
        self.assertEqual(result_bc[0].key, "b/c.md")

    async def test_int_conversion(self):
        b = "Tbbb".encode("utf-8")
        res: int = 0
        for c in b:
            res = (res << 8) + int(c)
        self.assertEqual(1415733858, res)

        tb: List[int] = []
        tc = 1415733858
        while tc > 0:
            tb.append(tc % 256)
            tc = tc >> 8
        tb.reverse()
        st_b = bytes(tb)
        self.assertEqual("Tbbb", st_b.decode("utf-8"))
