FROM jenkins/jenkins:lts-jdk17

USER root
RUN apt-get update && apt-get install -y curl jq && rm -rf /var/lib/apt/lists/*
USER jenkins

# Pre-install plugins: pipeline, credentials, JCasC, Plain Credentials binding
RUN jenkins-plugin-cli --plugins \
    workflow-aggregator \
    pipeline-model-definition \
    configuration-as-code \
    plain-credentials \
    credentials-binding \
    git \
    http_request \
    build-user-vars-plugin

ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"
ENV CASC_JENKINS_CONFIG="/var/jenkins_home/casc_configs/jenkins.yaml"

# Groovy init script to set admin password — JCasC password: field does not reliably
# override the Jenkins initial admin password in the Docker image.
COPY init-admin-password.groovy /usr/share/jenkins/ref/init.groovy.d/
