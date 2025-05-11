# Project setup

The project has been tested in `Windows 11` without IMUs, and in `Ubuntu 22.04 LTS` with Taobotics IMUs.

The installation process will be explained for **Linux** as the current project version includes Taobotics IMUs support and Windows does not manage its drivers properly.

!!! tip "Try the dockerized version tested in Windows 11 and Linux distros Ubuntu and Fedora"
    A simplified docker version is available and fully compatible with all the sensors, including also Taobotics IMUs in Windows!

    [:fontawesome-solid-download: Detailed docker setup steps for Windows 11](../../docker_streamlit/setup/project_windows.md){ .md-button .md-button--secondary }

## Dependencies

- **Phidget22**. For Phidget load cells and encoders.
- **MRPT**. To use the `pymrpt` library for the Taobotics IMUs.
- **UV**. To manage the python project. This is optional but highly recommended.

## Installation procedure

### 1. Clone the repository

Clone the `force_platform` repository.

Clone using the web URL:
```bash
git clone https://github.com/AaronPB/force_platform.git
```

Clone with SSH:
```bash
git clone git@github.com:AaronPB/force_platform.git
```

### 2. Install sensor dependencies

#### Phidget dependency

```bash
curl -fsSL https://www.phidgets.com/downloads/setup_linux | sudo -E bash - &&\
sudo apt-get install -y libphidget22
```

> Phidget documentation of the [Linux Installer](https://www.phidgets.com/docs/OS_-_Linux#Quick_Downloads).

#### MRPT dependency

```bash
sudo add-apt-repository ppa:joseluisblancoc/mrpt &&\
sudo apt install libmrpt-dev mrpt-apps &&\
sudo apt install python3-pymrpt
```

> For more information, refer to the [MRPT Documentation](https://docs.mrpt.org/reference/latest/download-mrpt.html#debian-ubuntu-ppa).

### 3. Install UV and setup the project requirements

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install the project requirements:

```bash
cd force_platform/ &&\
uv venv &&\
uv pip install -r uv.lock
```

!!! warning
    MRPT cannot be installed by pip. As a temporary solution, set `include-system-site-packages = true` in your `.venv/pyvenv.cfg` file.

## Run the project

When all dependencies are installed, try to run the `main.py` file in the `force_platform` repository from a terminal using uv:

```bash
uv run python main.py
```

If the main GUI shows up, it is done!
