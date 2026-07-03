---
name: cloud-gpu-runner
description: Plan, stage, launch, monitor, resume, and clean up GPU jobs on GCP or AWS with cost, capacity, and interruption discipline. Use when user asks to use cloud GPUs, GCP/AWS GPU instances, Spot/preemptible GPU capacity, L4/A100/H100/G5/P4/P5 training, eval, batch inference, or resumable GPU jobs.
---

# Cloud GPU Runner

Use this skill when cloud GPU execution is part of the work. It does not choose
the research direction by itself; pair it with `frontier-search` for experiment
space search or `route-driven-work` for long implementation routes.

Assume `gcloud` and `aws` CLIs may be installed, but never assume the account,
region, quota, price, image, or capacity is current. Check them fresh before any
cost-bearing action.

## Default Workflow

1. Frame the job contract:
   - objective, workload type, provider, region/zone, accelerator, runtime cap;
   - max spend or spend boundary;
   - artifact store, input manifests, output prefix, and evidence claim.
2. Draft the plan:
   - use `scripts/cloud_gpu_plan.py` for a repeatable launch gate;
   - read `references/cost-capacity-checklist.md` for the decision ladder.
3. Stage everything before GPU launch:
   - model weights, datasets, containers/env disks, run config, and startup
     scripts are prepared on local or non-GPU compute;
   - object storage is canonical; zonal disks/EBS volumes are rebuildable caches.
4. Run preflight:
   - fresh price/capacity/quota check;
   - IAM write probe to the run prefix;
   - hash verification for weights/data/env;
   - startup script shell check and cleanup command.
5. Run a thin GPU smoke:
   - local/offline model load;
   - tiny train/eval/inference step;
   - checkpoint write and object-store upload;
   - no hub download, package install, or dependency solve on the GPU VM.
6. Use Spot only after resumability is proven:
   - periodic checkpoints are primary;
   - preemption notice is a final flush window;
   - upload checkpoint payload first, update `latest.json` or equivalent last.
7. Launch the bounded run:
   - labels/tags include owner, purpose, run id, and expiry;
   - record start time, expected stop condition, monitor command, and cleanup path.
8. Close the run:
   - copy logs, host metadata, serial output, metrics, and final artifacts;
   - delete or intentionally retain instances, unattached disks, snapshots, and
     elastic IPs;
   - record end time, cost estimate, evidence boundary, and next run.

## Provider Paths

- GCP: read `references/provider-playbooks.md#gcp`.
- AWS: read `references/provider-playbooks.md#aws`.
- Resumable job design: read `references/resumable-job-contract.md`.
- Cost and capacity gates: read `references/cost-capacity-checklist.md`.

## Non-Negotiable Rules

- Do not use a paid GPU VM for first-time weight downloads, dataset staging,
  package builds, dependency solving, or exploratory shell setup.
- Do not leave GPU instances running unattended without a monitor, runtime cap,
  and cleanup command.
- Do not rely on Spot/preemption shutdown hooks as the main checkpointing
  mechanism.
- Do not claim product/model improvement from infrastructure evidence. Training
  loss, smoke success, and saved checkpoints prove only their stated contract.
- Do not report cloud GPU prices from memory. Query official provider pricing or
  CLI/API output during the run and state the timestamp/region.

## Stop Rules

Stop and ask before launch when the job lacks a spend boundary, durable artifact
store, cleanup path, or resumable contract for long Spot work. Stop if provider
credentials, quota, IAM, or region choice require the user's decision.

## Output Shape

When reporting, include:

- `Job Contract`: provider, accelerator, workload, artifacts, runtime and spend.
- `Fresh Provider Facts`: timestamped price, quota, capacity, and docs/CLI source.
- `Launch Gate`: what is staged, what passed smoke, and what remains risky.
- `Run Evidence`: start/end time, artifacts, logs, metrics, and evidence boundary.
- `Cleanup`: active resources retained/deleted and the next cleanup command.
