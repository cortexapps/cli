# SKE + Cortex Integration Flow

## How it works

When a platform team installs an SKE Promise with the `kratix.io/cortex: "true"` label, the **SKE Cortex Controller** automatically registers the Promise as an Entity Type in Cortex and generates Create, Update, and Delete workflows. Developers then use Cortex to request and manage platform resources without needing direct Kubernetes access.

**What is a Promise?** A Promise is a YAML file with two parts: (1) an **API** — a Kubernetes CRD that defines the fields developers fill in (e.g. `spec.message`, `spec.size`), and (2) a **Pipeline** — a container image that transforms the developer's input into real Kubernetes resources (e.g. a ConfigMap, Deployment, or database).

### Setup (one-time)

```mermaid
flowchart TD
    A["Platform Team — Defines Promise"]
    B["SKE Cortex Controller — Detects labeled Promise"]
    C["Cortex — Entity Type + Workflows auto-created"]

    A -->|1. kubectl apply promise.yaml| B
    B -->|2. Registers Entity Type + Create, Update, Delete Workflows| C

    style A fill:#6366f1,stroke:#4f46e5,color:#fff
    style B fill:#f59e0b,stroke:#d97706,color:#fff
    style C fill:#10b981,stroke:#059669,color:#fff
```

### Request lifecycle

```mermaid
flowchart TD
    D["Developer — Triggers workflow in Cortex"]
    E["Git Repo — kratix-resource-requests/"]
    F["ArgoCD — Syncs request to cluster"]
    G["Kratix — Picks up resource request"]
    H["Pipeline Pod — Transforms request into K8s manifests"]
    I["Git Repo — kratix-output/"]
    J["ArgoCD — Syncs output to cluster"]
    K["Provisioned Resource — ConfigMap, Deployment, etc."]
    L["Cortex Entity — Status updated"]

    D -->|3. Commits resource request YAML| E
    E -->|4. Detects new file| F
    F -->|5. Applies to cluster| G
    G -->|6. Runs pipeline| H
    H -->|7. Writes manifests| I
    I -->|8. Detects new output| J
    J -->|9. Creates resource| K
    H -.->|Updates status| L

    style D fill:#10b981,stroke:#059669,color:#fff
    style E fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style F fill:#3b82f6,stroke:#2563eb,color:#fff
    style G fill:#f59e0b,stroke:#d97706,color:#fff
    style H fill:#f59e0b,stroke:#d97706,color:#fff
    style I fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style J fill:#3b82f6,stroke:#2563eb,color:#fff
    style K fill:#ef4444,stroke:#dc2626,color:#fff
    style L fill:#10b981,stroke:#059669,color:#fff
```

### Color key

| Color | Component |
|-------|-----------|
| **Purple** | Git Repository |
| **Blue** | ArgoCD (GitOps sync) |
| **Yellow** | Kratix / SKE (Kubernetes) |
| **Green** | Cortex (Developer Portal) |
| **Red** | Final provisioned resource |

## Step by step

1. **Platform team** defines a Promise (API + pipeline) and applies it to the cluster
2. **SKE Cortex Controller** detects the `kratix.io/cortex: "true"` label and creates an Entity Type and Workflows in Cortex
3. **Developer** opens Cortex, finds the service, and runs a workflow (e.g. "Create Message")
4. **Cortex workflow** commits a resource request YAML to the Git repository
5. **ArgoCD** detects the new file and syncs it to the Kubernetes cluster
6. **Kratix** picks up the resource request and runs the pipeline pod
7. **Pipeline** transforms the request into Kubernetes manifests and writes them to Git
8. **ArgoCD** syncs the pipeline output back to the cluster
9. **Resource** is created on the cluster and status is synced back to the Cortex entity

## Architecture overview

```mermaid
flowchart TD
    PT["Platform Team"]
    SKE["SKE Cortex Controller"]
    ET["Entity Type"]
    WF["Workflows"]
    DEV["Developer"]
    GR["Git Repo — resource-requests/"]
    KR["Kratix Platform Controller"]
    PP["Pipeline Pod"]
    GO["Git Repo — pipeline-output/"]
    RES["Provisioned Resource"]

    PT -->|kubectl apply| SKE
    SKE -->|registers| ET
    SKE -->|generates| WF
    DEV -->|triggers| WF
    WF -->|commits| GR
    GR -->|ArgoCD syncs| KR
    KR -->|runs| PP
    PP -->|writes| GO
    PP -.->|updates status| ET
    GO -->|ArgoCD syncs| RES

    style PT fill:#6366f1,stroke:#4f46e5,color:#fff
    style SKE fill:#f59e0b,stroke:#d97706,color:#fff
    style KR fill:#f59e0b,stroke:#d97706,color:#fff
    style PP fill:#f59e0b,stroke:#d97706,color:#fff
    style ET fill:#10b981,stroke:#059669,color:#fff
    style WF fill:#10b981,stroke:#059669,color:#fff
    style DEV fill:#10b981,stroke:#059669,color:#fff
    style GR fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style GO fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style RES fill:#ef4444,stroke:#dc2626,color:#fff
```
