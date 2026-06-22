"""Batching."""


def make_batches(dataset, size=32):
    """Yield fixed-size batches from a dataset."""
    for i in range(0, len(dataset), size):
        yield dataset[i:i + size]
