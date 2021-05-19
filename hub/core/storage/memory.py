from os import path
from typing import Union, Iterable
from hub.core.storage.provider import StorageProvider
from multiprocessing.pool import ThreadPool


class MemoryProvider(StorageProvider):
    """Provider class for using the memory."""

    def __init__(self, root):
        self.dict = {}

    def __getitem__(
        self,
        paths: Union[str, Iterable[str]],
    ):
        """Gets the object present at the path within the given byte range.

        Example:
            memory_provider = MemoryProvider("xyz")
            my_data = memory_provider["abc.txt"]

        Args:
            path (str): The path relative to the root of the provider.

        Returns:
            bytes: The bytes of the object present at the path.

        Raises:
            KeyError: If an object is not found at the path.
        """
        if isinstance(paths, str):
            return self.dict[paths]
        with ThreadPool() as pool:
            return pool.map(self.dict.__getitem__, (paths,))

    def __setitem__(
        self, paths: Union[str, Iterable[str]], values: Union[bytes, Iterable[bytes]]
    ):
        """Sets the object present at the path with the value

        Example:
            memory_provider = MemoryProvider("xyz")
            memory_provider["abc.txt"] = b"abcd"

        Args:
            path (str): the path relative to the root of the provider.
            value (bytes): the value to be assigned at the path.
        """

        def set(path_value):
            path, value = path_value
            self.dict[path] = value

        if isinstance(paths, str):
            set((paths, values))
        else:
            with ThreadPool() as pool:
                pool.map(set, list(zip(paths, values)))

    def __iter__(self):
        """Generator function that iterates over the keys of the provider.

        Example:
            memory_provider = MemoryProvider("xyz")
            for my_data in memory_provider:
                pass

        Yields:
            str: the path of the object that it is iterating over, relative to the root of the provider.
        """
        yield from self.dict

    def __delitem__(self, path: str):
        """Delete the object present at the path.

        Example:
            memory_provider = MemoryProvider("xyz")
            del memory_provider["abc.txt"]

        Args:
            path (str): the path to the object relative to the root of the provider.

        Raises:
            KeyError: If an object is not found at the path.
        """
        del self.dict[path]

    def __len__(self):
        """Returns the number of files present inside the root of the provider.

        Example:
            memory_provider = MemoryProvider("xyz")
            len(memory_provider)

        Returns:
            int: the number of files present inside the root.
        """
        return len(self.dict)