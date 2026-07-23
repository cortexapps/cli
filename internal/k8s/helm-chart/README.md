# Cortex k8s Helm Chart

## Requirements
* [Helm](https://helm.sh/docs/intro/install/)
* A token for our package registry

## Process
1. Generate a new Cortex API Key on the [API Keys Settings tab](https://app.getcortexapp.com/admin/settings/api-keys) in Cortex.
	- This will be used for the Cortex Kubernetes agent to communicate and push service information to Cortex backend without exposing your public API Key.
2. Inside your Kubernetes cluster, run the following command to generate a Kubernetes secret for the Cortex API Key.
  `kubectl create secret generic cortex-key --from-literal api-key=YOUR_API_KEY`
3. Run `kubectl create secret docker-registry cortex-docker-registry-secret --docker-server=ghcr.io --docker-username=$GITHUB_USERNAME --docker-password=$GITHUB_PASSWORD --docker-email=<doesn't matter>`
4. Download the helm chart and inside the repository run the following command to install the agent in your cluster.
  `helm install YOUR_SELECTED_CHART_NAME .`

## Customization
The helm chart make installation quick and simple, but if you want to customize any of the installation features for the Cortex agent you can do so by changing the following information in the `values.yaml` of the helm chart.
### Service Account
To authenticate the Cortex agent in your cluster and grant it access to service information, the agent needs its own service account. The helm chart by default creates a Service Account `cortex-service-account`, but you can customize the `name` and `namespace` of this Service Account. If you already have a Service Account that you want the Cortex agent to use, set `create: false` under `serviceAccount` and enter the `name` and `namespace` of the Service Account you wish to use.
### Service
The service type and port can be customized as well. For security, the agent uses a default `ClusterIP` service type that only allows the service to be accessed from within the cluster.
### Resources
By default, no resources are specified. While the Cortex Kubernetes agent is designed to be lightweight and minimize resource utilization, you have the option to add custom CPU limits and requests.
### Base URL
The Base URL defaults to that for the hosted version of Cortex. If you are using the on-prem version of Cortex, you should change the `app/baseUrl` value to the correct URL for your on-prem Cortex.

# Usage
After installation, usage is very simple as no additional steps are required. The next time you go to create a new service in your Service Directory Homepage, you should see all of your Kubernetes services already added, ready for you to use in Cortex. If you do not want to import all of your Kubernetes discovered services, you can simply remove the ones you do not want to add. Removed services will still show up in the Kubernetes tab of Discovered Services if you want to go back and add them later.
