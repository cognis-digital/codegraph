"""Training loop: builds batches, steps the optimizer, checkpoints.

This is the module a teammate asks about with "how does a training step
actually update the weights?" — a question `codegraph ask` answers from the
graph instead of guessing.
"""

from trainer.checkpoint import save_checkpoint
from trainer.data import make_batches
from trainer.optim import Optimizer


def train(dataset, epochs, lr):
    """Run the training loop and return the final loss."""
    optimizer = Optimizer(lr)
    loss = None
    for epoch in range(epochs):
        for batch in make_batches(dataset):
            loss = train_step(optimizer, batch)
        save_checkpoint(epoch, loss)
    return loss


def train_step(optimizer, batch):
    """One forward/backward step; returns the batch loss."""
    grads = compute_gradients(batch)
    optimizer.apply(grads)
    return batch_loss(batch)


def compute_gradients(batch):
    """Compute gradients for a batch (stubbed)."""
    return [0.01 for _ in batch]


def batch_loss(batch):
    """Return a scalar loss for the batch (stubbed)."""
    return 0.5 / (len(batch) or 1)
