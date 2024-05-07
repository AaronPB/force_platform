[:house: `Back to Home`](../home.md)

# Project setup

The installation process will be explained for **Linux**. It is also possible to install on Windows and MacOs (not tested) if the required dependencies have support for those OS.

> [!NOTE]
> Please note that if you do not use Linux and you want to use the Taobotics IMUs, you will have to manage its drivers.

The project has been tested in `Windows 11` without IMUs, and in `Ubuntu 12.04 LTS` with Taobotics IMUs.

## Dependencies

- **Python version `3.10` or `3.11`**. In case you want to use recent versions, check the [requirements](../../requirements.txt) for potential conflicts with the required python modules.
- **Phidget22**. For Phidget load cells and encoders.
- **MRPT**. To use the `pymrpt` library for the Taobotics IMUs.

## Installation procedure

### 1. Clone the repository

Clone the `force_platform` repository:

```bash
git clone git@github.com:AaronPB/force_platform.git
```

### 2. Install python required modules

Install the project requirements:

```bash
cd force_platform/
pip install -r requirements
```

### 3. Install sensor dependencies

#### Phidget dependency

For [Linux](https://www.phidgets.com/docs/OS_-_Linux#Quick_Downloads):

```bash
curl -fsSL https://www.phidgets.com/downloads/setup_linux | sudo -E bash - &&\
sudo apt-get install -y libphidget22
```

> For [Windows](https://www.phidgets.com/docs/OS_-_Windows#Quick_Downloads) or [MacOS](https://www.phidgets.com/docs/OS_-_macOS#Quick_Downloads)

#### MRPT dependency

For more information, refer to the [MRPT Documentation](https://docs.mrpt.org/reference/latest/download-mrpt.html#debian-ubuntu-ppa)

```bash
sudo add-apt-repository ppa:joseluisblancoc/mrpt
sudo apt install libmrpt-dev mrpt-apps
sudo apt install python3-pymrpt
```

> [!WARNING]
> If you are using `virtualenv` (or any other virtual environment), MRPT cannot be installed by pip. As a temporary solution, set `include-system-site-packages = true` in your `pyvenv.cfg` file.

## Run the project

When all dependencies are installed, try to run the `main.py` file in the `force_platform` repository from IDE or a terminal:

```bash
cd force_platform/
chmod +x main.py
main.py
```

If the main GUI shows up, its done!

---

[:house: `Back to Home`](../home.md)