#!/usr/bin/env bash

LOCAL_TESTRIBUTE_IMAGE=${TESTRIBUTE_IMAGE:-elixircloud/testribute:latest}
LOCAL_HOST_NAME=${TESTRIBUTE_HOST:-testribute}

# Helper functions
function deploy() { # {{{
cat << EOF
apiVersion: v1
kind: List
metadata: {}
items:
- apiVersion: apps/v1
  kind: Deployment
  metadata:
    labels:
      app: testribute
    name: testribute
  spec:
    replicas: 1
    selector:
      matchLabels:
        app: testribute
    template:
      metadata:
        labels:
          app: testribute
      spec:
        containers:
          - image: ${LOCAL_TESTRIBUTE_IMAGE}
            name: testribute
            command:
            - /bin/bash
            - -c
            - cd /app/TEStribute; python server.py

- apiVersion: v1
  kind: Service
  metadata:
    labels:
      app: testribute
    name: testribute
  spec:
    selector:
      app: testribute
    ports:
    - name: 8080-8080
      port: 8080
      protocol: TCP
      targetPort: 8080
    type: ClusterIP

# Here lacks TLS configuration
- apiVersion: extensions/v1beta1
  kind: Ingress
  metadata:
    labels:
      app: testribute
    name: testribute
  spec:
    rules:
    - host: ${LOCAL_HOST_NAME}
      http:
        paths:
        - path: "/"
          backend:
            serviceName: testribute
            servicePort: 8080
EOF
} # }}}

function usage() { # {{{
  echo -en "TEStribute deployer.\n"
  echo -en "\nUsage:\n\t<envVar1>=<value1> <envVar2>=<value2> ... $0 -d | kubectl -n <namespace> create -f -\n"
  echo -en "\nEnv vars:\n\tTESTRIBUTE_IMAGE: Use this image URI to run TEStribute.\n\tDefault: ${LOCAL_TESTRIBUTE_IMAGE}\n"
  echo -en "\n\tTESTRIBUTE_HOST: Expose TEStribute at this host.\n\tDefault: ${LOCAL_HOST_NAME}\n"
  echo -en "\n"
} # }}}


# Deal with args here

while getopts "hd" opt; do 
  case $opt in
    h)
      usage
      exit
      ;;
    d)
      deploy
      exit
      ;;
  esac
done

usage

