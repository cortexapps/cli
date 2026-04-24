import kratix_sdk as ks
import yaml


def main():
    sdk = ks.KratixSDK()
    resource = sdk.read_resource_input()
    name = resource.get_name()
    message = resource.get_value("spec.message")

    configmap = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": name,
            "namespace": "default",
        },
        "data": {
            "message": message,
        },
    }

    data = yaml.safe_dump(configmap).encode("utf-8")
    sdk.write_output("configmap.yaml", data)

    status = ks.Status()
    status.set("message", message)
    sdk.write_status(status)


if __name__ == "__main__":
    main()