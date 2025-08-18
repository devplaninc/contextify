import unittest

from dev_observer.api.types.observations_pb2 import ObservationKey, Observation
from dev_observer.observations.memory import MemoryObservationsProvider


class TestMemoryObservationsProvider(unittest.IsolatedAsyncioTestCase):
    async def test_list_files_with_path_filter(self):
        """Test the new path filtering functionality for MemoryObservationsProvider"""
        provider = MemoryObservationsProvider()
        
        # Create test observations
        obs1 = Observation(
            key=ObservationKey(kind="repos", key="a.md", name="a.md"),
            content="test_a"
        )
        obs2 = Observation(
            key=ObservationKey(kind="repos", key="b/c.md", name="c.md"),
            content="test_c"
        )
        obs3 = Observation(
            key=ObservationKey(kind="files", key="x.txt", name="x.txt"),
            content="test_x"
        )
        obs4 = Observation(
            key=ObservationKey(kind="repos", key="b/d.md", name="d.md"),
            content="test_d"
        )
        
        # Store observations
        await provider.store(obs1)
        await provider.store(obs2)
        await provider.store(obs3)
        await provider.store(obs4)
        
        # Test without path filter (should return all repos)
        result_all = await provider.list("repos")
        self.assertEqual(len(result_all), 3)
        keys = [r.key for r in result_all]
        self.assertIn("a.md", keys)
        self.assertIn("b/c.md", keys)
        self.assertIn("b/d.md", keys)
        
        # Test with path filter "b" (should only return files under b/ directory)
        result_b = await provider.list("repos", path="b")
        self.assertEqual(len(result_b), 2)
        keys_b = [r.key for r in result_b]
        self.assertIn("b/c.md", keys_b)
        self.assertIn("b/d.md", keys_b)
        
        # Test with path filter "a" (should return a.md file)
        result_a = await provider.list("repos", path="a")
        self.assertEqual(len(result_a), 1)
        self.assertEqual(result_a[0].key, "a.md")
        self.assertEqual(result_a[0].name, "a.md")
        self.assertEqual(result_a[0].kind, "repos")
        
        # Test with non-existent path filter (should return empty list)
        result_empty = await provider.list("repos", path="nonexistent")
        self.assertEqual(len(result_empty), 0)
        
        # Test with path filter "b/c" (should return the specific file)
        result_bc = await provider.list("repos", path="b/c")
        self.assertEqual(len(result_bc), 1)
        self.assertEqual(result_bc[0].key, "b/c.md")
        
        # Test different kind (should return files kind only)
        result_files = await provider.list("files")
        self.assertEqual(len(result_files), 1)
        self.assertEqual(result_files[0].key, "x.txt")
        
        # Test different kind with path filter (should return empty since no files match)
        result_files_path = await provider.list("files", path="b")
        self.assertEqual(len(result_files_path), 0)