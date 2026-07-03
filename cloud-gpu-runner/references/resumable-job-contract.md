# Resumable Job Contract

Cloud GPU jobs should be restartable before they become expensive.

## Artifact Layout

Use object storage as the canonical store:

```text
artifacts/
  models/<model_slug>/<revision>/manifest.json
  datasets/<dataset_slug>/<version>/manifest.json
  envs/<env_slug>/<version>/manifest.json
  runs/<run_id>/
    run_config.json
    latest.json
    checkpoints/
    metrics/
    logs/
    host/
```

Zonal persistent disks, EBS volumes, local NVMe, and container layers are caches.
They can speed startup, but must be rebuildable from object storage.

## Manifest Requirements

Every real run needs manifests for:

- model weights: source, revision, file list, byte counts, hashes;
- dataset: source, version, split hashes, row counts;
- environment: image/container id, package lock or requirements hash;
- run config: command, seed, hyperparameters, batch/sequence limits, output
  prefix, expected metrics, checkpoint interval.

Hash verification should happen on the GPU host before training starts.

## Checkpoint Order

Write checkpoints in this order:

1. write payload to a new checkpoint directory;
2. fsync or equivalent local durability if writing to disk first;
3. upload/sync the checkpoint payload to object storage;
4. verify required files or hashes;
5. update `latest.json` to point at the completed checkpoint.

Never point `latest.json` at a checkpoint still being uploaded.

## Trainer Requirements

The training/eval entrypoint must support:

- `--resume auto` from `latest.json`;
- fixed checkpoint interval by steps or minutes;
- final checkpoint on clean completion;
- signal handling for best-effort final flush;
- preflight object-store write probe;
- local/offline artifact verification;
- structured `run_status.json` on success, failure, and interruption.

For long Spot work, prove resume on a tiny trainer or tiny dataset before the
real job.

## Thin Smoke

A useful smoke is small but real:

- creates the same VM shape or a smaller compatible GPU;
- mounts or downloads from the staged artifacts, not public hubs;
- loads the model/tokenizer or runtime offline;
- executes one tiny GPU operation;
- writes a checkpoint and `latest.json`;
- uploads logs and status;
- deletes the VM or records why it remains.

This proves infrastructure and startup discipline. It does not prove product
quality or model improvement.

## Interruption Smoke

Before trusting Spot:

1. run until checkpoint `N`;
2. stop/interrupt the instance or process;
3. restart from the same run prefix;
4. prove the second pass resumes from checkpoint `N`, not step `0`;
5. upload evidence showing both passes and final status.

Use provider interruption simulation only when available and safe. A controlled
process exit or instance stop is still valuable for validating trainer resume
logic.

## Evidence Boundary

Record what each run proves:

- artifact smoke: files, hashes, IAM, startup, and GPU availability;
- proxy training: objective can learn a distribution under the tested config;
- native generation/eval: behavior changed on the measured slice;
- production claim: only after the product eval contract passes.

Never let a lower-fidelity run borrow the meaning of a higher-fidelity one.
