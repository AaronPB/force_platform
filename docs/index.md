---
hide:
  - navigation
  - toc
title: Home
---
#
<figure markdown="span">
![project_logo_name](assets/project_logo_name.png)
</figure>
<br>
<div class="grid cards" markdown>

-   :fontawesome-solid-truck-fast:{ .lg .middle } __Set up in 10 minutes__

    ---

    Install the dependencies ([`Phidget22`](https://www.phidgets.com/docs/Phidget22?srsltid=AfmBOorPWIP_i6m9MabFbrDAVYYXTi3JjgvsbhZHfs7VnlNO6sR47uO3) [`MRPT`](https://docs.mrpt.org/reference/latest/download-mrpt.html)), the [project](https://github.com/AaronPB/force_platform/tree/master)
    and get up and running in minutes

    [:octicons-arrow-right-24: Getting started](setup/project.md)

-   :fontawesome-solid-microchip:{ .lg .middle } __Sensor compatibility__

    ---

    The Phidget [Load Cell](https://www.phidgets.com/?tier=2&catid=98&pcid=78) and [Encoder](https://www.phidgets.com/?tier=1&catid=4&pcid=2) interfaces are compatible with a wide range of sensors

    [:octicons-arrow-right-24: More information](setup/sensors.md)

-   :fontawesome-solid-gear:{ .lg .middle } __Highly configurable__

    ---

    Sensors are defined into group types, working in a modular and flexible way

    [:octicons-arrow-right-24: Configuration file](setup/config_file.md)

-   :fontawesome-solid-file-csv:{ .lg .middle } __Data recording and CSV export__

    ---

    It supports sampling rates up to 100 Hz and CSV data export, with or without sensor calibration parameters

-   :fontawesome-solid-sliders:{ .lg .middle } __Calibration feature__

    ---

    It includes an interactive calibration panel to adjust sensor calibration parameters

    [:octicons-arrow-right-24: Calibrate sensors](usage/calibration_test.md)

-   :fontawesome-solid-scale-balanced:{ .lg .middle } __Open Source, GPL-3.0__

    ---

    The software is licensed under the GNU GPL-3.0 and available on [GitHub](https://github.com/AaronPB/force_platform)

    [:octicons-arrow-right-24: License](https://github.com/AaronPB/force_platform/blob/develop/LICENSE)

</div>

## The project

!!! abstract "Talk about the project"

## Quick setup

Install the dependencies and clone the project into your workspace.

### Phidget dependency

For [Linux](https://www.phidgets.com/docs/OS_-_Linux#Quick_Downloads):

```bash
curl -fsSL https://www.phidgets.com/downloads/setup_linux | sudo -E bash - &&\
sudo apt-get install -y libphidget22
```

> For [Windows](https://www.phidgets.com/docs/OS_-_Windows#Quick_Downloads) or [MacOS](https://www.phidgets.com/docs/OS_-_macOS#Quick_Downloads)

### MRPT dependency

For more information, refer to the [MRPT Documentation](https://docs.mrpt.org/reference/latest/download-mrpt.html#debian-ubuntu-ppa)

```bash
sudo add-apt-repository ppa:joseluisblancoc/mrpt
sudo apt install libmrpt-dev mrpt-apps
sudo apt install python3-pymrpt
```

!!! warning
    If you are using `virtualenv`, MRPT cannot be installed by pip. As a temporary solution, set `include-system-site-packages = true` in your `pyvenv.cfg` file.

### Project requirements

Clone the `force_platform` repository and install the project requirements.

Clone using the web URL:
```bash
git clone https://github.com/AaronPB/force_platform.git
```

Clone with SSH:
```bash
git clone git@github.com:AaronPB/force_platform.git
```

Project requirements:
```bash
pip install -r requirements.txt
```

!!! tip
    Do it in a virtual environment to avoid module installation issues (using `virtualenv`, for example).

    This project is developed with Python v3.10.6
