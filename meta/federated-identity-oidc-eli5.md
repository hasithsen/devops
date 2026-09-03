# Badges, Keycards, and the Cluster ID Office

### How AKS Workload Identity, OIDC, and Federated Credentials Actually Fit Together

*A plain-language walkthrough for platform engineers who keep hearing “federate the SA to the UAMI” and want the mental model, not just the `az` command.*

---

## The problem in one sentence

A pod in Kubernetes needs to call Azure (Key Vault, Storage, ACR, …), and Azure will not trust a random process just because it lives in your cluster.

---

## Two kinds of identity (don’t mix them up)

| Layer | What it is | Nickname |
|-------|------------|----------|
| **Kubernetes ServiceAccount** | Who the pod is *inside* the cluster | **Badge** |
| **Azure User-Assigned Managed Identity (UAMI)** | Who can open doors *in Azure* | **Keycard** |

They are different objects in different systems. Linking them is the whole game.

```
  Kubernetes                              Azure
 ─────────────                           ───────

  ┌─────────────────┐                   ┌─────────────────┐
  │ ServiceAccount  │                   │ Managed Identity│
  │ build-actions-sa│                   │  odin-api-dev   │
  │                 │                   │                 │
  │   "the badge"   │                   │  "the keycard"  │
  └─────────────────┘                   └─────────────────┘
```

Putting the keycard’s ID number on the badge sticker is **not** enough by itself. Azure still needs a rule that says that badge may use that keycard.

---

## The old way (and why we stopped)

```
  Pod ──carries──► long-lived secret / client secret
                         │
                         ▼
                   Azure accepts it
```

If someone steals the pod (or its env / secret mount), they steal the key forever. Rotation is painful. Audit is fuzzy.

---

## The new way: federated identity

No long-lived secret in the pod. Instead:

1. Kubernetes issues a **short-lived proof** that the pod is a specific ServiceAccount.
2. Azure AD checks that proof.
3. If a **federation rule** says that proof may act as this Managed Identity, Azure hands out a normal Azure access token.

```
  ┌──────────┐     short-lived      ┌──────────┐     Azure token     ┌────────┐
  │   Pod    │ ───────────────────► │ Azure AD │ ──────────────────► │  KV /  │
  │ (as SA)  │   "I'm this SA"      │          │   "ok, act as UAMI" │ Storage│
  └──────────┘                      └──────────┘                     └────────┘
```

---

## What is an OIDC issuer?

Think of the cluster as having a public **ID office**.

When Kubernetes says “this pod is `build-actions-sa`,” Azure asks:

> Who signed this ID? Can I verify their paperwork?

The **OIDC issuer** is that ID office’s address — a URL unique to the cluster, roughly:

```text
https://<region>.oic.prod-aks.azure.com/<tenant-id>/<cluster-id>/
```

```
                    ┌─────────────────────────────┐
                    │     AKS cluster             │
                    │                             │
                    │   ┌─────────────────────┐   │
                    │   │   OIDC ID Office    │   │
                    │   │   (issuer URL)      │   │
                    │   │                     │   │
                    │   │  signs SA tokens    │   │
                    │   │  publishes public   │   │
                    │   │  keys (JWKS)        │   │
                    │   └─────────────────────┘   │
                    └─────────────────────────────┘
                                    │
                                    │  "iss" in every SA JWT
                                    ▼
                              Azure AD looks here
```

**One line:** the OIDC issuer is *which Kubernetes cluster is allowed to vouch for a ServiceAccount*.

Dev and prod-stg each have their **own** issuer. A badge from the wrong building does not open the door.

---

## What is a federated credential?

A row on the Managed Identity in Azure that says:

> I trust **this issuer** + **this subject** (+ this audience) to use **me**.

Subject is usually:

```text
system:serviceaccount:<namespace>:<serviceaccount-name>
```

Example:

```text
system:serviceaccount:argo:build-actions-sa
```

```
  Managed Identity: odin-api-dev
  ┌──────────────────────────────────────────────────────────┐
  │ Federated credentials                                   │
  │                                                          │
  │  #1  issuer = https://.../odin-dev-aks/.../              │
  │      subject = system:serviceaccount:odin:odin-api       │
  │                                                          │
  │  #2  issuer = https://.../odin-dev-aks/.../   (optional) │
  │      subject = system:serviceaccount:argo:build-actions-sa│
  └──────────────────────────────────────────────────────────┘
```

If only rule `#1` exists, the API pods can get tokens. Build-action pods wearing a different badge cannot — even if you wrote the same client ID on their ServiceAccount annotation.

---

## How Azure actually checks the ServiceAccount

Azure does **not** call your kube-apiserver and ask “is this pod real?”  
It does public cryptography against the cluster’s OIDC documents.

### Step by step

```
  (1) Pod needs Azure access
           │
           ▼
  (2) Kubernetes projects / issues a short-lived JWT for the SA
           │
           │  claims include:
           │    sub = system:serviceaccount:argo:build-actions-sa
           │    iss = https://...oic.prod-aks.azure.com/.../
           │    aud = api://AzureADTokenExchange
           │
           ▼
  (3) Identity library POSTs that JWT to Azure AD
      "Exchange this for a token for UAMI <client-id>"
           │
           ▼
  (4) Azure AD verifies the JWT
           │
           ├─► read iss
           ├─► fetch issuer's JWKS (public keys)
           ├─► check signature, expiry, audience
           └─► find federated credential matching
                 issuer + subject (+ audience)
           │
           ▼
  (5a) Match          (5b) No match
       │                    │
       ▼                    ▼
   mint Entra            reject
   access token          (AADSTS errors)
   for the UAMI
```

### Sequence view

```
  Pod/SA                 AKS OIDC              Azure AD              Key Vault
    │                       │                     │                     │
    │  SA JWT (signed)      │                     │                     │
    │──────────────────────►│ (keys published)    │                     │
    │                       │                     │                     │
    │  token exchange (JWT + client-id)           │                     │
    │────────────────────────────────────────────►│                     │
    │                       │   GET JWKS from iss │                     │
    │                       │◄────────────────────│                     │
    │                       │   verify signature  │                     │
    │                       │   check fedcred     │                     │
    │  Azure access token                         │                     │
    │◄────────────────────────────────────────────│                     │
    │                                                                   │
    │  API call + Bearer token                                          │
    │──────────────────────────────────────────────────────────────────►│
```

---

## The annotation people always confuse with federation

On the ServiceAccount you often see:

```yaml
metadata:
  annotations:
    azure.workload.identity/client-id: "<UAMI-client-id>"
```

That sticker means: **“when this badge asks for a token, try *this* keycard.”**

It does **not** create trust in Azure. Trust is only the federated credential.

```
  Wrong mental model:

    annotate SA with client-id  ──►  Azure trusts it forever
                         ✗


  Right mental model:

    annotate SA with client-id  ──►  "which keycard to request"
    federated credential        ──►  "Azure allows this badge to use it"
```

---

## A concrete story (API vs build-actions)

Imagine two badges in one cluster, one shared keycard number:

```
  Badge A: odin-api          ──►  federated  ──►  UAMI odin-api-dev   ✅ works
  Badge B: build-actions-sa  ──►  no fedcred ──►  same UAMI client-id  ❌ fails
```

Copying the client ID onto badge B is like writing the master key’s serial number on Alice’s visitor pass. The door still checks the federation list.

You can either:

1. **Add a second federated credential** on the same UAMI for `build-actions-sa`, or  
2. **Create a dedicated UAMI** for build-actions and federate only that SA to it (cleaner least-privilege).

---

## Cheat sheet

| Term | ELI5 |
|------|------|
| **ServiceAccount** | Badge inside the cluster |
| **UAMI / Managed Identity** | Keycard in Azure |
| **OIDC issuer** | The cluster’s ID office URL |
| **SA JWT** | Short-lived signed badge proof |
| **JWKS** | Public keys so Azure can verify the signature |
| **Federated credential** | Azure rule: this issuer + subject may use this keycard |
| **client-id annotation** | Which keycard number to ask for |
| **Workload Identity** | The whole pattern: badge → proof → exchange → Azure token |

---

## Closing

Workload Identity is not magic. It is three boring ideas stacked:

1. Kubernetes can **sign** short-lived statements about ServiceAccounts.  
2. Azure can **verify** those signatures via the cluster’s OIDC issuer.  
3. You explicitly **allow-list** which statements may become which Managed Identity.

Once you see badges, keycards, and the ID office, the `az identity federated-credential create` line stops feeling like folklore — it’s just writing the allow-list entry.
