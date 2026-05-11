#!/bin/bash
set -e

# Usage:
#   bash planemo_run_workflow.sh GALAXY_URL API_KEY workflow.ga job.yml [--no_wait]
#
# Example:
#   bash planemo_run_workflow.sh https://usegalaxy.org.au $GALAXY_API_KEY workflow.ga job.yml

GALAXY_URL="$1"
API_KEY="$2"
WORKFLOW_FILE="$3"
JOB_FILE="$4"
EXTRA_FLAG="${5:-}"

if [ -z "$GALAXY_URL" ] || [ -z "$API_KEY" ] || [ -z "$WORKFLOW_FILE" ] || [ -z "$JOB_FILE" ]; then
  echo "Usage: bash planemo_run_workflow.sh GALAXY_URL API_KEY workflow.ga job.yml [--no_wait]"
  exit 1
fi

echo "Running planemo against: ${GALAXY_URL}"
echo "Workflow: ${WORKFLOW_FILE}"
echo "Job file: ${JOB_FILE}"

planemo run \
  --galaxy_url "${GALAXY_URL}" \
  --galaxy_user_key "${API_KEY}" \
  --download_outputs \
  ${EXTRA_FLAG} \
  "${WORKFLOW_FILE}" "${JOB_FILE}" | tee planemo_run.log

echo "Done. See planemo_run.log and downloaded outputs."
