# Demo 05 — Grounded Q&A over an ML training loop

## Where this came from
A `trainer` package with a `train` loop that batches data, steps an
`Optimizer`, and checkpoints each epoch. This is the "explain this training
code to me" question that LLM assistants usually answer by *guessing* — here it
is answered from the actual call graph.

## The question you're answering
> *"How does a training step update the weights, and what does the loop call
> each epoch?"*

## Run it
```bash
cd demos/05-ml-training-loop
codegraph build . --out codegraph.json

# Ground truth from the graph
codegraph callees func:trainer.loop.train_step
#   -> func:trainer.loop.batch_loss
#   -> func:trainer.loop.compute_gradients
#   -> func:trainer.optim.Optimizer.apply

# Inspect the exact context block `ask` would send to the fleet (no network):
python -c "from codegraph.graph import KnowledgeGraph; from codegraph.ask import assemble_context; print(assemble_context(KnowledgeGraph.load('codegraph.json'), 'how does a training step update the weights?'))"

# With a local OpenAI-compatible backend running (e.g. the Cognis fleet on :8772):
codegraph ask "how does a training step update the weights?"
```

## What to expect
- `build` reports **14 nodes, 19 edges**.
- `callees` of `train_step` shows it computes gradients, applies them via the
  `Optimizer`, and returns the batch loss.
- `assemble_context` prints the grounded block (symbols + docstrings +
  connections) — verifiable offline. `ask` then sends *only* that block to the
  model, so the answer cannot invent symbols that aren't in the code.

## How to act on it
Run `codegraph ask` with `--backend http://host:port --model <name>` to point at
any OpenAI-compatible endpoint. The `assemble_context` step is pure, so you can
unit-test what the model is grounded on without a live server.
