# Cost And Capacity Checklist

Use this checklist before any cloud GPU action that can incur cost.

## Decision Ladder

1. Avoid cloud GPU if a local CPU/Mac/MLX/proxy run can answer the question.
2. Use the smallest useful accelerator for infrastructure smoke and proxy signal:
   - GCP examples: L4 before A100/H100 unless memory or throughput requires more.
   - AWS examples: G5 before P4/P5 unless memory or throughput requires more.
3. Prefer Spot for fault-tolerant, checkpointed jobs.
4. Prefer On-Demand for short smoke tests, time-critical runs, or anything not
   yet resumable.
5. Move to larger GPUs only after a smaller run proves the data, code, artifact
   contract, and metric are meaningful.
6. Use managed training or fleet abstractions only when repeated manual VM
   orchestration is already the bottleneck.

## Fresh Price Gate

Cloud prices and discounts move. Before quoting or optimizing cost, capture:

- provider, region/zone or availability zone;
- instance/machine type and accelerator count;
- purchase option: Spot, On-Demand, reserved/capacity block, or committed use;
- hourly compute, attached storage, object storage, snapshot, network egress, and
  image/license costs where relevant;
- timestamp and source command or official pricing URL.

Use the estimate:

```text
estimated_run_cost =
  hourly_compute_usd * planned_hours
  + persistent_storage_usd
  + object_storage_delta_usd
  + expected_data_transfer_usd
  + safety_margin
```

For exploratory runs, set `planned_hours` from a hard runtime cap, not optimism.

## Capacity Gate

Before launch:

- check quota for the accelerator family in the chosen region;
- check which zones/AZs currently offer the target accelerator;
- keep at least one fallback zone/AZ or smaller accelerator;
- avoid binding correctness to one zone-specific disk unless it can be rebuilt
  from object storage;
- treat a successful capacity probe as temporary evidence, not a reservation.

Capacity search should not start before artifacts are ready. Holding a GPU while
waiting for weights, data, or dependencies is an avoidable tax.

## Launch Gate

Do not launch until all are true:

- model/data/env/config manifests exist and are revision-pinned;
- hashes can be verified on the target VM;
- object-store write probe succeeds under the VM service role/account;
- startup script passes static shell checks;
- cleanup command is known and copied into the scratchpad/route/report;
- run id, labels/tags, max runtime, and output prefix are fixed;
- expected evidence claim is written in advance.

## Runtime Budget Discipline

- Record start time before instance creation and end time after cleanup.
- Prefer provider runtime limits where available, plus a host-side watchdog.
- Check status frequently enough that a stuck startup does not burn hours.
- Store serial console output or cloud-init logs even for failed runs.
- Write partial metrics and checkpoints periodically so failed runs teach
  something.

## Cleanup Ledger

At close, report all of these:

- instances still running or stopped intentionally;
- unattached disks/EBS volumes;
- snapshots/images retained intentionally;
- elastic/static IPs;
- object-store prefixes written;
- next cleanup command.

If any paid resource remains, name why it remains and when to delete it.
