# Project setup - Linux distros

Installation steps for Linux distros.

!!! abstract "Tested on Ubuntu and Fedora distros"

## Install Docker Engine

Install the [Docker Engine](https://docs.docker.com/engine/install/).

The procedures for [Ubuntu](https://docs.docker.com/engine/install/ubuntu/) and [Fedora](https://docs.docker.com/engine/install/fedora/) are shown below (copied from the Docker documentation page).

=== "Ubuntu"

    Set up Docker's `apt` repository

    ```bash
    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    ```

    Install the Docker packages.

    ```bash
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```

=== "Fedora"
    
    Install the `dnf-plugins-core` package (which provides the commands to manage your DNF repositories) and set up the repository.

    ```bash
    sudo dnf -y install dnf-plugins-core
    sudo dnf-3 config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
    ```

    Install the Docker packages.

    ```bash
    sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```

    !!! info
        If prompted to accept the GPG key, verify that the fingerprint matches `060A 61C5 1B55 8A7F 742B 77AA C52F EB6B 621E 9F35`, and if so, accept it.

        This fingerprint might update! Check it out [here](https://docs.docker.com/engine/install/fedora/#install-docker-engine).

### Linux postinstall instructions

Docker provides some [instructions](https://docs.docker.com/engine/install/linux-postinstall/) regarding the docker user group.

Create the docker group:

```bash
sudo groupadd docker
```

Add your user to the docker group:

```bash
sudo usermod -aG docker $USER
```

Log out and log back in so that your group membership is re-evaluated.

*You can also run the following command to activate the changes to groups:*

```bash
newgrp docker
```

Check if you can use `docker images` for example, without `sudo` in a new terminal. If not, restart you computer or try again with `newgrp docker`. 

## Add user to dialout group

To be able to register data from USB devices, the user needs to be added to the dialout group:

```bash
sudo usermod -aG dialout $USER
```

Log out and log back in so that your group membership is re-evaluated.

## Setup the software

### Pull the project docker image

Open a terminal and pull the [project docker image](https://hub.docker.com/r/aaronrpb/force-platform-app):

```bash
docker pull aaronrpb/force-platform-app
```

### Run a new docker container

Connect your sensors, check if the `/dev/bus/usb` (and `/dev/ttyUSB*` in case you have Taobotics IMUs) paths exists and create a new container where the software will be running, with:

```bash
docker run -d --name example_app \
  --device /dev/bus/usb \
  --device /dev/ttyUSB0 \
  --device /dev/ttyUSB1 \
  -p 8501:8501 \
  aaronrpb/force-platform-app
```

!!! note
    - You can change the name example_app to any name you prefer.
    - If you have no sensors of USB devices connected, the `/dev/bus/usb` and/or `/dev/ttyUSB*` could be empty, and the docker daemon will throw a `no such file or directory` error.
    - You can ignore some `--device` flags if you are not using Taobotics IMUs (`/dev/ttyUSB*`).

Check if the container is running, going to [http://localhost:8501/](http://localhost:8501/) and try to connect your sensors.

!!! info "You will need to upload a custom configuration file with proper usb paths."

To stop or escape the software, use:

```bash
docker stop example_app
```

### Customize your container settings

It is possible to attach a local configuration file instead of the default internal from the image, by using a [volume](https://docs.docker.com/engine/storage/bind-mounts/):

```bash hl_lines="4"
docker run -d --name example_app \
  --device /dev/bus/usb \
  --device /dev/ttyUSB0 \
  --volume $(pwd)/local_config.yaml:/app/config.yaml \
  -p 8501:8501 \
  aaronrpb/force-platform-app
```

This will store any changes or configuration uploads to your local file. If you stop or delete the container, the file will not be affected.

Also, if you want to use symlinks for the Taobotics IMUs instead of the device ID, you can share those as volumes:

```bash hl_lines="4 5"
docker run -d --name example_app \
  --device /dev/bus/usb \
  --device /dev/ttyUSB0 \
  -v /dev:/dev \
  -v /run/udev:/run/udev:ro \
  -p 8501:8501 \
  aaronrpb/force-platform-app
```

=== "With symlinks"

    IMUs are searched by serial paths instead of USB-ID, avoiding reconnection issues.

    ```bash hl_lines="6"
      imu_1:
        name: Example
        type: SENSOR_IMU
        read: true
        connection:
          serial: /dev/serial/by-path/pci-0000:03:00.4-usb-0:1.4.1:1.0-port0
    ```

=== "Without symlinks"
    
    If IMUs are disconnected, their USB-ID value may change when reconnected.

    ```bash hl_lines="6"
      imu_1:
        name: Example
        type: SENSOR_IMU
        read: true
        connection:
          serial: /dev/ttyUSB0
    ```

## Software usage instructions

Follow these steps to ensure proper sensor connectivity and optimal software functionality.

For more information about the software app features, check out the documentation within the software, at the homepage.

### Start

1. Connect sensors to PC.
2. Start the docker container using the `docker start <container_name>` command in a terminal.
3. Open the software app url ([http://localhost:8501/](http://localhost:8501/)) or other configured port/url.
4. Connect your sensors to the app.
5. Record data, check graphs and download it in `CSV` files.

### Stop

1. Make sure you are not recording data from connected sensors.
2. Stop the docker container using the `docker stop <container_name>` command in a terminal.
3. Disconnect the sensors.

### Update

You can check new updates from the [DockerHub page](https://hub.docker.com/r/aaronrpb/force-platform-app) or the [GitHub repository](https://github.com/AaronPB/force-platform-app).

!!! danger "If you where using a custom configuration file, you will need to upload it again."
    **Download your custom configuration file before removing the docker container.**

    The new updated container will always run with default settings and has no custom configuration file in it.

If you want to update the software to newer versions, follow these steps:

1. Pull the latest docker image: `docker pull aaronrpb/force-platform-app`
2. Remove the previous docker container: `docker container rm <container_name>`
3. Create a new container using the `docker run` command again:

```bash
docker run -d --name example_app \
  --device /dev/bus/usb \
  --device /dev/ttyUSB0 \
  --device /dev/ttyUSB1 \
  -p 8501:8501 \
  aaronrpb/force-platform-app
```