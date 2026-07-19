#!/usr/bin/env bash
set -euo pipefail

project_id="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null)}"
location="${GEMINI_NOTEBOOK_LOCATION:-global}"

if [[ -z "$project_id" || "$project_id" == "(unset)" ]]; then
  echo "Set GOOGLE_CLOUD_PROJECT or select a gcloud project first." >&2
  exit 1
fi

project_number=$(gcloud projects describe "$project_id" --format='value(projectNumber)')
access_token=$(gcloud auth print-access-token)
endpoint="https://${location}-discoveryengine.googleapis.com/v1alpha/projects/${project_number}/locations/${location}/notebooks:listRecentlyViewed?pageSize=5"

response_with_status=$(curl -sS --max-time 60 \
  -H "Authorization: Bearer ${access_token}" \
  -H 'Content-Type: application/json' \
  -w $'\n%{http_code}' \
  "$endpoint")
http_status=${response_with_status##*$'\n'}
response=${response_with_status%$'\n'*}

if (( http_status >= 400 )); then
  printf '%s\n' "$response" | jq '{
    code: .error.code,
    status: .error.status,
    message: .error.message
  }'
  exit 1
fi

printf '%s\n' "$response" | jq '{
  notebook_count: (.notebooks // [] | length),
  notebooks: [(.notebooks // [])[] | {title, notebookId, name}]
}'
