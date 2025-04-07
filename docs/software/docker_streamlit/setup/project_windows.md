# Project setup - Windows

Installation steps for Windows.

!!! abstract "Tested on Windows 11"

It is possible to run the software in Windows, with a few extra steps.

## Install Docker Desktop

!!! warning "Virtualization needs to be enabled"

    Check first if the PC has virtualization enabled.

    1. Open the `Task Manager`.
    2. Go to the performance tab and click on the CPU graph.
    3. Check the `Virtualization` option at the bottom-right corner. It needs to be `enabled` or Docker will not run.

    Not enabled? Try [these instructions](https://support.microsoft.com/en-us/windows/enable-virtualization-on-windows-c5578302-6e43-4b4b-a449-8ced115f58e1) from Windows Support.

Download [Docker Desktop](https://www.docker.com/products/docker-desktop/) and follow the [interactive installation](https://docs.docker.com/desktop/setup/install/windows-install/#install-docker-desktop-on-windows).

## Install usbipd

This is needed to attach the USB sensors to the Windows Subsystem for Linux (WSL).

Open a terminal in administrator mode (right click and `run as administrator`) and install the [usbipd software](https://github.com/dorssel/usbipd-win) using the following command:

```bash
winget install usbipd
```

Maybe a confirmation window will pop up, follow the instructions and wait until it finishes.

## Setup the software

### Pull the project docker image

Open a new terminal (or use the previous one) and pull the [project docker image](https://hub.docker.com/r/aaronrpb/force-platform-app):

```bash
docker pull aaronrpb/force-platform-app
```

### Run a new docker container

Create a new container where the software will be running, with:

```bash
docker run -d --name example_app --privileged -p 8501:8501 aaronrpb/force-platform-app
```

!!! note
    - You can change the name example_app to any name you prefer.

    - Currently, it is necessary to use the `--privileged` flag. This is required to allow WSL to recognize the connected sensors, and unfortunately, there's no known workaround at this time.

Check if the container is running, going to [http://localhost:8501/](http://localhost:8501/).

*Do not try to connect sensors, it won't work unless we bind them to WSL. This is the last step.*

If the streamlit web-app is showing, stop the container with:

```bash
docker stop example_app
```

Or stop it from the Docker Desktop window, going to the Containers tab and clicking the stop icon.

## Attach the USB sensors to WSL

Before starting the docker container, you will need to attach the sensors to WSL.
Connect them to the PC and follow the steps.

### Identify the sensors

Open a terminal in administrator mode and check the connected usbs with `usbipd`:

```bash
usbipd list
```

This will show up something like the following list:

```
Connected:
BUSID  VID:PID    DEVICE                                                        STATE
4-11   0db0:422d  Realtek USB2.0 Audio, Dispositivo de entrada USB              Not shared
4-12   0e8d:0616  RZ616 Bluetooth(R) Adapter                                    Not shared
4-15   1462:7d75  Dispositivo de entrada USB                                    Not shared
6-1    1532:0084  Razer DeathAdder V2, Dispositivo de entrada USB               Not shared
6-2    1b1c:1b40  Dispositivo de entrada USB                                    Not shared
7-1    06c2:003b  Dispositivo de entrada USB                                    Not shared
7-2    b58e:9e84  Yeti Stereo Microphone, Dispositivo de entrada USB            Not shared

Persisted:
GUID                                  DEVICE

```

Identify the `BUSID` and the `VIP:PID` from the sensors. This will be used for the bind/attach commands and WSL usb checks.

For example, in the provided list, `BUSID 7-1` corresponds to a PhidgetBridge USB connection with four loadcell sensors.

!!! question "If you have more than one USB connection, repeat the following steps for all sensors."

### Bind the sensors

All the sensors we want to attach have to be binded first, with the `--busid` flag:

```bash
usbipd bind --busid 7-1
```

Now if we check the list again with `usbipd list`, bus `7-1` will be `Shared` at the `STATE` column:

``` hl_lines="8"
Connected:
BUSID  VID:PID    DEVICE                                                        STATE
4-11   0db0:422d  Realtek USB2.0 Audio, Dispositivo de entrada USB              Not shared
4-12   0e8d:0616  RZ616 Bluetooth(R) Adapter                                    Not shared
4-15   1462:7d75  Dispositivo de entrada USB                                    Not shared
6-1    1532:0084  Razer DeathAdder V2, Dispositivo de entrada USB               Not shared
6-2    1b1c:1b40  Dispositivo de entrada USB                                    Not shared
7-1    06c2:003b  Dispositivo de entrada USB                                    Shared
7-2    b58e:9e84  Yeti Stereo Microphone, Dispositivo de entrada USB            Not shared

Persisted:
GUID                                  DEVICE

```

### Attach the binded sensors

Once the sensors are with the `Shared` state, attach them to WSL with:

```bash
usbipd attach --wsl --busid 7-1
```

This will trigger the Windows USB unplug sound and also show some information in the command line from `usbipd`:

```
usbipd: info: Using WSL distribution 'docker-desktop' to attach; the device will be available in all WSL 2 distributions.
usbipd: info: Detected networking mode 'nat'.
usbipd: info: Using IP address 172.28.48.1 to reach the host.
usbipd: info: Firewall check not possible with this distribution (no bash, or wrong version of bash).

```

### Check WSL USB lists

From the same terminal, enter to WSL (Docker Desktop must be open):

```bash
wsl
```

Check the connected usbs with `lsusb`:

```bash
lsusb
```

Something like the following will show up. Identify the connected sensors by their `ID` (those are the `VIP:PID` tags shown with `usbipd list`).

``` hl_lines="2"
Bus 001 Device 001: ID 1d6b:0002
Bus 001 Device 002: ID 06c2:003b
Bus 002 Device 001: ID 1d6b:0003
```

In this example we can check that the PhidgetBridge is correctly attached.
The `VIP:PID` was `06c2:003b`, this corresponds with `Bus 001 Device 002`.

!!! success "If you see all your sensors listed, they are correctly attached!"

!!! warning "Are you connecting Taobotics IMUs?"
    To connect Taobotics IMUs you will need to do an extra step inside WSL. Check first if WSL has automatically assigned your IMUs to `ttyUSB` ports:

    ```bash
    ls /dev/ttyUSB*
    ```
    
    If it shows `No such file or directory`, your IMU drivers are not being recognized. You will need to load the kernel module `cp210x` for USB to UART Bidge usbs. Do not be scared, it is only one command inside WSL:

    ```bash
    modprobe cp210x
    ```

    Now if you check again with `ls /dev/ttyUSB*` you will see the recognized IMUs!

### Detach and unbind sensors

It is not necessary to detach and unbind every time you want to disconnect the USB sensors from WSL.
This is only needed if you want to release the device from WSL so that it is no longer in use, and Windows can take control of it again.

```bash
usbipd detach --busid 7-1
usbipd unbind --busid 7-1
```

## Software usage instructions

Follow these steps to ensure proper sensor connectivity and optimal software functionality.

For more information about the software app features, check out the documentation within the software, at the homepage.

### Start

1. Open Docker Desktop.
2. Connect sensors to PC.
3. Check in they are attached to WSL.
4. Start the docker container from the Containers tab on Docker Desktop, or use the `docker start <container_name>` command in a terminal.
5. Open the software app url ([http://localhost:8501/](http://localhost:8501/)) or other configured port/url.
6. Connect your sensors to the app.
7. Record data, check graphs and download it in `CSV` files.

### Stop

1. Make sure you are not recording data from connected sensors.
2. Stop the docker container from the Containers tab on Docker Desktop, or use the `docker stop <container_name>` command in a terminal.
3. Disconnect the sensors or detach/unbind them (this is optional).

### Update

You can check new updates from the [DockerHub page](https://hub.docker.com/r/aaronrpb/force-platform-app) or the [GitHub repository](https://github.com/AaronPB/force-platform-app).

!!! danger "If you where using a custom configuration file, you will need to upload it again."
    **Download your custom configuration file before removing the docker container.**

    The new updated container will always run with default settings and has no custom configuration file in it.

If you want to update the software to newer versions, follow these steps:

1. Open Docker Desktop and go to the Images tab. Click in the three vertical dots on the `aaronrpb/force-platform-app` actions column and click on the `Pull` option.
2. When updated, go the the Containers tab and remove the app container.
3. Create a new container opening a terminal and running the following command:

```bash
docker run -d --name example_app --privileged -p 8501:8501 aaronrpb/force-platform-app
```