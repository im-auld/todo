## Installing the things we need
```bash
kenobi:monorepo$ mkdir todo-k8s; cd todo-k8s
kenobi:monorepo$ /usr/local/bin/python3 venv todo-k8s
kenobi:monorepo$ todo-k8s/bin/python -m pip install -U pip
kenobi:monorepo$ todo-k8s/bin/python -m pip install grpcio pynamodb
kenobi:monorepo$ brew install terraform
kenobi:monorepo$ brew install jsonnet
kenobi:monorepo$ brew install kubectl
```

## Creating a proto file


## Generate your code
`todo-k8s/bin/python -m grpc_tools.protoc -I proto/ --python_out=proto/ --grpc_python_out=proto/ proto/todo.proto`

#### Note:
Replace `import todo_pb2 as todo__pb2` with `from . import todo_pb2 as todo__pb2`

## Write a client

## Write the service

## Kubernetes - What the hell is it?
From the Kubernetes (k8s) site:

> Kubernetes is an open-source system for automating deployment, scaling, and management of containerized applications.

> It groups containers that make up an application into logical units for easy management and discovery. Kubernetes builds upon 15 years of experience of running production workloads at Google, combined with best-of-breed ideas and practices from the community.

Kubernetes is a tool for container orchestration. You describe the state you want to be in via JSON or YAML files
and Kubernetes will (attempt) to put your system in that state. Let's look at some terms specific to k8s:

Terms from http://python-kube.readthedocs.io/en/latest/concepts.html

 - **Node**: A Node is a worker machine in a Kubernetes Cluster. A Node may be a virtual or physical machine, depending on the cluster.
 - **Pod**: A Pod is the smallest deployable unit of computing that can be created and managed in Kubernetes. It is a group of one or more containers (such as Docker containers), the shared storage for those containers, and options about how to run them. Pods model an application-specific “logical host”.
 - **Namespace**: Kubernetes supports multiple virtual clusters backed by the same physical cluster. These virtual clusters are called namespaces.
 - **Cluster**: A Kubernetes cluster is a set of physical or virtual machines and other infrastructure which runs containerised applications. You would normally interact with the apiserver running on the Kubernetes master node.
 - **Replication Controller**: A ReplicationController ensures that a specified number of pod “replicas” are running at any one time. In other words, a ReplicationController makes sure that a pod or homogeneous set of pods are always up and available. If there are too many pods, it will kill some. If there are too few, the ReplicationController will start more. Unlike manually created pods, the pods maintained by a ReplicationController are automatically replaced if they fail, get deleted, or are terminated.
 - **Replica Set**: A ReplicaSet is the next-generation Replication Controller. The only difference between a ReplicaSet and a Replication Controller is the selector support.
 - **Deployment**: A Deployment provides declarative updates for Pods and Replica Sets (the next-generation Replication Controller). You only need to describe the desired state in a Deployment object, and the Deployment controller will change the actual state to the desired state at a controlled rate for you. You can define Deployments to create new resources, or replace existing ones by new ones.
 - **Service**: A Kubernetes Service is an abstraction which defines a logical set of fungible Pods and a policy by which to access them. The set of Pods targeted by a Service is usually determined by a Label Selector.
 - **Horizontal Pod Autoscaler**: With Horizontal Pod Autoscaling, Kubernetes automatically scales the number of pods in a replication controller, deployment or replica set based on observed CPU utilization (or, with alpha support, on some other, application-provided metrics).

## Kubectl
Since we will be deploying our service to Kubernetes we will need to get
`kubectl` installed and configured. `kubectl` is the command line
interface for Kubernetes. You use it to get logs, delete pods, services,
and deployments and get detailed information about what's
happening in your cluster.

You can even use `kubectl` to deploy your service to k8s but we have a
Jenkins build/deploy tool that can do that for us.

### Installation
You can install `kubectl` with `brew` or `cURL`. It's the same as installing any other package so I won't go into
 detail about it here. However, you will want to make sure you get version 1.6 as we have had some issues with 1.7.

### Configuration
Next you will need to get access to our clusters. YOu can do that by heading to `http://kuberos.offerup.net` and following the instructions there.

### Usage
Here are some common `kubectl` commands when working with a service:

For brevity I'm using an alias I created. It's a good idea to create aliases for `kubectl` lest you accidentally runa command in the wrong environment:
```
kenobi:monorepo$ alias ksdev
alias ksdev='kubectl --context dev --namespace pre-staging'
```

Get the pods running in a namespace/context (in our case pre-staging/dev):
`$ ksdev get pods` or `ksdev get po`

Most `kubectl` commands that name resources (pods, deployments, services, etc) also have a shortened version.
The shortened version of `pods` is `po` for example.

This will produce output that looks something like this:
```
NAME                           READY     STATUS    RESTARTS   AGE
servicea-2896832079-087d6      1/1       Running   0          7d
servicea-2735020731-s43rc      1/1       Running   0          7d
kubernary-8gl71                1/1       Running   0          7d
kubernary-rhzsn                1/1       Running   0          7d
kubernary-t8bjh                1/1       Running   0          7d
kubernary-tbhcj                1/1       Running   0          7d
kubernary-z72zw                1/1       Running   0          5d
servicea-3211819407-q4mb2      1/1       Running   0          7d
servicea-3211819407-whzjj      1/1       Running   0          7d
servicea-2996431968-tlkhg      0/1       Running   0          7d
servicea-2996431968-vdw3q      0/1       Running   0          7d
servicea-556186243-4gmck       1/1       Running   0          7d
todo-k8s-2791184815-rnz06      1/1       Running   0          1d
```

To see the logs for a specific pod:
`ksdev logs --tail 10 -f todo-k8s-2791184815-rnz06`

This will show the last 10 log lines and follow the logs for the given pod.

You can get more information about a pod by using the describe command:
`ksdev describe po todo-k8s-2791184815-rnz06`

`kubectl` has lots of other functionality and is a very powerful tool but these are the commands
we will most likely need as the Jenkins job does a lot of the work for us.

## Jsonnet
### What is jsonnet?
`jsonnet` is another tool we will use to make our lives easier. k8s resources can be described by JSON
or YAML and then passed into `kubectl` which will then communicate with the cluster to create or modify said resources.
Since manually writing complex JSON files is almost guaranteed to produce an error of some kind we will use
`jsonnet` which is a sort of compiled JSON to create our required configuration files. From their website:

> Jsonnet is a domain specific configuration language that helps you define JSON data.
 Jsonnet lets you compute fragments of JSON within the structure, bringing the same benefit
 to structured data that templating languages bring to plain text.

`jsonnet` brings much more sophisticated concepts like functions, import statements and inheritance/OO concepts to
 JSON to help make creating these files simpler and less error prone.

### Usage
A simple example of a `jsonnet` file:

```
// people.jsonnet
// Oh, jsonnet supports comments as well!
{
    person1: {
        name: "Alice",
        welcome: "Hello " + self.name + "!",
    },
    person2: self.person1 { name: "Bob" },
}
```

And how to get it's output:
```
[todo-k8s-demo *$]
kenobi:monorepo ian$ cat <<EOT >> /tmp/people.jsonnet
> {
>     person1: {
>         name: "Alice",
>         welcome: "Hello " + self.name + "!",
>     },
>     person2: self.person1 { name: "Bob" },
> }
> EOT
[todo-k8s-demo *$]
kenobi:monorepo ian$ jsonnet /tmp/people.jsonnet
{
   "person1": {
      "name": "Alice",
      "welcome": "Hello Alice!"
   },
   "person2": {
      "name": "Bob",
      "welcome": "Hello Bob!"
   }
}
```

Pretty cool but not very interesting on it's own. We can however do something a little more complex using
inheritance. We can create a `common.jsonnet` as a base and then only modify some values for each
environment we want to deploy to.

```
// common.libsonnet
{
  serviceName: "todo-k8s",
  configName: "todo-k8s-config",
  ecrRepoAccount: "735354846484.dkr.ecr.us-east-1.amazonaws.com",
  image: "735354846484.dkr.ecr.us-east-1.amazonaws.com/master/todo-k8s:VERSION",
  ecrRepoBase: "master",
  command: "/offerup/todo-k8s-server.pex",
  servicePort: 8081,
  numReplicas: 1,
  maxReplicas: 5,
  minReplicas: 1,
  targetCPUUtilizationPercentage: 80,
  cpuLimit: "300m",  // 0.3 CPU cores
  memoryLimit: "300Mi",  // 300Mb of memory
  cpuRequest: "200m",  // 0.2 CPU cores
  memoryRequest: "200Mi", // 200Mb of memory
  initialDelaySeconds: 30,
  periodSeconds: 3,
}
```

Great, now we have a base to start with let's create a new file that will be specific to our dev environment:

```
// dev.libsonnet
(import "common.libsonnet")+{
    iamRole: "dev-service",
    namespace: "pre-staging",
}
```

For our dev deployment most of the values we added in the common file will be fine. However for our
production deployment we want to be a bit more conservative in our CPU based scaling and we will want
a higher min and max pod count due to the higher traffic. So our prod file might look like this:

```
// prod.libsonnet
(import "common.libsonnet")+{
  iamRole: "prod-service",
  namespace: "prod",
  numReplicas: 2,
  maxReplicas: 10,
  minReplicas: 2,
  targetCPUUtilizationPercentage: 60,
}
```

These files alone won't be all we need. These are just the settings that are unique to our application.
We can then import these objects in to our k8s deployment files and use the values there. This
makes maintaining the files much easier. For example here is the base deployment file provided by the Tools team:

```
// deployment.jsonnet
local utils = import "common/include.libsonnet";
local globals = import "../shared/common.libsonnet";

local serviceName = globals.serviceName;
local servicePort = globals.servicePort;
local numReplicas = globals.numReplicas;
local command = globals.command;
local image = globals.image;

(import "common/deployment.jsonnet") {
  metadata+: {
    labels: {
      app: serviceName
    },
    name: serviceName,
    namespace: "",
  },
  spec+: {
    replicas: numReplicas,
    selector: {
      matchLabels: {
        app: serviceName
      }
    },
    template+: {
      metadata: {
        annotations: {
          "iam.amazonaws.com/role": utils.PLACEHOLDER
        },
        labels: {
          app: serviceName
        }
      },
      spec+: {
        containers: [
          super.containers[0] + {
            command: [
              command,
            ],
            image: image,
            imagePullPolicy: "IfNotPresent",
            name: serviceName,
            ports: [
              {
                name: "grpc",
                containerPort: servicePort,
              },
            ],
            readinessProbe: {
              tcpSocket: {
                port: servicePort
              },
              initialDelaySeconds: 5,
              periodSeconds: 10,
              timeoutSeconds: 2,
            },
            livenessProbe: {
              tcpSocket: {
                port: servicePort,
              },
              initialDelaySeconds: 15,
              periodSeconds: 20,
              timeoutSeconds: 1,
            },
            terminationMessagePath: "/dev/termination-log",
          }
        ],
        dnsPolicy: "ClusterFirst",
        restartPolicy: "Always",
        securityContext: {},
        terminationGracePeriodSeconds: 30,
      }
    }
  }
}
```

This is a pretty generic file without most of the specifics we need. Here is the deployment file for the  dev environment:
```
// dev.jsonnet
// This variables are provided by the build job on Jenkins
local version = std.extVar("version");
local configVersion = std.extVar("configVersion");

// A collection of variables set by the dev (that's you). This should be things like the service name, the namespace
// you are deploying to and other service specific values. Centralizing them here makes it easier to see what is set for
// your service and abstracts aways the guts of the k8s deployment files.
local devSettings = import "shared/dev.libsonnet";

// Use the imported libsonnet module here to set these variables. This just makes it more convient to see what is being
// used in each file. In the event you want to swap in a new value for testing purposes without you can do it here in
// one palce. Some of these values can be used several times in a single file and only having to update one place makes
// mistakes less likely.
local service = devSettings.serviceName;
local namespace = devSettings.namespace;
local ecrRepoAccount = devSettings.ecrRepoAccount;
local ecrRepoBase = devSettings.ecrRepoBase;
local iamRole = devSettings.iamRole;
local numReplicas = devSettings.numReplicas;
local numReplicas = devSettings.numReplicas;
local maxReplicas = devSettings.maxReplicas;
local minReplicas = devSettings.minReplicas;
local targetCPUUtilizationPercentage = devSettings.targetCPUUtilizationPercentage;

// If this is the first time you are deploying a k8s service you probably don't need to touch any of this stuff.
// jsonnet will do the work here of gluing all these templates together to create a full k8s deployment. There are more
// keys and values that can be added here to control almost everything about your deployment[citation needed].
{
  "kind": "List",
  "apiVersion": "v1",
  "items":[
    (import "base/deployment.jsonnet") {
      metadata+: {
        name: service,
        namespace: namespace,
        labels+: {
          configVersion: configVersion
        },
      },
      spec+: {
        replicas: numReplicas,
        template+: {
          metadata+: {
            labels+: {
              configVersion: configVersion,
              version: version
            },
            annotations: {
              "iam.amazonaws.com/role": iamRole
            }
          },
          spec+: {
            containers: [
              super.containers[ 0 ] + {
                name: service,
                image: "%s/%s/%s:%s" % [ ecrRepoAccount, ecrRepoBase, service, version ],
                resources: {
                  limits: {
                    cpu: cpuLimit,
                    memory: memoryLimit
                  },
                  requests: {
                    cpu: cpuRequest,
                    memory: memoryRequest
                  }
                }
              }
            ]
          }
        }
      }
    },
    (import "base/service.jsonnet") {
      metadata+: {
        namespace: namespace,
      },
    },
    (import "base/hpa.jsonnet") {
      metadata+: {
        namespace: namespace,
      },
      spec+: {
        maxReplicas: maxReplicas,
        minReplicas: minReplicas,
        targetCPUUtilizationPercentage: targetCPUUtilizationPercentage,
      },
    },
  ]
}
```

We will also need files for the k8s service, HPA and configmap.
The tools team has created a `cookiecutter` template for creating the files so you don't have
to do too much to get up and running.

## Dockerfiles and Build Scripts
Couldn't talk about k8s without talking about Docker. Kubernetes allows us to take our containers and
 easily deploy them to multiple environments with a single deployment strategy. It's possible to deploy
 to Kubernetes without setting things up in this specific way. This is just how our tools are setup atm.

### Base Docker Image
To improve build times we will take heavy advantage of Docker layering. We add our code at the last step
so we can use Dockers caching system to make our builds as fast as possible. To do this we will make use of 3
images. The lowest image will be a base image that will have our language and runtime installed as these
 are unlikely to change over time so we will put them at the bottom of our layers. The tools team has provided
 several of these base images for us to use. Thanks Nic <3 :-( ! So unless you are introducing a new language
 or new version of a language you won't need to worry about this but I'll include and example here for completeness.

```
# This Dockerfile is used by Jenkins to create a runtime Docker image.
# See: https://offerup.atlassian.net/wiki/display/OPS/Service+Dockerfiles

FROM python:3.5
MAINTAINER Nick Turner <nick.turner@offerupnow.com> # :-(

RUN mkdir -p /offerup
WORKDIR /offerup
```

So these images are very basic as you can see. It pulls from the official Python image for 3.5 and creates
 an empty directory for our code to live in.

Next we will build a base image for our service. This will likely be an empty Dockerfile but this is simply to give
us a place to put some service specific configuration like installing system packages that won't need to be
reinstalled on every build. For this particular service we don't have any of those so our file is empty:

```
FROM 735354846484.dkr.ecr.us-east-1.amazonaws.com/base/python3.5
MAINTAINER Ian Auld <ian.auld@offerupnow.com>
```

If we needed to install something like `lib-jpeg` or `uwsgi` this is the place we would do it.

There is a Jenkins job to create this base image for us called

### Service Dockerfile
Now we need to build an image that contains our application. This is another simple Dockerfile without much going on:

```
FROM 735354846484.dkr.ecr.us-east-1.amazonaws.com/master/todo-k8s:base-20170704010456-41-8f2b4e75
MAINTAINER Ian Auld <ian.auld@offerupnow.com>

COPY todo-k8s-server.pex /offerup/todo-k8s-server.pex
```

And that's it! Sort of.

You might be saying where does the PEX come from? Great question, there are a couple of glue scripts we will
need to make use of the Jenkins jobs that put everything in the right place.


### Scripts
The are a couple of scripts we will need to have so the Jenkins job knows what to do. So in your services scripts directory
you will need:

 - pre_container_base_build.sh
 - build_server.sh
 - pre_container_build.sh

These scripts are also very simple and will likely only contain a couple of commands (if any).

#### pre_container_base_build
This script will run as part of the `service_base_container_build` job in Jenkins. You will likely only run this job
a few times at the creation of your service.

We don't need anything for the base image for this particular service so our script is just:

```
#!/bin/bash

MONOREPO="$(dirname $0)/../.."
```

However some services may want or need other files to be in the Docker build context for their base image. For example,
 Python/uWSGI services can copy the `utils/bootstrap.py` script in to the context with this script.

 > *Note: The reason we need to move files in to the service dir is because Docker won't allow you to copy files into an
 image if the file is above the Dockerfile in the file system. So anything that comes from somewhere else will need to be copied in at build time.*

#### build_server
A simple script run as part of the `build3` job to create our binary:

```
#!/usr/bin/env bash
 set -e
 set -x

PEX_VERBOSE=5 PEX_PYTHON=python3 ./pants binary services/todo-k8s/src/python:todo-k8s-server
```

This should look pretty familiar to everyone. This creates the binary that is used in the next step.

#### pre_container_build
This script also runs as part of the `build3` job on Jenkins. This is also a very simple script:

```
#!/bin/bash

MONOREPO="$(dirname $0)/../../.."

pushd $MONOREPO
cp dist/nanocontext_server_bootstrap.pex services/nanocontext/
popd
```

This just brings our binary in to the Docker build context.


## Terraform

## Deploy
