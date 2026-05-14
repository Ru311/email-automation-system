# 📧 Email Automation System — GCP + Cloud Run Deployment Guide

---

## 🧭 SECTION 1 — How to Check Your GCP Setup

### 🔐 Login

```bash
gcloud auth login
```

---

### 📌 Set / Check Current Project

```bash
gcloud config get-value project
gcloud config set project email-automation-clean
```

---

### 📦 List Cloud Run Services

```bash
gcloud run services list
```

---

### 🔍 Describe Your Service (Full Config)

```bash
gcloud run services describe email-automation --region=asia-south1
```

---

### 🖼 Get Deployed Image

```bash
gcloud run services describe email-automation \
  --region=asia-south1 \
  --format="value(spec.template.spec.containers[0].image)"
```

---

### ⏱ List Scheduler Jobs

```bash
gcloud scheduler jobs list --location=asia-south1
```

---

### 👤 List Service Accounts

```bash
gcloud iam service-accounts list
```

---

---

# 🚀 SECTION 2 — Deployment Guide (After Code Changes)

## ⚠️ IMPORTANT

* Always build for **amd64** (especially on Mac M1/M2/M3)
* Always run from project root

---

## 🐳 MAC (Apple Silicon) — Recommended

### Build + Push

```bash
docker buildx build \
  --platform linux/amd64 \
  -t asia-south1-docker.pkg.dev/email-automation-clean/email-automation/email-automation \
  --push .
```

---

### Deploy

```bash
gcloud run deploy email-automation \
  --image asia-south1-docker.pkg.dev/email-automation-clean/email-automation/email-automation \
  --region asia-south1
```

---

## 🪟 WINDOWS / INTEL MAC

### Build

```bash
docker build -t email-automation .
```

---

### Tag

```bash
docker tag email-automation asia-south1-docker.pkg.dev/email-automation-clean/email-automation/email-automation
```

---

### Push

```bash
docker push asia-south1-docker.pkg.dev/email-automation-clean/email-automation/email-automation
```

---

### Deploy

```bash
gcloud run deploy email-automation \
  --image asia-south1-docker.pkg.dev/email-automation-clean/email-automation/email-automation \
  --region asia-south1
```

---

## 🧪 Test Deployment

```bash
curl https://email-automation-71080312134.asia-south1.run.app/
```

---

## 📜 View Logs (CLI)

```bash
gcloud run services logs read email-automation --region=asia-south1
```

---

---

# ⏱ SECTION 3 — Scheduler Management

---

## 📌 View Existing Scheduler Jobs

```bash
gcloud scheduler jobs list --location=asia-south1
```

---

## 🔍 Describe Current Job

```bash
gcloud scheduler jobs describe email-job --location=asia-south1
```

---

## ✏️ Update Scheduler Frequency (5 min → 1 min)

### ✅ Change to EVERY 1 MINUTE:

```bash
gcloud scheduler jobs update http email-job \
  --schedule="* * * * *" \
  --location=asia-south1
```

---

## 🧠 Cron Reference

| Frequency   | Cron          |
| ----------- | ------------- |
| Every 5 min | `*/5 * * * *` |
| Every 1 min | `* * * * *`   |
| Every hour  | `0 * * * *`   |

---

## ▶️ Manually Trigger Scheduler

```bash
gcloud scheduler jobs run email-job --location=asia-south1
```

---

## 🛑 Pause Scheduler

```bash
gcloud scheduler jobs pause email-job --location=asia-south1
```

---

## ▶️ Resume Scheduler

```bash
gcloud scheduler jobs resume email-job --location=asia-south1
```

---

---

# ⚡ OPTIONAL — One Command Deploy Script

Create `deploy.sh`:

```bash
#!/bin/bash

IMAGE="asia-south1-docker.pkg.dev/email-automation-clean/email-automation/email-automation"

echo "🐳 Building & pushing..."
docker buildx build --platform linux/amd64 -t $IMAGE --push .

echo "🚀 Deploying..."
gcloud run deploy email-automation --image $IMAGE --region asia-south1

echo "✅ Done"
```

Run:

```bash
bash deploy.sh
```

---

---

# 🎯 SUMMARY

### To redeploy:

```bash
docker buildx build --platform linux/amd64 -t IMAGE --push .
gcloud run deploy ...
```

### To change scheduler:

```bash
gcloud scheduler jobs update http email-job --schedule="* * * * *"
```

### To debug:

```bash
gcloud run services logs read email-automation
```

---

---

# 🚀 You’re now set

You can:

* Rebuild anytime
* Deploy confidently
* Adjust scheduler instantly

No more guessing 👍
