# Provider Playbooks

Use official provider docs or CLI/API output for fresh facts. These snippets are
templates; verify flags with the installed CLI before cost-bearing launches.

## GCP

### Fast Facts To Recheck

- Spot VMs can be preempted; design workloads as fault tolerant.
- GCP supports configurable Spot preemption notice duration on supported paths;
  use `120s` only after confirming the current docs and `gcloud` track support it.
- Spot prices are variable. Do not quote them from memory.
- Set the preemption termination action explicitly. Use `STOP` for resumable
  jobs and `DELETE` only for disposable capacity probes.

Useful official docs:

- Spot VMs: `https://docs.cloud.google.com/compute/docs/instances/spot`
- Create Spot VMs: `https://docs.cloud.google.com/compute/docs/instances/create-use-spot`
- Compute pricing: `https://cloud.google.com/products/compute/pricing`
- GPU machine types: `https://docs.cloud.google.com/compute/docs/gpus`

### Preflight Commands

```bash
gcloud config list
gcloud auth list
gcloud compute project-info describe \
  --format='table(quotas.metric,quotas.limit,quotas.usage)'
gcloud compute accelerator-types list \
  --filter='name:(nvidia-l4 OR nvidia-tesla-a100 OR nvidia-h100)' \
  --format='table(zone,name)'
gcloud compute machine-types list --zones="$ZONE" \
  --filter='name~(g2|a2|a3|a4)' \
  --format='table(zone,name,guestCpus,memoryMb)'
gcloud storage ls "$GCS_RUN_PREFIX"
```

Run a write probe with the same service account the VM will use:

```bash
printf 'write-probe\n' > /tmp/gpu-write-probe.txt
gcloud storage cp /tmp/gpu-write-probe.txt "$GCS_RUN_PREFIX/preflight/write-probe.txt"
```

### Launch Template

Use a provider-specific image with NVIDIA drivers/CUDA already handled when
possible. Add explicit GPU accelerator flags only for machine families that need
them; accelerator-optimized machine types may already include GPUs.

```bash
gcloud beta compute instances create "$VM_NAME" \
  --zone="$ZONE" \
  --machine-type="$MACHINE_TYPE" \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP \
  --preemption-notice-duration=120s \
  --maintenance-policy=TERMINATE \
  --max-run-duration="$MAX_RUN_DURATION" \
  --service-account="$SERVICE_ACCOUNT" \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --labels="owner=codex,purpose=gpu-job,run-id=$RUN_ID,expires=$EXPIRES" \
  --metadata="RUN_ID=$RUN_ID,GCS_RUN_PREFIX=$GCS_RUN_PREFIX" \
  --metadata-from-file=startup-script="$STARTUP_SCRIPT"
```

If the job is not yet resumable, use On-Demand for the first thin smoke or keep
the run duration tiny.

### Monitoring And Cleanup

```bash
gcloud compute instances describe "$VM_NAME" --zone="$ZONE" \
  --format='yaml(name,status,machineType,scheduling,labels,disks)'
gcloud compute instances get-serial-port-output "$VM_NAME" --zone="$ZONE"
gcloud storage ls --recursive "$GCS_RUN_PREFIX"
gcloud compute instances delete "$VM_NAME" --zone="$ZONE" --quiet
gcloud compute disks list --filter='labels.owner=codex' \
  --format='table(name,zone,status,sizeGb,users,labels)'
```

## AWS

### Fast Facts To Recheck

- EC2 Spot interruptions provide a two-minute warning before stop or terminate
  on the documented interruption-notice path.
- Interruption behavior can be terminate, stop, or hibernate depending on request
  type and instance support. Confirm support before relying on stop/hibernate.
- Spot prices update frequently. Do not quote them from memory.
- Use S3 as canonical storage and EBS/instance store only as cache or scratch.

Useful official docs:

- Spot interruption notices:
  `https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-instance-termination-notices.html`
- Spot interruptions:
  `https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-interruptions.html`
- EC2 Spot pricing: `https://aws.amazon.com/ec2/spot/pricing/`
- EC2 On-Demand pricing: `https://aws.amazon.com/ec2/pricing/on-demand/`

### Preflight Commands

```bash
aws sts get-caller-identity
aws ec2 describe-instance-type-offerings \
  --location-type availability-zone \
  --filters "Name=instance-type,Values=g5.*,g6.*,p4d.*,p5.*"
aws ec2 describe-instance-types \
  --instance-types "$INSTANCE_TYPE" \
  --query 'InstanceTypes[].{Type:InstanceType,Gpus:GpuInfo.Gpus,Memory:MemoryInfo.SizeInMiB}'
aws ec2 describe-spot-price-history \
  --instance-types "$INSTANCE_TYPE" \
  --product-descriptions "Linux/UNIX" \
  --start-time "$(date -u +%FT%TZ)" \
  --max-results 20
aws s3 ls "$S3_RUN_PREFIX"
```

For On-Demand launches, replace the Spot price-history command with a fresh
official EC2 pricing page or AWS Pricing API lookup for the exact region and
instance type.

For quotas, list the current EC2 service quotas and record the relevant GPU
family quota names instead of relying on memorized quota codes:

```bash
aws service-quotas list-service-quotas --service-code ec2 \
  --query 'Quotas[?contains(QuotaName, `Running On-Demand`) || contains(QuotaName, `Spot`)].{Name:QuotaName,Value:Value}'
```

### Launch Template

Prefer a launch template or EC2 Fleet for repeated work. For one-off jobs:

```bash
aws ec2 run-instances \
  --image-id "$AMI_ID" \
  --instance-type "$INSTANCE_TYPE" \
  --iam-instance-profile "Name=$INSTANCE_PROFILE" \
  --instance-market-options '{"MarketType":"spot","SpotOptions":{"SpotInstanceType":"persistent","InstanceInterruptionBehavior":"stop"}}' \
  --block-device-mappings file://block-devices.json \
  --user-data "file://$STARTUP_SCRIPT" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=owner,Value=codex},{Key=purpose,Value=gpu-job},{Key=run-id,Value=$RUN_ID},{Key=expires,Value=$EXPIRES}]"
```

If `stop` is unsupported or the job uses disposable instance storage, checkpoint
to S3 frequently and assume termination.

### Interruption Polling

Poll the instance metadata service from the VM and flush if an action appears:

```bash
TOKEN="$(curl -sS -X PUT \
  -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600' \
  http://169.254.169.254/latest/api/token)"
curl -fsS \
  -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/spot/instance-action
```

Treat this as a final flush signal. It is not a replacement for periodic
checkpointing.

### Monitoring And Cleanup

```bash
aws ec2 describe-instances \
  --filters "Name=tag:owner,Values=codex" "Name=tag:purpose,Values=gpu-job" \
  --query 'Reservations[].Instances[].{Id:InstanceId,State:State.Name,Type:InstanceType,AZ:Placement.AvailabilityZone,RunId:Tags[?Key==`run-id`]|[0].Value}'
aws s3 ls "$S3_RUN_PREFIX" --recursive
aws ec2 terminate-instances --instance-ids "$INSTANCE_ID"
aws ec2 describe-volumes \
  --filters "Name=tag:owner,Values=codex" "Name=status,Values=available" \
  --query 'Volumes[].{Id:VolumeId,Size:Size,AZ:AvailabilityZone,Tags:Tags}'
```
