#!/bin/bash

# Initialize variables with default values
TARGET_HASH=''
NUM_PROCESSES_THREADS= # Default value for NUM_PROCESSES_THREADS
CONTAINER_MODE=''      # Default value for CONTAINER_MODE
WORDLIST_FILENAME='' # Default value for WORDLIST_FILENAME
CONTAINER_IMAGE=''
PYTHON_SCRIPT=''
PARALLELISM=2

# Function to display script usage
function display_usage() {
  echo "Usage: $0 [-H|--hash <TARGET_HASH>] [-N|--num-processes-threads <NUM_PROCESSES_THREADS>] [-M|--mode <MODE>] [--wordlist <WORDLIST_FILENAME>] [--cpu <CPU_LIMIT>] [--memory <MEMORY_LIMIT>] [-P|--parallelism <PARALLELISM>] [--help]"
  echo "Options:"
  echo "  -H, --hash                     Specify the target hash (e.g., '\$2b\$10\$iXPVYOPG1UbIDNQtVOZnUOBcxathZbvwON9jrRY4BScvgVp4VPpyW')"
  echo "  -N, --num-processes-threads    Specify the number of processes or threads (e.g., '16') (default: 10)"
  echo "  -M, --mode                     Specify the mode: 'PL' for parallel or 'Seq' for sequential (default: PL)"
  echo "  --wordlist                     Specify the wordlist filename (e.g., 'John.txt' or 'rockyou.txt') (default: John.txt)"
  echo "  --cpu                          Specify the CPU limit (e.g., '200m') (default: all cpu resources)"
  echo "  --memory                       Specify the memory limit (e.g., '0.5Gi') (default: up to full memory resources)"
  echo "  -P, --parallelism              Specify the number of parallelism (default: 2)"
  echo "  --help                         Display this help message"
}

# Parse command-line options
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    -H|--hash)
      TARGET_HASH="$2"
      shift # past argument
      shift # past value
      ;;
    -N|--num-processes-threads)
      NUM_PROCESSES_THREADS="$2"
      shift # past argument
      shift # past value
      ;;
    -M|--mode)
      CONTAINER_MODE="$2"
      shift # past argument
      shift # past value
      ;;
    --wordlist)
      WORDLIST_FILENAME="$2"
      shift # past argument
      shift # past value
      ;;
    --cpu)
      CPU_LIMIT="$2"
      shift # past argument
      shift # past value
      ;;
    --memory)
      MEMORY_LIMIT="$2"
      shift # past argument
      shift # past value
      ;;
    -P|--parallelism)
      PARALLELISM="$2"
      shift # past argument
      shift # past value
      ;;
    --help)
      display_usage
      exit 0
      ;;
    *) # unknown option
      echo "Error: Unknown option '$key'."
      display_usage
      exit 1
      ;;
  esac
done

# Set default values if the corresponding variables are empty
if [[ -z $NUM_PROCESSES_THREADS ]]; then
  NUM_PROCESSES_THREADS=10
fi

if [[ -z $CONTAINER_MODE ]]; then
  CONTAINER_MODE='PL'
fi

if [[ -z $WORDLIST_FILENAME ]]; then
  WORDLIST_FILENAME='John.txt'
fi

# Check if the required arguments are provided
if [[ -z $TARGET_HASH || -z $NUM_PROCESSES_THREADS || -z $CONTAINER_MODE || -z $WORDLIST_FILENAME ]]; then
  echo "Error: Missing required arguments."
  display_usage
  exit 1
fi

# Determine the container image and Python script based on the selected mode
case $CONTAINER_MODE in
  "PL"|"parallel")
    CONTAINER_IMAGE="mahmoodmattar/bcrypt_cracking:Parallel"
    PYTHON_SCRIPT="crack_PL.py"
    ;;
  "Seq"|"sequential")
    CONTAINER_IMAGE="mahmoodmattar/bcrypt_cracking:Sequential"
    PYTHON_SCRIPT="crack_Seq.py"
    ;;
  *)
    echo "Error: Invalid mode. Supported modes are 'PL' or 'parallel', and 'Seq' or 'sequential'."
    display_usage
    exit 1
    ;;
esac

# Create a temporary YAML file with the desired values
cat > parallelism_temp.yaml << EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: cracking-job
spec:
  parallelism: $PARALLELISM
  completions: $PARALLELISM
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: cracking-container
          image: $CONTAINER_IMAGE
          env:
            - name: TARGET_HASH
              value: "$TARGET_HASH"
            - name: INPUT_FILE
              value: "/crack_final/input/$WORDLIST_FILENAME"
            - name: NUM_PROCESSES
              value: "$NUM_PROCESSES_THREADS"
          volumeMounts:
            - name: wordlist-volume
              mountPath: /crack_final/input # Update this to the actual path of the wordlist on the worker nodes
          command:
            - "python3"
          args:
            - "$PYTHON_SCRIPT"
EOF

# Add the resources section if CPU or memory limit is provided
if [[ -n $CPU_LIMIT || -n $MEMORY_LIMIT ]]; then
  cat >> parallelism_temp.yaml << EOR
          resources:
$( [ -n "$CPU_LIMIT" ] && echo "            limits:" || echo "" )
$( [ -n "$CPU_LIMIT" ] && echo "              cpu: $CPU_LIMIT" || echo "" )
$( [ -n "$MEMORY_LIMIT" ] && echo "              memory: $MEMORY_LIMIT" || echo "" )
EOR
fi

cat >> parallelism_temp.yaml << EOF
      volumes:
        - name: wordlist-volume
          hostPath:
            path: /home/crack_final/input # Update this to the actual path of the wordlist on the worker nodes
  backoffLimit: 0
EOF

# Deploy the Kubernetes Job
kubectl apply -f parallelism_temp.yaml > /dev/null 2>&1

# Wait for the job to complete
echo "Waiting for the job to complete..."  > /dev/null 2>&1
kubectl wait --for=condition=complete job/cracking-job --timeout=300s > /dev/null 2>&1
PASSWORD_FOUND=false

# Check logs of the pods to find if the password is found
for pod in $(kubectl get pods -l job-name=cracking-job -o jsonpath='{.items[*].metadata.name}'); do
  log=$(kubectl logs $pod)
  if [[ $log == *"Password cracked successfully!"* ]]; then
    echo "$log"
    PASSWORD_FOUND=true
  fi
done

# If the password is not found, display a message
if [[ $PASSWORD_FOUND == false ]]; then
  last_pod=$(kubectl get pods -l job-name=cracking-job -o jsonpath='{.items[-1].metadata.name}')
  kubectl logs $last_pod
fi
# Get the job name from the temporary YAML file
JOB_NAME=$(kubectl get -f parallelism_temp.yaml -o=jsonpath='{.metadata.name}')

# Delete the job using the job name variable
kubectl delete job $JOB_NAME > /dev/null 2>&1

# Delete the temporary YAML file
rm parallelism_temp.yaml



