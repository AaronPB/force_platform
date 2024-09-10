[:house: `Back to Home`](../home.md)

# Project setup with docker

## Linux distro

### 1. Install docker

Install the [desktop version](https://www.docker.com/products/docker-desktop/) or `docker.io`:

```bash
sudo apt-get update
sudo apt install docker.io -y
```

### 2. Install git and clone the repository

Install `git`:

```bash
sudo apt-get update
sudo apt install git -y
```

Clone the `force_platform` repository:

```bash
git clone git@github.com:AaronPB/force_platform.git
```

### 3. Build docker image and run the container

Move into the cloned repository:

```bash
cd force_platform
```

Build a docker image from the `Dockerfile` file:

```bash
docker build -tag force_platform .
```

Run a new container called `force_platform_app`:

```bash
docker run --name force_platform_app -p 8501:8501 --privileged -v /dev:/dev force_platform
```

### 4. Start and stop the container

To stop the app, simply interrupt the process with `ctrl+c`. This will also stop the container.

To run the container again, instead of `docker run`, run the following command:

```bash
docker start force_platform_app
```

> [!TIP]
> If you want to modify the container arguments, you need to remove the container and run it again.
>
> ```bash
> docker container rm force_platform_app
> docker run --name force_platform_app -p 8501:8501 [other_options]
> ```

## Windows

TODO

## MacOS

TODO

# Development container

The project has also a `Dockerfile.dev` file along with a `requirements-dev.txt`file to setup a [devcontainer environment with Visual Studio Code](https://code.visualstudio.com/docs/devcontainers/containers).

An example of a valid `devcontainer.json` for this project:

```json
{
    "name": "force_platform",
    "build": {
      "dockerfile": "../Dockerfile.dev",
      "context": ".."
    },
    "runArgs": [
      "--privileged", // Necessary to access multiple serial ports
      "-v", "/dev:/dev" // To access all USB dirs
      // Replace --privileged and total volume access with this line, to put only specific routes.
      // Requires to put manually all sensor ports.
      // "--device=/dev/ttyUSB0"
    ],
    // Configure tool-specific properties.
    "customizations": {
      // Configure properties specific to VS Code.
      "vscode": {        
        // Add the IDs of extensions you want installed when the container is created.
        "extensions": [
          "ms-python.black-formatter",
          "ms-python.vscode-pylance",
          "ms-python.python",
          "ms-python.debugpy",
          "naumovs.color-highlight",
          "davidanson.vscode-markdownlint"
        ]
      }
    }
  }
```