"""
Confluence Seed Knowledge Data
Contains the 8 required operational knowledge pages for the CloudOps knowledge base.
Each page includes metadata: id, title, spaceKey, version, lastUpdated, author, url, and full content.
"""

from typing import List, Dict, Any

SEED_PAGES: List[Dict[str, Any]] = [
    {
        "id": "1540097",
        "title": "Cloud Operations Overview",
        "spaceKey": "AITEST",
        "version": 3,
        "lastUpdated": "2026-08-10T10:00:00Z",
        "author": "abhinav.singh@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1540097/Cloud+Operations+Overview",
        "content": """
# Cloud Operations Overview

## 1. CloudOps Team Responsibilities
The Cloud Operations (CloudOps) team is responsible for the overall availability, reliability, latency, performance, efficiency, monitoring, and emergency response of all cloud infrastructure supporting production services.

Key duties include:
- Maintaining 99.99% uptime across production cloud environments.
- 24/7/365 tier-2 and tier-3 on-call incident response.
- Managing Infrastructure as Code (Terraform) pipelines and cloud resource lifecycles.
- Enforcing cloud security postures, IAM governance, and least-privilege compliance.
- Capacity planning, cost optimization, and idle asset decommissioning.

## 2. Supported Cloud Platforms
The CloudOps team officially supports and operates:
1. **Google Cloud Platform (GCP)**: Primary hosting environment for containerized microservices (GKE, Cloud Run), serverless workloads, and BigQuery analytics.
2. **Amazon Web Services (AWS)**: Secondary hosting environment for legacy EC2 instances, S3 archival storage, and specific third-party integrations.

*Note: Microsoft Azure is currently not an officially supported platform within our production tier. Multi-cloud deployments are limited to GCP and AWS.*

## 3. Operational Responsibilities
- **Continuous Monitoring**: Proactive alerting via Google Cloud Monitoring and AWS CloudWatch.
- **Access Management**: Reviewing and approving privilege elevation requests.
- **Disaster Recovery**: Bi-annual failover testing between GCP regions.
- **Patch Management**: Monthly OS patching and Kubernetes cluster minor version upgrades.

## 4. Incident Management Overview
All production anomalies impacting service availability, data integrity, or customer experience follow the standard Incident Lifecycle:
Detection -> Triage -> Containment -> Remediation -> Post-Incident Review.
For detailed incident severity classifications and response SLAs, consult the **Production Incident Management** page.

## 5. Change Management Overview
Zero unapproved production changes are permitted. Every infrastructure modification must have an associated Request for Change (RFC) ticket approved by the Change Advisory Board (CAB) or automated compliance checks. Refer to **Change Management Procedure** for guidelines.

## 6. Monitoring Responsibilities
CloudOps monitors golden signals: Latency, Traffic, Errors, and Saturation.
- GCP Alerting Policies: Bound to PagerDuty service `GCP-Prod-Alerts`.
- AWS CloudWatch Alarms: Configured for CPU, Disk IOPS, and Synthetic HTTP checks.

## 7. Escalation Principles
- If an incident cannot be triaged within 15 minutes of acknowledgement, escalate to the secondary on-call engineer.
- For issues requiring specialized application domain knowledge, initiate cross-functional escalation as defined in the **CloudOps Escalation Matrix**.
"""
    },
    {
        "id": "1638401",
        "title": "Production Incident Management",
        "spaceKey": "AITEST",
        "version": 5,
        "lastUpdated": "2026-08-15T14:30:00Z",
        "author": "abhinav.singh@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1638401/Production+Incident+Management",
        "content": """
# Production Incident Management

## 1. Incident Severity Levels & Definitions

| Severity | Definition | Target Response SLA | Status Update Frequency |
| :--- | :--- | :--- | :--- |
| **P1 (Critical)** | Catastrophic outage; primary business revenue or customer services completely unavailable; core production database down; data loss risk. | **< 15 minutes** | Every **15 minutes** on Statuspage & Slack |
| **P2 (Major)** | Significant degradation of core service; critical functionality impaired with no viable workaround; high latency affecting >20% users. | **< 30 minutes** | Every **30 minutes** on Slack & JIRA |
| **P3 (Minor)** | Non-critical component failing; minor bug with existing workaround; low customer impact; administrative dashboard down. | **< 2 hours** | Daily or upon status shift |

## 2. Initial Response Process
1. **Acknowledge Alert**: On-call engineer must acknowledge PagerDuty page within SLA (P1: 5 mins, P2: 15 mins).
2. **Open Incident Channel**: Automatically or manually generate a dedicated Slack incident channel `#incident-YYYYMMDD-<short-name>`.
3. **Declare Roles**:
   - **Incident Commander (IC)**: Leads strategy, communications, and decision making.
   - **Technical Lead (TL)**: Drives technical diagnosis and remediation.
   - **Communications Lead (CL)**: Drafts internal updates and external status postings.
4. **Initiate War Room**: Start Google Meet video bridge linked in Slack channel topic.

## 3. Investigation Process
- Review recent deployments in GCP Cloud Build / GitHub Actions within the last 2 hours.
- Inspect golden signals in Google Cloud Monitoring (Error rate, 5xx responses, CPU/Memory saturation).
- Query Google Cloud Logging using error filters: `severity>=ERROR AND resource.type="k8s_container"`.
- If an active change or deployment caused the regression, immediately trigger the rollback procedure defined in **Change Management Procedure**.

## 4. Communication Requirements
- Post an initial broadcast to `#prod-incidents` within 10 minutes of incident declaration.
- Update the public Statuspage for P1 incidents within 15 minutes.
- Internal executive briefings must be provided by the Communications Lead every 30 minutes for P1, 60 minutes for P2.

## 5. Escalation Process
- If root cause is not identified within 30 minutes for P1 or 45 minutes for P2, the Incident Commander must invoke the **CloudOps Escalation Matrix** to engage Platform Engineering and Cloud Architecture leads.
- In case of cloud provider regional outage, notify the VP of Infrastructure immediately.

## 6. Incident Resolution
An incident is officially resolved only when:
1. Core services return to baseline error rates (<0.01% 5xx errors for 15 consecutive minutes).
2. Synthetic health checks in GCP and AWS pass without failure.
3. Verification is signed off by both the Technical Lead and the Incident Commander.

## 7. Post-Incident Review (PIR)
- A blameless Post-Incident Review meeting must be scheduled within **48 hours** for all P1 and P2 incidents.
- A completed PIR document must be published to Confluence within **5 business days**, including root cause analysis (5 Whys), action items, and preventative Jira tickets.
"""
    },
    {
        "id": "1671169",
        "title": "Change Management Procedure",
        "spaceKey": "AITEST",
        "version": 4,
        "lastUpdated": "2026-08-12T09:15:00Z",
        "author": "operations.governance@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1671169/Change+Management+Procedure",
        "content": """
# Change Management Procedure

## 1. Change Request Process (RFC)
All production environment changes must be documented via a Request for Change (RFC) ticket in Jira Service Management at least 24 hours prior to planned execution.

Types of Changes:
1. **Standard Change**: Pre-approved, low-risk, routine maintenance (e.g. routine certificate renewal, OS security patch).
2. **Normal Change**: Moderate to high-impact changes (e.g. database schema migrations, GKE node pool upgrade, firewall modifications). Requires CAB review.
3. **Emergency Change**: Unplanned changes required to resolve or mitigate an active P1 or P2 incident. Requires retrospective CAB approval within 24 hours.

## 2. Pre-Change Validation
Before executing any production change:
- Dry-run validation: Run `terraform plan` to confirm only expected resources are modified.
- Verify backup status: Ensure full snapshot or cloud database point-in-time recovery (PITR) is active and verified.
- Confirm peer review: At least two SRE / CloudOps engineers must review and approve the pull request.

## 3. Approval Requirements
- Standard Changes: Auto-approved upon CI/CD pipeline automated test pass.
- Normal Changes: Requires approval from CloudOps Lead, Security Architect, and Product Owner.
- Emergency Changes: Verbal or Slack approval by Incident Commander (IC) or on-duty SRE Lead.

## 4. Implementation Windows
- Production change window: Tuesday through Thursday between 01:00 UTC and 05:00 UTC.
- Production deployment freeze: Fridays after 12:00 UTC, weekends, and major retail holiday weeks unless an Emergency RFC is declared.

## 5. Monitoring During Rollout
During rollout execution:
- Observe canary metrics in Cloud Monitoring for 15 minutes.
- Check HTTP 5xx error rate threshold (must not exceed 0.05%).
- Verify latency p99 remains below 250ms.

## 6. Rollback Procedure
If any of the following criteria are met, the engineer must immediately initiate a rollback:
- HTTP 5xx error rate spikes above 0.5% for > 3 minutes.
- Database connection pool reaches 100% saturation.
- Unhandled application exceptions in Cloud Logging.
- P1 or P2 incident is declared as a direct consequence of the change.

**Step-by-Step Rollback Steps**:
1. Abort ongoing deployment pipeline in Cloud Build / GitLab CI.
2. In GKE / Cloud Run: Execute deployment revision rollback:
   `kubectl rollout undo deployment/<service-name> -n production` or `gcloud run services update-traffic <service-name> --to-revisions=<prev-revision>=100`.
3. If database schema was altered, execute the pre-tested down-migration script.
4. Notify the change channel `#prod-changes` and Incident Commander of rollback initiation.

## 7. Post-Change Validation
- Run automated end-to-end integration test suite against production endpoints.
- Monitor logs for 30 minutes post-rollout to ensure no lingering anomalies.

## 8. Change Closure
- Update RFC ticket status to 'Completed' or 'Rolled Back' with execution timestamp and verification logs attached.
"""
    },
    {
        "id": "1638417",
        "title": "Cloud Resource Cleanup Procedure",
        "spaceKey": "AITEST",
        "version": 2,
        "lastUpdated": "2026-07-28T16:45:00Z",
        "author": "finops@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1638417/Cloud+Resource+Cleanup+Procedure",
        "content": """
# Cloud Resource Cleanup Procedure

## 1. Resource Identification
The FinOps & CloudOps automated audit script scans GCP and AWS environments weekly for idle and orphaned assets:
- **Unattached Disks**: Persistent disks in GCP or EBS volumes in AWS unattached for > 7 days.
- **Idle IP Addresses**: Static external IP addresses not assigned to any forwarding rule or instance.
- **Stopped VM Instances**: Instances in stopped/terminated state for > 30 days.
- **Orphaned Snapshots**: Manual disk snapshots older than 90 days without retention tag.
- **Dangling Load Balancers**: Load balancers with 0 backend instances or 0 traffic for 14 days.

## 2. Owner Validation
- Every cloud resource must contain the mandatory labels: `owner`, `cost-center`, and `environment`.
- When an idle asset is detected, the automated notification bot notifies the designated owner via Slack and Email.
- If an asset lacks an owner label, the notification is routed to the departmental manager.

## 3. Business Confirmation
- The resource owner has **7 business days** to confirm whether the asset is required or can be decommissioned.
- If the owner confirms decommissioning or does not respond within 7 business days, the asset transitions to the scheduled shutdown phase.

## 4. Approval Requirements
- Decommissioning non-production assets: Approval from Engineering Team Lead.
- Decommissioning production or staging assets: Requires RFC ticket approved by CloudOps Lead.

## 5. Shutdown Procedure
1. Tag the resource with `status=pending-deletion` and `scheduled-deletion-date=YYYY-MM-DD`.
2. Stop the VM instance or detach associated networking components.
3. Keep the asset in a stopped state for **14 calendar days** to allow rapid recovery if unexpected dependencies emerge.

## 6. Decommissioning & Deletion
1. Take a final snapshot of the disk or export data to cold-line GCS / AWS Glacier storage tagged with a 1-year retention policy.
2. Terminate the VM instance, delete unattached persistent disks, and release external static IP addresses.
3. Remove associated DNS entries in Cloud DNS or Route 53.

## 7. Validation & Audit Evidence
- Confirm resource termination via Google Cloud Console or AWS CLI.
- Record deleted resource details (Resource ID, Cost savings per month, Approval ticket) in the FinOps Monthly Decommissioning Report.
"""
    },
    {
        "id": "1572872",
        "title": "GCP Troubleshooting Runbook",
        "spaceKey": "AITEST",
        "version": 6,
        "lastUpdated": "2026-08-20T11:20:00Z",
        "author": "gcp.sre@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1572872/GCP+Troubleshooting+Runbook",
        "content": """
# GCP Troubleshooting Runbook

## 1. Google Kubernetes Engine (GKE) Troubleshooting
GKE hosts all microservices in production. Follow this prioritized sequence for GKE issues:

### A. Pod CrashLoopBackOff or Error
1. Check pod status:
   `kubectl get pods -n <namespace> -o wide`
2. Inspect pod event history:
   `kubectl describe pod <pod-name> -n <namespace>`
   Look for OOMKilled (Exit Code 137), failed liveness/readiness probes, or missing Secret/ConfigMap mounts.
3. View pod logs:
   `kubectl logs <pod-name> -n <namespace> --previous --tail=100`

### B. ImagePullBackOff or ErrImagePull
- Verify Artifact Registry permissions: ensure the GKE node Service Account has `roles/artifactregistry.reader`.
- Confirm image tag exists in Artifact Registry:
  `gcloud artifacts docker images list us-central1-docker.pkg.dev/<project-id>/<repo-name>`

### C. Node Pressure / Pod Evictions
- Check node conditions: `kubectl get nodes` (look for `MemoryPressure`, `DiskPressure`).
- If nodes are saturated, verify GKE Cluster Autoscaler is enabled and maximum node limits are not exceeded:
  `gcloud container clusters describe <cluster-name> --region <region> --format="value(nodePools.autoscaling)"`

## 2. Cloud Run Troubleshooting
For Cloud Run service latency or 5xx errors:
1. **504 Gateway Timeout**:
   - Check request timeout setting in Cloud Run service configuration (default 300s).
   - Inspect container logs in Cloud Logging: filter `resource.type="cloud_run_revision" AND severity>=ERROR`.
2. **Container Startup Failure (Container failed to start)**:
   - Check if the container is listening on the expected port (environment variable `$PORT`, default 8080).
   - Ensure container boots within 240 seconds.
3. **Concurrency Saturation**:
   - Check maximum instances and container concurrency settings. Increase `max-instances` if traffic spikes.

## 3. Compute Engine (VM) Troubleshooting
1. **Unresponsive VM Instance**:
   - Check serial console output:
     `gcloud compute instances get-serial-port-output <instance-name> --zone <zone>`
   - Inspect OS kernel panics or disk full errors (`No space left on device`).
2. **SSH Connection Refused**:
   - Verify VPC firewall rule `allow-ssh` (TCP 22) exists and targets the VM's network tag.
   - Use IAP (Identity-Aware Proxy) tunneling:
     `gcloud compute ssh <instance-name> --tunnel-through-iap --zone <zone>`

## 4. IAM & Permission Denied Troubleshooting
1. Check audit logs in Cloud Logging:
   `protoPayload.status.code=7` (PERMISSION_DENIED)
2. Inspect caller identity: verify if request used user OAuth token or Service Account.
3. Check role bindings:
   `gcloud projects get-iam-policy <project-id> --flatten="bindings[].members" --filter="bindings.members:<identity>"`

## 5. Networking & VPC Checks
- Verify Cloud NAT allocation: check for `k8s-node-nat` port exhaustion in Cloud Monitoring.
- Verify VPC Peering and Cloud Interconnect BGP status.

## 6. Escalation Criteria
- If GKE cluster control plane is unresponsive or Cloud Run reports GCP infrastructure 500 errors, immediately escalate to Google Cloud Premium Support and page the GCP Platform Lead via the **CloudOps Escalation Matrix**.
"""
    },
    {
        "id": "1540114",
        "title": "AWS Troubleshooting Runbook",
        "spaceKey": "AITEST",
        "version": 3,
        "lastUpdated": "2026-08-01T15:00:00Z",
        "author": "aws.sre@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1540114/AWS+Troubleshooting+Runbook",
        "content": """
# AWS Troubleshooting Runbook

## 1. Amazon EC2 Troubleshooting
### A. Status Check Failures
1. **System Status Check Failure (0/2 or 1/2 passing - AWS hardware issue)**:
   - Perform a Stop/Start cycle on the instance via AWS CLI to migrate to a healthy physical host:
     `aws ec2 stop-instances --instance-ids <instance-id>`
     `aws ec2 start-instances --instance-ids <instance-id>`
   *Do NOT use reboot, as reboot keeps the instance on the same underlying hypervisor.*
2. **Instance Status Check Failure (OS/kernel/software failure)**:
   - Review instance system screenshot and system log:
     `aws ec2 get-console-output --instance-id <instance-id>`
   - Inspect root volume filesystem corruption or networking configuration errors.

### B. Unresponsive or Inaccessible EC2
- Use AWS Systems Manager (SSM) Session Manager to establish a shell without opening inbound port 22:
  `aws ssm start-session --target <instance-id>`
- Verify Security Group rules allow required traffic from ALB or internal CIDR blocks.

## 2. Amazon EKS Troubleshooting
- Check node status: `kubectl get nodes`
- If CoreDNS pods are in CrashLoopBackOff:
  Verify cluster VPC CNI plugin version and IP address availability in private subnets.
- Check AWS IAM authenticator mappings in `aws-auth` ConfigMap.

## 3. Amazon S3 Troubleshooting
1. **403 Forbidden / Access Denied**:
   - Evaluate multi-layer permissions: Bucket Policy, IAM Policy, S3 Block Public Access, and AWS KMS Key Policy.
   - If KMS encrypted, caller must have `kms:Decrypt` and `kms:GenerateDataKey` permissions.

## 4. CloudWatch Alarm Triage
- When CloudWatch alarm triggers:
  1. Inspect metric graph over 3-hour window.
  2. Correlate with AWS CloudTrail events for unexpected API calls or configuration modifications.

## 5. Escalation Criteria
- For unresolved EC2 underlying hardware outages or AWS account-level service limits, escalate to AWS Enterprise Support and engage the Secondary AWS On-Call via **CloudOps Escalation Matrix**.
"""
    },
    {
        "id": "1572888",
        "title": "CloudOps Escalation Matrix",
        "spaceKey": "AITEST",
        "version": 4,
        "lastUpdated": "2026-08-18T17:10:00Z",
        "author": "oncall.director@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1572888/CloudOps+Escalation+Matrix",
        "content": """
# CloudOps Escalation Matrix

## 1. Escalation Matrix by Issue Type & Severity

| Issue Domain | Severity | Primary On-Call Team | Secondary Escalation Team | Escalation SLA |
| :--- | :--- | :--- | :--- | :--- |
| **GCP Infrastructure (GKE, Cloud Run, IAM)** | P1 | CloudOps On-Call SRE (PagerDuty: `gcp-sre-p1`) | Principal SRE / Cloud Architect | **15 minutes** |
| **GCP Infrastructure** | P2 | CloudOps On-Call SRE | Senior CloudOps Engineer | **30 minutes** |
| **AWS Infrastructure (EC2, EKS, S3)** | P1 / P2 | AWS On-Call SRE (PagerDuty: `aws-sre-p1`) | Lead Infrastructure Architect | **15m (P1) / 30m (P2)** |
| **Networking / Cloud Interconnect / DNS** | P1 / P2 | Network Operations (NetOps) | Principal Network Architect | **20 minutes** |
| **Database Outage (Cloud SQL, BigQuery)** | P1 | Database Operations (DBA On-Call) | Lead Data Architect | **15 minutes** |
| **Security Incident / Compromised Credential** | P1 | Security Operations Center (SecOps) | Chief Information Security Officer (CISO) | **Immediate (< 10 mins)** |
| **Cloud Provider Regional Outage** | P1 | CloudOps Incident Commander | VP of Infrastructure / Google/AWS TAM | **15 minutes** |

## 2. Escalation Paths & Contact Information
- **PagerDuty Roster**: [https://cloudops.pagerduty.com](https://cloudops.pagerduty.com)
- **Emergency War Room Bridge**: Google Meet `meet.google.com/ops-incident-war-room`
- **Internal Slack Channels**:
  - `#cloudops-escalation`: Urgent escalation requests.
  - `#prod-incidents`: Public incident broadcasting.
  - `#incident-command`: Incident Commander private coordinator channel.
- **On-Call Escalation Hotline**: +1 (800) 555-OPS1 (Pin: 8477)

## 3. Required Information Before Escalating
When paging a secondary team or specialist, the initiating engineer must supply:
1. **Incident ID & Severity** (e.g. `INC-8492 - P1`).
2. **Impacted Service & Cloud Platform** (e.g. `Payment-Gateway on GCP us-central1 GKE`).
3. **Current Symptoms & Error Logs** (Relevant Cloud Logging query link and 5xx graph).
4. **Actions Already Attempted** (e.g., "Attempted pod restart and revision rollback, failed with error X").
5. **Active War Room Link**.

## 4. Executive & Stakeholder Notification Rules
- For P1 incidents exceeding 30 minutes duration, the Incident Commander must notify:
  - VP of Engineering
  - Head of Customer Support
  - VP of Product
"""
    },
    {
        "id": "1703937",
        "title": "Standard Operating Procedures",
        "spaceKey": "AITEST",
        "version": 3,
        "lastUpdated": "2026-08-05T13:40:00Z",
        "author": "operations.governance@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1703937/Standard+Operating+Procedures",
        "content": """
# Standard Operating Procedures (SOPs)

This document contains standard operating procedures that intentionally cross-reference and summarize critical operational policies. When handling production events, verify specifics against individual authoritative runbooks.

## SOP-01: Production Outage Fast-Response & Pager Acknowledgement
- When an automated alert triggers via PagerDuty for a production service, the on-call engineer has **5 minutes** (P1) or **15 minutes** (P2) to acknowledge the alert.
- If unacknowledged within SLA, the pager auto-escalates to the secondary on-call engineer as stipulated in the **CloudOps Escalation Matrix**.
- Immediately open a dedicated incident Slack channel and post the initial assessment within 10 minutes, adhering to the communication protocols in **Production Incident Management**.

## SOP-02: Emergency Rollback Execution for Failed Releases
- When a software release or configuration change introduces high error rates (>0.5% 5xx) or service unavailability:
  1. Do NOT attempt to "hotfix forward" during an active P1/P2 incident.
  2. Initiate an immediate rollback to the last known stable revision.
  3. For GKE: `kubectl rollout undo deployment/<service-name> -n production`.
  4. For Cloud Run: Route 100% of traffic back to the previous healthy revision using `gcloud run services update-traffic`.
  5. Detailed rollback gates and post-rollback verification steps are governed by the **Change Management Procedure**.

## SOP-03: Quarterly Unused Cloud Asset Purge
- Every quarter, CloudOps executes a comprehensive cloud cleanup to eliminate waste and optimize cloud expenditure.
- Assets targeted include: unattached persistent disks (>7 days), idle public IPs, stopped VMs (>30 days), and unreferenced snapshots.
- All cleanup activities must follow the 7-day notification window, snapshot archiving, and audit logging mandated in the **Cloud Resource Cleanup Procedure**.

## SOP-04: Cross-Team Incident Notification Bridge
- For multi-service outages impacting both GCP and AWS layers:
  1. The Incident Commander joins the master Google Meet bridge.
  2. Ping the respective domain leads via `#cloudops-escalation`.
  3. Ensure both GCP SRE and AWS SRE leads are actively troubleshooting their respective runbooks (**GCP Troubleshooting Runbook** and **AWS Troubleshooting Runbook**).
"""
    },
    {
        "id": "1671185",
        "title": "Disaster Recovery and Multi-Region Failover Guide",
        "spaceKey": "AITEST",
        "version": 2,
        "lastUpdated": "2026-08-25T11:00:00Z",
        "author": "disaster.recovery@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1671185/Disaster+Recovery+and+Multi-Region+Failover+Guide",
        "content": """
# Disaster Recovery and Multi-Region Failover Guide

## 1. Objectives and Recovery Metrics
- **Recovery Point Objective (RPO)**: <= 5 minutes for core transactional data.
- **Recovery Time Objective (RTO)**: <= 30 minutes for full application traffic restoration.

## 2. Multi-Region Architecture
- **Primary Region**: GCP `us-central1` (Iowa).
- **Secondary Failover Region**: GCP `us-east4` (Northern Virginia).
- Continuous cross-region replication is maintained via Cloud Spanner multi-region instance configuration and asynchronous Cloud SQL cross-region read replicas.

## 3. Disaster Declaration Criteria
A regional failover is declared by the Incident Commander only under:
1. Complete GCP regional outage confirmed via Google Cloud Status Dashboard or TAM escalation exceeding 20 minutes duration.
2. Catastrophic data center connectivity failure impacting all available zones in `us-central1`.

## 4. Step-by-Step Regional Failover Procedure
1. **Promote Read Replicas**:
   Promote the secondary database replica in `us-east4` to primary:
   `gcloud sql instances promote-replica prod-db-replica-us-east4`
2. **Scale Secondary GKE Cluster**:
   Scale the standby GKE cluster worker node pool in `us-east4`:
   `gcloud container clusters resize prod-cluster-us-east4 --node-pool=primary-pool --num-nodes=12 --region=us-east4`
3. **Shift Global Cloud Load Balancing (GCLB) Traffic**:
   Update Cloud Armor / GCLB backend service weights to redirect 100% of ingress traffic to `us-east4`.
4. **DNS Failover Confirmation**:
   Verify global anycast VIP routing and test synthetic availability from 5 global edge locations.
"""
    },
    {
        "id": "1736705",
        "title": "Cloud Security and Vulnerability Remediation SLA",
        "spaceKey": "AITEST",
        "version": 3,
        "lastUpdated": "2026-08-28T09:30:00Z",
        "author": "secops@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1736705/Cloud+Security+and+Vulnerability+Remediation+SLA",
        "content": """
# Cloud Security and Vulnerability Remediation SLA

## 1. Vulnerability Classification & SLAs

| Severity Rating | CVSS Base Score | Maximum Remediation SLA | Required Action |
| :--- | :--- | :--- | :--- |
| **Critical** | 9.0 - 10.0 | **24 hours** | Immediate emergency patch, hotfix deployment, or port isolation |
| **High** | 7.0 - 8.9 | **7 business days** | Normal RFC deployment with security verification |
| **Medium** | 4.0 - 6.9 | **30 calendar days** | Scheduled into regular monthly release cycle |
| **Low** | 0.1 - 3.9 | **90 calendar days** | Backlog hygiene review |

## 2. Security Incident Response
- Any compromised service account credential or leaked API key must be revoked **immediately (< 10 minutes)**.
- Trigger automated credential rotation via Secret Manager.
- Notify SecOps via PagerDuty service `secops-p1` and open an urgent security war room.
"""
    },
    {
        "id": "1638433",
        "title": "Database Operations Runbook (Cloud SQL and Spanner)",
        "spaceKey": "AITEST",
        "version": 4,
        "lastUpdated": "2026-08-30T14:15:00Z",
        "author": "dba.team@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1638433/Database+Operations+Runbook+Cloud+SQL+and+Spanner",
        "content": """
# Database Operations Runbook (Cloud SQL and Spanner)

## 1. Cloud SQL Connection Pool Exhaustion
When database connections reach > 85% of `max_connections`:
1. Check active client connections:
   `SELECT count(*), state, client_addr FROM pg_stat_activity GROUP BY state, client_addr;`
2. Terminate idle-in-transaction connections older than 5 minutes:
   `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction' AND state_change < current_timestamp - INTERVAL '5 minutes';`
3. If connection churn originates from GKE microservices, verify PgBouncer connection pooling sidecar deployment.

## 2. Point-In-Time Recovery (PITR) Execution
1. Identify target restoration timestamp from Cloud Logging right before data corruption occurred.
2. Execute PITR clone command:
   `gcloud sql instances clone <source-instance> <restored-instance> --point-in-time="YYYY-MM-DDTHH:MM:SS.000Z"`
3. Validate table integrity before switching application connection strings.
"""
    },
    {
        "id": "1638449",
        "title": "Kubernetes Ingress and Cloud Load Balancing Guide",
        "spaceKey": "AITEST",
        "version": 2,
        "lastUpdated": "2026-09-01T16:00:00Z",
        "author": "platform.networking@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1638449/Kubernetes+Ingress+and+Cloud+Load+Balancing+Guide",
        "content": """
# Kubernetes Ingress and Cloud Load Balancing Guide

## 1. GKE Ingress Architecture
Production workloads expose HTTPS endpoints through Google Cloud External Application Load Balancers integrated with GKE Ingress controllers via Google-managed SSL certificates and Cloud Armor security policies.

## 2. SSL Certificate Troubleshooting
- Check managed certificate status:
  `kubectl describe managedcertificate <cert-name> -n production`
- If certificate status is `ProvisioningFailed` or stuck in `Provisioning`:
  Verify Cloud DNS A-record points directly to the Ingress static IP and no CAA (Certificate Authority Authorization) records block Google Trust Services.

## 3. Cloud Armor DDoS Mitigation
- When layer-7 HTTP flood is detected:
  Apply rate-limiting rule in Cloud Armor security policy:
  `gcloud compute security-policies rules update 1000 --security-policy=prod-armor-policy --rate-limit-threshold-count=500 --rate-limit-threshold-interval-sec=60 --conform-action=allow --exceed-action=deny-429`
"""
    },
    {
        "id": "1572904",
        "title": "Cost Optimization and FinOps Best Practices",
        "spaceKey": "AITEST",
        "version": 2,
        "lastUpdated": "2026-09-02T10:45:00Z",
        "author": "finops@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1572904/Cost+Optimization+and+FinOps+Best+Practices",
        "content": """
# Cost Optimization and FinOps Best Practices

## 1. Committed Use Discounts (CUD)
- 1-year and 3-year compute and database commitments are purchased to cover baseline 24/7 workloads, providing up to 57% savings over on-demand rates.
- Commitment coverage target: maintain between 75% and 85% compute commitment coverage.

## 2. Spot / Preemptible VM Usage
- Non-critical batch processing, CI/CD runners, and staging environments must exclusively utilize Spot VMs.
- GKE node pools running stateless batch jobs must have `spot=true` taint configured.

## 3. Storage Tiering Lifecycle Policies
- Configure GCS bucket lifecycle rules to transition objects to Nearline after 30 days, Coldline after 90 days, and Archive after 365 days.
"""
    },
    {
        "id": "1540130",
        "title": "Zero Trust Access and BeyondCorp Enterprise Runbook",
        "spaceKey": "AITEST",
        "version": 2,
        "lastUpdated": "2026-09-03T13:20:00Z",
        "author": "iam.security@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1540130/Zero+Trust+Access+and+BeyondCorp+Enterprise+Runbook",
        "content": """
# Zero Trust Access and BeyondCorp Enterprise Runbook

## 1. Identity-Aware Proxy (IAP) Policies
- All internal administrative portals, Grafana dashboards, and staging environments are guarded by Google Cloud Identity-Aware Proxy.
- Inbound SSH/RDP access to Compute Engine VMs is permitted strictly via IAP TCP forwarding:
  `gcloud compute ssh <vm-name> --tunnel-through-iap --zone=<zone>`
- Direct public IP binding on VM instances is prohibited by organization policy constraints (`compute.vmExternalIpAccess`).

## 2. Service Account Key Governance
- Long-lived user-downloaded service account JSON keys are forbidden in production.
- Workload Identity Federation must be used for GitHub Actions, Azure DevOps, and AWS integrations to exchange short-lived OIDC tokens for Google Cloud credentials.
"""
    },
    {
        "id": "1769473",
        "title": "CI/CD Pipeline and Deployment Troubleshooting",
        "spaceKey": "AITEST",
        "version": 3,
        "lastUpdated": "2026-09-04T15:10:00Z",
        "author": "devops.enablement@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1769473/CI+CD+Pipeline+and+Deployment+Troubleshooting",
        "content": """
# CI/CD Pipeline and Deployment Troubleshooting

## 1. Cloud Build Failures
- **Build Timeout (Default 10m exceeded)**:
  Increase timeout parameter in `cloudbuild.yaml` using `timeout: 1800s`.
- **Artifact Registry Push Denied**:
  Verify Cloud Build service account (`@cloudbuild.gserviceaccount.com`) has role `roles/artifactregistry.writer`.

## 2. Canary Deployment Rollout Verification
- Canary deployments route 10% traffic to the new revision for 15 minutes.
- Automated canary analysis aborts deployment if HTTP 5xx error rate exceeds 0.1% or latency increases by > 20% compared to baseline.
"""
    },
    {
        "id": "1703953",
        "title": "Production On-Call Handoff and Shift Guidelines",
        "spaceKey": "AITEST",
        "version": 2,
        "lastUpdated": "2026-09-05T08:00:00Z",
        "author": "sre.leadership@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1703953/Production+On-Call+Handoff+and+Shift+Guidelines",
        "content": """
# Production On-Call Handoff and Shift Guidelines

## 1. Shift Schedule and Handoff Meeting
- On-call shifts rotate weekly on **Tuesdays at 10:00 UTC**.
- A mandatory 30-minute video handoff meeting occurs between the outgoing and incoming primary SREs.

## 2. Handoff Checklist
1. Review all P1, P2, and P3 alerts triggered during the preceding 7 days.
2. Review active maintenance windows or ongoing RFC emergency changes.
3. Verify PagerDuty escalation override schedules and mobile phone push notification alerts.
4. Confirm health of synthetic monitoring probes and test alert pager dispatch.
"""
    }
,
    {
        "id": "1769521",
        "title": "GCP Core Services and Architecture Deep Dive",
        "spaceKey": "AITEST",
        "version": 1,
        "lastUpdated": "2026-09-10T10:00:00Z",
        "author": "gcp.principal@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1769521/GCP+Core+Services+and+Architecture+Deep+Dive",
        "content": """
# GCP Core Services and Architecture Deep Dive

## 1. Google Cloud Core Infrastructure Overview
Google Cloud Platform (GCP) serves as the primary production hosting tier for our containerized microservices, event-driven data pipelines, and distributed databases. All production workloads are orchestrated across multi-zone regional deployments in `us-central1` (Iowa) with secondary standby capacity in `us-east4` (Northern Virginia).

## 2. Compute and Serverless Options Matrix

| Service | Architecture Type | Startup Latency | Scaling Model | High Availability SLA | Best Production Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Google Kubernetes Engine (GKE)** | Managed Kubernetes (Autopilot) | 1 - 2 minutes (node provisioning) | Horizontal Pod Autoscaler (HPA) + Cluster Autoscaler | 99.95% (Multi-Zonal) | Stateful services, high-throughput microservice mesh |
| **Cloud Run** | Managed Serverless Containers | < 250ms (warm) / 1.5s (cold) | Concurrency-based autoscaling (0 to 1000 instances) | 99.95% (Regional) | REST APIs, webhooks, asynchronous event processors |
| **Cloud Functions** | Function-as-a-Service (FaaS) | < 150ms (warm) / 1.2s (cold) | Automatic per-request scaling | 99.95% (Regional) | Event triggers, Pub/Sub transformations, cloud audit hooks |
| **Compute Engine (GCE)** | Infrastructure-as-a-Service (VMs) | 30 - 45 seconds | Managed Instance Groups (MIGs) with health checks | 99.99% (Multi-Zone) | Legacy monoliths, custom kernel extensions, high-IOPS workloads |

## 3. Database and Storage Ecosystem
- **Cloud Spanner**: Globally distributed, externally consistent (ACID) relational database delivering 99.999% availability for multi-region instances with automatic synchronous sharding.
- **Cloud SQL (PostgreSQL / MySQL)**: Fully managed relational database with automated multi-zone failover, read replicas across regions, and point-in-time recovery (PITR) up to 35 days.
- **BigQuery**: Serverless, multi-cloud enterprise data warehouse with built-in machine learning (BQML) and BigQuery Omni for cross-cloud querying.
- **Cloud Storage (GCS)**: Strongly consistent object storage categorized into Standard (frequent access), Nearline (30-day cold), Coldline (90-day cold), and Archive (365-day cold).

## 4. End-to-End GCP Traffic Architecture
```
[External Users / Clients]
          │
          ▼ (Global Anycast IPv4 / IPv6)
[Cloud Armor Security Perimeter (OWASP WAF + DDoS Filtering)]
          │
          ▼
[Global External Application Load Balancer (GCLB)]
    ├───> [Cloud CDN Edge Points of Presence]
    │
    ├───> [Production GKE Autopilot Cluster (Private Nodes)]
    │         │
    │         ├───> [Cloud Spanner Multi-Region Cluster]
    │         └───> [Cloud SQL HA Primary + Read Replicas]
    │
    └───> [Cloud Run Microservices]
              │
              └───> [Cloud Pub/Sub Topics] ───> [BigQuery Analytics Engine]
```

## 5. Reliability and Production Readiness Best Practices
- **Regional Deployment**: Never deploy single-zone workloads in production. All GKE clusters must be regional.
- **Resource Quotas**: Pre-allocate Compute Engine vCPU quotas and static external IP addresses 30 days before major traffic events.
- **Graceful Shutdown**: Implement SIGTERM handling with 30-second graceful termination windows in all containerized services.
"""
    },
    {
        "id": "1802250",
        "title": "AWS Enterprise Networking Master Reference",
        "spaceKey": "AITEST",
        "version": 1,
        "lastUpdated": "2026-09-11T12:30:00Z",
        "author": "aws.networking@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1802250/AWS+Enterprise+Networking+Master+Reference",
        "content": """
# AWS Enterprise Networking Master Reference

## 1. Enterprise VPC Architecture and Subnet Segmentation
Our AWS infrastructure operates within primary region `us-east-1` with dedicated disaster recovery in `us-east-2`. Every production Virtual Private Cloud (VPC) adheres to strict multi-Availability Zone (Multi-AZ) segmentation across three distinct tiers:

| Tier Name | CIDR Block Range | Internet Access Route | Subnet Purpose |
| :--- | :--- | :--- | :--- |
| **Public Tier** | `10.200.1.0/24` (AZ-a), `10.200.2.0/24` (AZ-b) | Direct route to Internet Gateway (IGW) | Application Load Balancers, NAT Gateways, Bastion proxies |
| **Private App Tier** | `10.200.10.0/24` (AZ-a), `10.200.20.0/24` (AZ-b) | Egress via AZ-specific NAT Gateway | EKS worker nodes, EC2 compute instances, microservices |
| **Isolated Data Tier** | `10.200.30.0/24` (AZ-a), `10.200.40.0/24` (AZ-b) | No internet route (strict VPC internal) | Amazon RDS PostgreSQL, DynamoDB VPC endpoints, ElastiCache |

## 2. AWS Transit Gateway (TGW) Hub-and-Spoke Topology
- A central AWS Transit Gateway acts as a regional network transit hub connecting our Production VPC, Staging VPC, and Shared Services VPC.
- Cross-account VPC attachments utilize AWS Resource Access Manager (RAM).
- Route Table Isolation: Production VPC cannot route packets directly to Development or Staging VPCs, strictly enforcing PCI-DSS and SOC-2 isolation boundaries.

## 3. Elastic Load Balancing (ELB) Architecture

| Load Balancer Type | OSI Layer | Protocol Support | Latency Profile | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Application Load Balancer (ALB)** | Layer 7 | HTTP, HTTPS, gRPC, WebSockets | ~4 - 8 ms | Path-based routing, containerized microservices, TLS offloading |
| **Network Load Balancer (NLB)** | Layer 4 | TCP, UDP, TLS | Ultra-low (< 1 ms) | Millions of RPS, static Elastic IP requirement, gaming protocols |
| **Gateway Load Balancer (GWLB)** | Layer 3 | IP packets (GENEVE encapsulation) | Transparent bump-in-wire | Third-party virtual firewall inspection appliances |

## 4. Security Groups vs. Network Access Control Lists (NACLs)
- **Security Groups (Stateful)**: Applied at the individual Elastic Network Interface (ENI) level. Inbound rules automatically permit return traffic regardless of outbound rules. Default: deny all inbound, allow all outbound.
- **Network ACLs (Stateless)**: Applied at the subnet boundary. Both inbound and outbound rules must explicitly permit traffic using numeric priority evaluations (100 - 32766).

## 5. AWS PrivateLink and Direct Connect
- **AWS PrivateLink**: Provides private, secure connectivity to AWS services (S3, Secrets Manager, CloudWatch) without routing traffic through public NAT Gateways, eliminating data transfer costs and internet exposure.
- **AWS Direct Connect (DX)**: 10 Gbps dedicated fiber cross-connect establishing private, deterministic bandwidth from corporate colocation facilities directly into AWS VPCs.
"""
    },
    {
        "id": "1638499",
        "title": "Multi-Cloud Hybrid Mesh (GCP and AWS Interconnect)",
        "spaceKey": "AITEST",
        "version": 1,
        "lastUpdated": "2026-09-12T14:00:00Z",
        "author": "hybrid.mesh@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1638499/Multi-Cloud+Hybrid+Mesh+GCP+and+AWS+Interconnect",
        "content": """
# Multi-Cloud Hybrid Mesh (GCP and AWS Interconnect)

## 1. High-Availability Cross-Cloud Connectivity Overview
To deliver zero-downtime cross-cloud failover, Google Cloud Platform (`us-central1`) and Amazon Web Services (`us-east-1`) are interconnected via a redundant, fault-tolerant **High Availability (HA) IPsec VPN Mesh** configured with Border Gateway Protocol (BGP) dynamic routing.

```
       ┌────────────────────────┐              ┌────────────────────────┐
       │   Google Cloud VPC     │              │     AWS Transit Hub    │
       │ (CIDR: 10.100.0.0/16)  │              │ (CIDR: 10.200.0.0/16)  │
       │    GCP Cloud Router    │              │   AWS Transit Gateway  │
       │      (ASN: 65001)      │              │      (ASN: 65002)      │
       └───────────┬────────────┘              └───────────┬────────────┘
                   │                                       │
        ┌──────────┴───────────────────────────────────────┴──────────┐
        │       4-Tunnel Dual-Redundant Encrypted IPsec Mesh          │
        │                                                             │
        │  Tunnel 1: Primary us-central1 <──> us-east-1a (Active)     │
        │  Tunnel 2: Primary us-central1 <──> us-east-1b (Active)     │
        │  Tunnel 3: Standby us-east4    <──> us-east-2a (Hot-Standby)│
        │  Tunnel 4: Standby us-east4    <──> us-east-2b (Hot-Standby)│
        └─────────────────────────────────────────────────────────────┘
```

## 2. BGP Routing and SLA Metrics
- **Autonomous System Numbers (ASNs)**: Google Cloud Router uses ASN `65001`; AWS Transit Gateway uses ASN `65002`.
- **BGP Keepalive Timers**: Keepalive = 3 seconds, Holddown Timer = 9 seconds. This enables sub-10 second automated dead-peer detection and route convergence.
- **Round-Trip Latency (RTT)**: Under normal operating conditions, cross-cloud latency between GCP Iowa and AWS N. Virginia averages **14ms - 18ms**.
- **Bandwidth Capacity**: Up to 3.0 Gbps per tunnel pair (total 6.0 Gbps aggregated throughput with Equal-Cost Multi-Path [ECMP] routing).

## 3. Cross-Cloud IP Address Allocation Plan
To prevent IP routing conflicts, the multi-cloud network adheres to non-overlapping RFC 1918 CIDRs:
- **GCP Production Virtual Private Cloud**: `10.100.0.0/16`
- **AWS Production Virtual Private Cloud**: `10.200.0.0/16`
- **VPN Point-to-Point Transit Subnets**: `169.254.10.0/30` through `169.254.10.12/30`

## 4. Multi-Cloud DNS Resolution
- **Google Cloud DNS Private Forwarding Zones**: Automatically forwards all queries for `*.aws.cloudops.internal` to the AWS Route 53 Inbound Resolver endpoint IP (`10.200.1.50`).
- **AWS Route 53 Outbound Resolver Rules**: Forwards all queries for `*.gcp.cloudops.internal` to the Google Cloud DNS Inbound Forwarding IP (`10.100.1.50`).

## 5. Troubleshooting Interconnect Degradation
1. **Check GCP Tunnel Status**:
   `gcloud compute vpn-tunnels list --region=us-central1`
   Confirm tunnel state is `ESTABLISHED` and BGP peer state is `PEER_UP`.
2. **Check AWS VPN Connection State**:
   `aws ec2 describe-vpn-connections --query "VpnConnections[*].VgwTelemetry"`
   Ensure telemetry status indicates `UP` with accepted route count > 0.
3. **Trace Route Verification**:
   `traceroute -T -p 443 10.200.10.15` (Verify path terminates over IPsec interface).
"""
    },
    {
        "id": "1507331",
        "title": "Google Cloud VPC and Security Perimeter Architecture",
        "spaceKey": "AITEST",
        "version": 1,
        "lastUpdated": "2026-09-13T16:00:00Z",
        "author": "gcp.secops@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1507331/Google+Cloud+VPC+and+Security+Perimeter+Architecture",
        "content": """
# Google Cloud VPC and Security Perimeter Architecture

## 1. Shared VPC Host and Service Project Governance
Our Google Cloud enterprise network is centrally managed via a **Shared VPC** architecture:
- **Host Project (`host-net-prod`)**: Central network administration project owning the VPC, subnets, firewall rules, Cloud NAT gateways, and Interconnect attachments.
- **Service Projects**: Application projects (`svc-microservices-prod`, `svc-analytics-prod`) attach their VM instances and GKE clusters to the Shared VPC subnets, preventing decentralized shadow networking.

## 2. VPC Service Controls (VPSC) Perimeter
To prevent catastrophic insider threat and data exfiltration, sensitive managed services are enclosed within an enforced VPC Service Controls perimeter (`perimeter-prod-data`):
- Protected Services: Cloud Storage (GCS), BigQuery, Cloud SQL, Secret Manager, Vertex AI.
- Ingress Rules: Permit access strictly from authorized corporate CIDRs via BeyondCorp Identity-Aware Proxy.
- Egress Rules: Strictly disallow copying data from internal GCS buckets to external personal Google accounts.

## 3. Cloud Armor Enterprise WAF Policies

| Security Policy Rule | Priority | Action | Description |
| :--- | :--- | :--- | :--- |
| **IP Denylist / Geofence** | 1000 | DENY (403) | Block sanctioned geographic origins and threat intelligence malicious IPs |
| **OWASP ModSecurity Core Rule Set** | 2000 | DENY (400) | Preconfigured rules blocking SQL Injection (SQLi) and Cross-Site Scripting (XSS) |
| **Adaptive Rate Limiting** | 3000 | RATE_BASED_BAN | Max 500 requests per minute per client IP; bans abusive clients for 15 minutes |
| **Default Allow Fallback** | 2147483647 | ALLOW | Permit standard sanitized traffic to reach application load balancer targets |

## 4. Cloud NAT and Private Google Access
- **Private Google Access**: Enabled on all production subnets. Compute Engine instances and GKE pods without public IPs communicate with Google APIs (e.g., `storage.googleapis.com`) entirely via internal Google routing.
- **Cloud NAT**: Provides high-throughput outbound internet connectivity for OS package updates without exposing workloads to inbound internet scans. Minimum ports per VM instance: 256; Idle connection timeout: 1200 seconds.
"""
    },
    {
        "id": "1703993",
        "title": "Multi-Cloud Data Pipeline and Analytics Architecture",
        "spaceKey": "AITEST",
        "version": 1,
        "lastUpdated": "2026-09-14T09:00:00Z",
        "author": "data.platform@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1703993/Multi-Cloud+Data+Pipeline+and+Analytics+Architecture",
        "content": """
# Multi-Cloud Data Pipeline and Analytics Architecture

## 1. Unified Multi-Cloud Analytics Mesh Overview
Our enterprise data platform ingests, processes, and analyzes operational telemetry and transaction streams across both Google Cloud and Amazon Web Services without incurring excessive cross-cloud data egress fees.

## 2. BigQuery Omni Cross-Cloud Data Analytics
- **BigQuery Omni** enables our data engineering team to query Parquet and ORC datasets stored directly in **Amazon S3** (`us-east-1`) using standard GoogleSQL syntax.
- Queries execute on managed Google-operated compute infrastructure co-located within the AWS region, returning only aggregated query results back to GCP, eliminating petabyte-scale data transfer costs.

## 3. Event Bus Bridging (Google Cloud Pub/Sub and AWS Kinesis)
- **Primary Event Backbone**: Google Cloud Pub/Sub handles 50,000+ events/sec with guaranteed at-least-once delivery and automated dead-letter topic (DLT) routing.
- **Cross-Cloud Event Replicator**: Apache Kafka MirrorMaker 2 running on GKE replicates critical audit logs and inventory mutations to AWS Amazon Kinesis data streams for backup archival.

## 4. Storage Transfer Service (STS) Automated Sync
- Daily automated sync jobs replicate analytical raw logs from AWS S3 to Google Cloud Storage (GCS) Nearline storage tier.
- Synchronization utilizes parallel multipart transfers with MD5 and CRC32C checksum validation to ensure 100% data fidelity.
"""
    },
    {
        "id": "1638516",
        "title": "Multi-Cloud IAM and Federated Zero-Trust Security",
        "spaceKey": "AITEST",
        "version": 1,
        "lastUpdated": "2026-09-14T11:30:00Z",
        "author": "iam.security@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1638516/Multi-Cloud+IAM+and+Federated+Zero-Trust+Security",
        "content": """
# Multi-Cloud IAM and Federated Zero-Trust Security

## 1. Workload Identity Federation (WIF) Architecture
Static, downloadable service account JSON keys are strictly forbidden across production environments. To authenticate AWS workloads with GCP services:
1. An AWS Lambda function or EKS pod assumes an AWS IAM Role with temporary AWS STS credentials.
2. The workload sends a cryptographically signed AWS `GetCallerIdentity` token request to Google Cloud Security Token Service (STS).
3. Google Cloud STS validates the signature against AWS cryptographic certificates, issuing a short-lived (60-minute) GCP federated access token.
4. The token grants precise, least-privilege access to target GCP resources (e.g., Secret Manager, BigQuery).

## 2. Cross-Cloud Role and Permission Mapping Matrix

| Operational Persona | Google Cloud IAM Role Binding | AWS IAM Policy Binding | Access Scope |
| :--- | :--- | :--- | :--- |
| **CloudOps Primary SRE** | `roles/viewer` + `roles/monitoring.editor` + `roles/container.developer` | `AmazonEC2ReadOnlyAccess` + `CloudWatchFullAccess` | Production monitoring, pod debugging, log triage |
| **Incident Commander** | `roles/resourcemanager.organizationAdmin` (Break-Glass PIM) | `AdministratorAccess` (AWS IAM Identity Center Break-Glass) | Emergency outage remediation (requires dual authorization) |
| **CI/CD Pipeline Service** | `roles/artifactregistry.writer` + `roles/cloudbuild.builds.editor` | `AmazonEC2ContainerRegistryPowerUser` | Building, scanning, and pushing signed container images |

## 3. BeyondCorp Enterprise Zero-Trust Endpoint Protection
- Administrative access to internal bastion hosts, Grafana clusters, and Kubernetes APIs requires Google Cloud Identity-Aware Proxy (IAP).
- Context-Aware Access policies enforce device compliance checks: corporate managed device certificate, disk encryption active, and geolocation origin within approved jurisdictions.
"""
    },
    {
        "id": "1572922",
        "title": "Multi-Cloud Observability, Telemetry, and Monitoring Mesh",
        "spaceKey": "AITEST",
        "version": 1,
        "lastUpdated": "2026-09-14T14:45:00Z",
        "author": "observability.lead@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1572922/Multi-Cloud+Observability+Telemetry+and+Monitoring+Mesh",
        "content": """
# Multi-Cloud Observability, Telemetry, and Monitoring Mesh

## 1. Unified Multi-Cloud Monitoring Architecture
Our SRE organization maintains a single-pane-of-glass observability platform aggregating metrics, distributed traces, and log telemetry across Google Cloud Platform and Amazon Web Services.

## 2. OpenTelemetry (OTel) Distributed Tracing
- OpenTelemetry Collector DaemonSets run across both GCP GKE and AWS EKS clusters.
- All microservices instrumented with the OTel SDK propagate W3C `traceparent` headers across HTTP and gRPC calls, providing end-to-end distributed latency waterfalls across cloud boundaries.

## 3. Golden Signals Monitoring Thresholds

| Golden Signal | Monitored Metric | Critical Alert Threshold (P1/P2) | Automated Action Triggered |
| :--- | :--- | :--- | :--- |
| **Latency** | 99th percentile HTTP response time | > 850 ms sustained for 3 minutes | Trigger horizontal pod scaling (HPA) & page on-call SRE |
| **Traffic** | Requests per second (RPS) per ingress | Deviation > 50% from baseline prediction | Anomaly detection alert dispatched to `#cloudops-alerts` |
| **Errors** | HTTP 5xx error percentage | > 0.1% total requests over 2 minutes | Auto-halt CI/CD deployment canary; page primary SRE |
| **Saturation** | Database CPU & Connection Pool % | > 85% connection limit or CPU > 90% | Trigger PgBouncer rate limits and alert Database Administrator |

## 4. Centralized Log Aggregation and Audit Archival
- FluentBit agents stream high-volume container logs to Google Cloud Logging.
- Sinks export security-critical audit logs to a partitioned BigQuery table for real-time SIEM inspection and immutable Cloud Storage Archive buckets for 7-year regulatory retention.
"""
    },
    {
        "id": "1671218",
        "title": "Global Traffic Management, Cloud CDN, and Edge Acceleration",
        "spaceKey": "AITEST",
        "version": 1,
        "lastUpdated": "2026-09-14T17:15:00Z",
        "author": "traffic.engineering@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1671218/Global+Traffic+Management+Cloud+CDN+and+Edge+Acceleration",
        "content": """
# Global Traffic Management, Cloud CDN, and Edge Acceleration

## 1. Global Anycast Routing Overview
Client traffic worldwide enters our network via Google's Global Anycast IP infrastructure. Traffic terminates at the nearest Google Edge Point of Presence (PoP) across 140+ global edge locations, routing packets across Google's private, high-speed fiber backbone to application clusters in `us-central1`.

## 2. Multi-Cloud DNS Routing and Health Checking
- **AWS Route 53 Traffic Flow**: Configured with latency-based routing policies and calculated health checks.
- If primary GCP endpoints experience health check failure (3 consecutive 5xx responses over 15 seconds), Route 53 automatically shifts DNS resolution to secondary AWS ALB ingress endpoints.
- DNS TTL is set to 30 seconds for all production public endpoints to ensure rapid failover propagation.

## 3. Cloud CDN vs. Amazon CloudFront Caching Strategy

| Feature | Google Cloud CDN | Amazon CloudFront | Production Configuration |
| :--- | :--- | :--- | :--- |
| **Edge Locations** | 140+ Google Edge PoPs | 450+ CloudFront PoPs | Dual-CDN strategy for static assets and video streaming |
| **Cache Invalidation** | Sub-second global cache purge | 1 - 3 minute invalidation SLA | Trigger cache purge via Cloud Build CI/CD deployment webhook |
| **Compression** | Brotli & Gzip automatic compression | Brotli & Gzip automatic compression | Enabled for all text/html, application/json, and CSS assets |
| **Origin Shielding** | Cloud CDN Origin Shield | CloudFront Origin Shield | Enabled in `us-central1` to prevent thundering herd load spikes |

## 4. Edge DDoS Mitigation and SSL Termination
- All TLS termination occurs at the edge using Google-managed and AWS-managed wildcard certificates with automated 90-day renewal cycles.
- Cloud Armor and AWS Shield Advanced provide continuous layer-3, layer-4, and layer-7 automated SYN flood and UDP amplification mitigation.
"""
    }
,
    {
        "id": "1867779",
        "title": "CloudOps AI Enterprise Architecture and Intelligence Engine",
        "spaceKey": "AITEST",
        "version": 1,
        "lastUpdated": "2026-09-19T21:45:00Z",
        "author": "cloudops.architect@cloudops.internal",
        "url": "https://abhinavclouds.atlassian.net/wiki/spaces/AITEST/pages/1867779/CloudOps+AI+Enterprise+Architecture+and+Intelligence+Engine",
        "content": """
# CloudOps AI Enterprise Architecture and Intelligence Engine

## 1. System Mission and Autonomous Reasoning Overview
CloudOps AI is an enterprise-grade autonomous reasoning assistant purpose-built to accelerate incident remediation, enforce change management governance, and eliminate human error in high-stress production scenarios across Google Cloud Platform and Amazon Web Services.

## 2. End-to-End Generative AI Pipeline
1. **Client Interaction**: Responsive web chat UI communicates with the backend via asynchronous REST API (`/api/chat`).
2. **Security & Injection Guardrails**: Pre-compiled heuristic regex patterns detect and neutralize prompt injection attempts, role-play bypasses, and credential exfiltration before reaching the model.
3. **Two-Phase Retrieval Strategy**:
   - Phase 1: Keyword CQL search over Confluence Cloud space `AITEST` with stop-word filtration.
   - Phase 2: Intent-driven multi-page expansion (e.g., automatically linking Incident Management with Change Management for rollback operations).
4. **Vertex AI Gemini Foundation Engine**: Interacts with Google Cloud Vertex AI using `gemini-2.5-flash` at temperature 0.1 for deterministic, verifiable answers.
5. **Post-Processing & Grounding Validator**: Maps retrieved pages to live Confluence Cloud URLs, formats structured responses (Answer, Recommended Approach, Source Pages), and enforces strict anti-hallucination guardrails.

## 3. Supported vs. Unsupported Cloud Environments
- **Fully Supported**: Google Cloud Platform (GCP) and Amazon Web Services (AWS).
- **Unsupported**: Microsoft Azure is currently not an officially supported cloud tier. If a user requests Azure operations (e.g. Azure Kubernetes Service), the agent explicitly refuses to hallucinate instructions and cites the lack of authoritative Confluence documentation.

## 4. Latency SLAs and Telemetry
- API Gateway latency: < 50ms.
- Confluence live retrieval latency: 350ms - 650ms.
- Vertex AI Gemini 2.5 Flash reasoning latency: 6,000ms - 9,500ms.
- Total end-to-end P95 response SLA: < 12 seconds.
- Audit Logging: All queries, tokens, and citations are streamed to Google Cloud Logging under structured JSON schemas for SOC-2 Type II compliance.
"""
    }
]

