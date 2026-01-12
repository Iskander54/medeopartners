#!/bin/bash

# Script de monitoring des VMs Medeo
# Usage: ./monitor_vms.sh

PROJECT_ID="mystical-runway-364716"
APP_INSTANCE_ID="6031040178769828631"
AD_INSTANCE_ID="2712066344944087395"

echo "=== MONITORING VMs MEDEO - $(date) ==="
echo

# 1. État des VMs
echo "📊 ÉTAT DES VMs:"
gcloud compute instances list --filter="name:(medeo-app-01 OR medeo-ad-01)" --format="table(name,zone,machineType,status,internalIP,externalIP)" --project=$PROJECT_ID
echo

# 2. Configuration Shielded VM
echo "🔒 CONFIGURATION SHIELDED VM (medeo-app-01):"
gcloud compute instances describe medeo-app-01 --zone=europe-west1-c --format="value(shieldedInstanceConfig)" --project=$PROJECT_ID
echo

# 3. Erreurs récentes (dernières 2 heures)
echo "⚠️  ERREURS RÉCENTES (dernières 2h):"
gcloud logging read "resource.type=gce_instance AND (resource.labels.instance_id=$APP_INSTANCE_ID OR resource.labels.instance_id=$AD_INSTANCE_ID) AND timestamp>=\"2025-09-03T18:00:00Z\" AND severity>=ERROR" --limit=10 --format="table(timestamp,resource.labels.instance_id,severity,textPayload)" --project=$PROJECT_ID
echo

# 4. Erreurs d'intégrité Shielded VM
echo "🛡️  ERREURS D'INTÉGRITÉ SHIELDED VM:"
gcloud logging read "resource.type=gce_instance AND resource.labels.instance_id=$APP_INSTANCE_ID AND timestamp>=\"2025-09-03T18:00:00Z\" AND logName=\"projects/$PROJECT_ID/logs/compute.googleapis.com%2Fshielded_vm_integrity\"" --limit=5 --format="table(timestamp,severity,jsonPayload.policyEvaluationPassed)" --project=$PROJECT_ID
echo

# 5. Erreurs MongoDB
echo "🍃 ERREURS MONGODB:"
gcloud logging read "resource.type=gce_instance AND resource.labels.instance_id=$APP_INSTANCE_ID AND timestamp>=\"2025-09-03T18:00:00Z\" AND textPayload:\"MongoDB\"" --limit=5 --format="table(timestamp,severity,textPayload)" --project=$PROJECT_ID
echo

# 6. Erreurs Fluent Bit
echo "📝 ERREURS FLUENT BIT:"
gcloud logging read "resource.type=gce_instance AND resource.labels.instance_id=$APP_INSTANCE_ID AND timestamp>=\"2025-09-03T18:00:00Z\" AND logName=\"projects/$PROJECT_ID/logs/ops-agent-fluent-bit\" AND severity>=ERROR" --limit=5 --format="table(timestamp,severity,textPayload)" --project=$PROJECT_ID
echo

echo "=== FIN DU MONITORING ==="
