# Drone plugin to update Rancher app

Drone.io allows to run tests, build images and push them in a registry. To deploy the new image on Kubernetes, we can use [this nice plugin](http://plugins.drone.io/mactynow/drone-kubernetes/) that is able to change image in a deployment.

With Rancher, that can be a bit problematic as the given "answers" for an application is not set. So, using interface to update something can potentially reset some values in a Deployment.

"drone-plugin-rancher" is made to hit Rancher API to change the answer as if you did it on Rancher UI. You don't need to use "drone-kubernetes" plugin.

**Important** this plugin only manages "answers" and not "YAML" configuration.

**I'm not responsible for possible application breaks, failure and data loses** - You **must know what you do before to use the plugin** - Please backup application and data before to try the plugin.

# Usage

In your `.drone.yml` file, lets take the example of building an image, then push it to a registry. Then, we set the new image tag on the corresponding answer.

```yaml
kind: pipeline
name: build-blog

steps:
- name: build-image
  image: plugin/docker
  settings:
    repo: foo/bar
    tags:
      - latest
      - ${DRONE_COMMIT_SHA}
- name: deploy
  image: metal3d/drone-plugin-rancher:v1
  settings:
    api: https://rancher.url/v3
    project: Default
    app: myblog
    token:
      from_secret: rancher-token
    verify: false
    cluster: mycluster
    keys: "image.tag,other.value"
    values: "${DRONE_COMMIT_SHA},whatever"
```

This example will update the application named "myblog" in the "Default" project. It will **merge** your answers to the already existing values.

Changing a key in answers should be applied by Rancher to corresponding resources. You need to know how the Rancher application is deployed and which key to change.

# Settings

The managed settings are:

- `api` that should be the Rancher API URL, the plugin is currently only compatible with tester v3 version
- `cluster` is the cluster name
- `project` (optional, default to "Default") is the project name where the application you want to manage resides
- `app` is the name of the application you want to update
- `token` is the token you generated in Rancher to make the plugin able to contact Rancher API, please use secret to not display the token in drone file
- `keys` ordered keys (comma separated) of the answer that you want to change, keep order following values
- `values` ordered values for corresponding keys to set

# Future work

To not have break in future plugin upgrade, please consider to use fixed tags.

`v1` will continue to use the same format and behavior. That should not break your deployment, but **please make backups before testing the plugin, and especially when you upgrade the plugin version.**

Changing to next releases as "v2" may break your application, one more time, make backups.

