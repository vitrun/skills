#!/usr/bin/env python3
"""Generate a cloud GPU launch gate for GCP or AWS jobs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone


def money(value: float) -> str:
    return f"${value:,.2f}"


def command_block(lines: list[str]) -> str:
    return "```bash\n" + "\n".join(lines) + "\n```"


def gcp_commands(args: argparse.Namespace) -> str:
    zone = args.zone or "<zone>"
    run_prefix = args.artifact_uri or "gs://<bucket>/<prefix>/runs/<run_id>"
    vm_name = f"{args.job_name}-<run-id>"
    lines = [
        "gcloud config list",
        "gcloud auth list",
        "gcloud compute project-info describe --format='table(quotas.metric,quotas.limit,quotas.usage)'",
        (
            "gcloud compute accelerator-types list "
            "--filter='name:(nvidia-l4 OR nvidia-tesla-a100 OR nvidia-h100)' "
            "--format='table(zone,name)'"
        ),
        f"gcloud compute machine-types list --zones='{zone}' --filter='name~(g2|a2|a3|a4)'",
        f"gcloud storage ls '{run_prefix}'",
        f"printf 'write-probe\\n' > /tmp/{args.job_name}-write-probe.txt",
        (
            f"gcloud storage cp /tmp/{args.job_name}-write-probe.txt "
            f"'{run_prefix}/preflight/write-probe.txt'"
        ),
    ]
    launch = [
        f"gcloud beta compute instances create '{vm_name}' \\",
        f"  --zone='{zone}' \\",
        f"  --machine-type='{args.instance_type or '<machine-type>'}' \\",
        f"  --provisioning-model={'SPOT' if args.capacity == 'spot' else 'STANDARD'} \\",
    ]
    if args.capacity == "spot":
        launch.extend(
            [
                "  --instance-termination-action=STOP \\",
                "  --preemption-notice-duration=120s \\",
            ]
        )
    launch.extend(
        [
            f"  --max-run-duration='{args.max_run_duration}' \\",
            "  --maintenance-policy=TERMINATE \\",
            f"  --labels='owner=codex,purpose=gpu-job,run-id=<run-id>,expires={args.expires}' \\",
            "  --metadata='RUN_ID=<run-id>,GCS_RUN_PREFIX=<gcs-run-prefix>' \\",
            "  --metadata-from-file=startup-script=<startup.sh>",
        ]
    )
    cleanup = [
        f"gcloud compute instances describe '{vm_name}' --zone='{zone}' --format='yaml(name,status,machineType,scheduling,labels,disks)'",
        f"gcloud compute instances get-serial-port-output '{vm_name}' --zone='{zone}'",
        f"gcloud compute instances delete '{vm_name}' --zone='{zone}' --quiet",
        "gcloud compute disks list --filter='labels.owner=codex' --format='table(name,zone,status,sizeGb,users,labels)'",
    ]
    return (
        "### GCP Preflight\n\n"
        + command_block(lines)
        + "\n\n### GCP Launch Template\n\n"
        + command_block(launch)
        + "\n\n### GCP Monitor And Cleanup\n\n"
        + command_block(cleanup)
    )


def aws_commands(args: argparse.Namespace) -> str:
    run_prefix = args.artifact_uri or "s3://<bucket>/<prefix>/runs/<run_id>"
    instance_type = args.instance_type or "<instance-type>"
    lines = [
        "aws sts get-caller-identity",
        (
            "aws ec2 describe-instance-type-offerings "
            "--location-type availability-zone "
            "--filters 'Name=instance-type,Values=g5.*,g6.*,p4d.*,p5.*'"
        ),
        (
            f"aws ec2 describe-instance-types --instance-types '{instance_type}' "
            "--query 'InstanceTypes[].{Type:InstanceType,Gpus:GpuInfo.Gpus,Memory:MemoryInfo.SizeInMiB}'"
        ),
        f"aws s3 ls '{run_prefix}'",
        f"printf 'write-probe\\n' > /tmp/{args.job_name}-write-probe.txt",
        f"aws s3 cp /tmp/{args.job_name}-write-probe.txt '{run_prefix}/preflight/write-probe.txt'",
    ]
    if args.capacity == "spot":
        lines.insert(
            3,
            (
                f"aws ec2 describe-spot-price-history --instance-types '{instance_type}' "
                "--product-descriptions 'Linux/UNIX' --start-time \"$(date -u +%FT%TZ)\" --max-results 20"
            ),
        )
    else:
        lines.insert(
            3,
            "# Capture On-Demand price from the official AWS EC2 pricing page or AWS Pricing API before launch.",
        )
    market_options = (
        "  --instance-market-options '{\"MarketType\":\"spot\",\"SpotOptions\":{\"SpotInstanceType\":\"persistent\",\"InstanceInterruptionBehavior\":\"stop\"}}' \\"
        if args.capacity == "spot"
        else None
    )
    launch = [
        "aws ec2 run-instances \\",
        "  --image-id '<ami-id>' \\",
        f"  --instance-type '{instance_type}' \\",
        "  --iam-instance-profile 'Name=<instance-profile>' \\",
        "  --block-device-mappings file://block-devices.json \\",
        "  --user-data 'file://<startup.sh>' \\",
        f"  --tag-specifications 'ResourceType=instance,Tags=[{{Key=owner,Value=codex}},{{Key=purpose,Value=gpu-job}},{{Key=job,Value={args.job_name}}},{{Key=expires,Value={args.expires}}}]'",
    ]
    if market_options is not None:
        launch.insert(4, market_options)
    cleanup = [
        (
            "aws ec2 describe-instances "
            "--filters 'Name=tag:owner,Values=codex' 'Name=tag:purpose,Values=gpu-job' "
            "--query 'Reservations[].Instances[].{Id:InstanceId,State:State.Name,Type:InstanceType,AZ:Placement.AvailabilityZone}'"
        ),
        f"aws s3 ls '{run_prefix}' --recursive",
        "aws ec2 terminate-instances --instance-ids '<instance-id>'",
        (
            "aws ec2 describe-volumes "
            "--filters 'Name=tag:owner,Values=codex' 'Name=status,Values=available' "
            "--query 'Volumes[].{Id:VolumeId,Size:Size,AZ:AvailabilityZone,Tags:Tags}'"
        ),
    ]
    return (
        "### AWS Preflight\n\n"
        + command_block(lines)
        + "\n\n### AWS Launch Template\n\n"
        + command_block(launch)
        + "\n\n### AWS Monitor And Cleanup\n\n"
        + command_block(cleanup)
    )


def render(args: argparse.Namespace) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cost_lines = ["Fresh price required before launch."]
    if args.hourly_usd is not None:
        subtotal = args.hourly_usd * args.max_hours
        with_margin = subtotal * (1 + args.safety_margin)
        cost_lines = [
            f"Hourly estimate: {money(args.hourly_usd)}",
            f"Planned hours: {args.max_hours:g}",
            f"Compute subtotal: {money(subtotal)}",
            f"With safety margin {args.safety_margin:.0%}: {money(with_margin)}",
        ]

    provider_section = gcp_commands(args) if args.provider == "gcp" else aws_commands(args)
    capacity_note = (
        "Spot is selected. Resume smoke and periodic checkpoints are required before a real run."
        if args.capacity == "spot"
        else "On-Demand is selected. Keep runtime capped and clean up immediately after evidence is copied."
    )

    cost_markdown = "\n".join(f"- {line}" for line in cost_lines)
    return "\n".join(
        [
            f"# Cloud GPU Launch Gate: {args.job_name}",
            "",
            f"Generated: `{now}`",
            "",
            "## Job Contract",
            "",
            f"- Provider: `{args.provider}`",
            f"- Workload: `{args.workload}`",
            f"- Accelerator: `{args.accelerator}`",
            f"- Instance or machine type: `{args.instance_type or 'TBD'}`",
            f"- Region: `{args.region or 'TBD'}`",
            f"- Zone/AZ: `{args.zone or 'TBD'}`",
            f"- Capacity: `{args.capacity}`",
            f"- Runtime cap: `{args.max_run_duration}`",
            f"- Artifact URI: `{args.artifact_uri or 'TBD'}`",
            f"- Evidence claim: `{args.evidence_claim}`",
            "",
            "## Cost Boundary",
            "",
            cost_markdown,
            "",
            "## Capacity Note",
            "",
            f"- {capacity_note}",
            "- Capacity probes are temporary evidence. Do not hold GPUs while staging artifacts.",
            "",
            "## Launch Gate",
            "",
            "- [ ] Fresh official price captured with timestamp and region.",
            "- [ ] Quota checked for the accelerator family.",
            "- [ ] Model weights are staged and hash-verifiable without public hub downloads.",
            "- [ ] Dataset/input artifacts are staged and hash-verifiable.",
            "- [ ] Environment/container/image is staged; no package solve on GPU startup.",
            "- [ ] VM role/service account can write to the run prefix.",
            "- [ ] Startup script passed static checks.",
            "- [ ] Thin GPU smoke passed.",
            "- [ ] Resume smoke passed if using Spot for non-trivial work.",
            "- [ ] Cleanup command and retained-resource policy are written down.",
            "",
            provider_section,
            "",
            "## Closeout",
            "",
            "- Start time:",
            "- End time:",
            "- Object-store evidence:",
            "- Metrics copied:",
            "- Resources deleted:",
            "- Resources intentionally retained:",
            "- Evidence boundary:",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=["gcp", "aws"], required=True)
    parser.add_argument("--job-name", required=True)
    parser.add_argument("--workload", default="training", help="training, eval, batch-inference, smoke, etc.")
    parser.add_argument("--accelerator", default="TBD", help="L4, A100, H100, G5, P4, P5, etc.")
    parser.add_argument("--instance-type", help="GCP machine type or AWS instance type")
    parser.add_argument("--region")
    parser.add_argument("--zone", help="GCP zone or AWS availability zone")
    parser.add_argument("--capacity", choices=["spot", "on-demand"], default="spot")
    parser.add_argument("--max-hours", type=float, default=1.0)
    parser.add_argument("--max-run-duration", default="2h")
    parser.add_argument("--hourly-usd", type=float)
    parser.add_argument("--safety-margin", type=float, default=0.20)
    parser.add_argument("--artifact-uri", help="gs:// or s3:// run prefix")
    parser.add_argument("--expires", default="YYYYMMDD")
    parser.add_argument(
        "--evidence-claim",
        default="infrastructure evidence only until the task eval passes",
    )
    args = parser.parse_args()

    if args.max_hours <= 0:
        parser.error("--max-hours must be positive")
    if args.hourly_usd is not None and args.hourly_usd < 0:
        parser.error("--hourly-usd must be non-negative")
    if args.safety_margin < 0:
        parser.error("--safety-margin must be non-negative")

    print(render(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
