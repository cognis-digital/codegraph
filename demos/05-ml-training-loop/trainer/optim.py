"""Optimizer."""


class Optimizer:
    """A toy SGD-style optimizer."""

    def __init__(self, lr):
        self.lr = lr

    def apply(self, grads):
        """Apply gradients (stubbed weight update)."""
        return [g * self.lr for g in grads]
