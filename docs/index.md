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

    Get up and running in minutes

    [:fontawesome-brands-linux: Install the legacy version](software/legacy_qt/index.md)
    
    [:fontawesome-brands-docker: Install the docker version](software/docker_streamlit/index.md) [(DockerHub repo)](https://hub.docker.com/r/aaronrpb/force-platform-app)

-   :fontawesome-solid-microchip:{ .lg .middle } __Sensor compatibility__

    ---

    The Phidget [Load Cell](https://www.phidgets.com/?tier=2&catid=98&pcid=78) and [Encoder](https://www.phidgets.com/?tier=1&catid=4&pcid=2) interfaces are compatible with a wide range of sensors

    [:octicons-arrow-right-24: More information](software/legacy_qt/setup/sensors.md)

-   :fontawesome-solid-gear:{ .lg .middle } __Highly configurable__

    ---

    Sensors are defined into group types, working in a modular and flexible way

    [:octicons-arrow-right-24: Configuration file](software/legacy_qt/setup/config_file.md)

-   :fontawesome-solid-file-csv:{ .lg .middle } __Data recording and CSV export__

    ---

    It supports sampling rates up to 100 Hz and CSV data export, with or without sensor calibration parameters

-   :fontawesome-solid-sliders:{ .lg .middle } __Calibration feature__

    ---

    It includes an interactive calibration panel to adjust sensor calibration parameters

    [:octicons-arrow-right-24: Calibrate sensors](software/legacy_qt/usage/calibration_test.md)

-   :fontawesome-solid-scale-balanced:{ .lg .middle } __Open Source, GPL-3.0__

    ---

    The software is licensed under the GNU GPL-3.0 and available on [GitHub](https://github.com/AaronPB/force_platform)

    [:octicons-arrow-right-24: License](https://github.com/AaronPB/force_platform/blob/develop/LICENSE)

</div>

## About the Software

<div class="grid" markdown>

<div markdown>
![Software main page](images/fp_software_ui_compact.png)
</div>

<div markdown>
A python software for synchronized data management of specific force platforms sensors compatible with [Phidget API](https://www.phidgets.com/docs/Phidget22?srsltid=AfmBOorPWIP_i6m9MabFbrDAVYYXTi3JjgvsbhZHfs7VnlNO6sR47uO3) and other sensor types such as IMUs.

This project is part of the [author](https://github.com/AaronPB)'s master's thesis in industrial engineering at the University of Almería
and funded by the "[Programa Operativo FEDER 2014-2020](https://www.miteco.gob.es/es/ministerio/servicios/ayudas-subvenciones/fondos_feder.html)" and the Andalusian "Consejería de Transformación Económica, Industria, Conocimiento y Universidades", under the project UAL2020-CTS-A2100.

[:fontawesome-solid-book: &nbsp; More information about the project](platform/index.md){ .md-button .md-button--primary }

<figure markdown="span">
![union_europea-junta_de_andalucia](assets/union_europea-junta_de_andalucia.png#only-light){ width="500px" }
![union_europea-junta_de_andalucia](assets/union_europea-junta_de_andalucia_modooscuro.png#only-dark){ width="500px" }
</figure>

</div>

</div>

### A flexible configuration

<div class="grid" markdown>

<div markdown>
The configuration file uses `YAML` format for better readability, and all sensors are stored in a single configuration section for a more structured setup.

Sensors are then organized into __sensor groups__. If a sensor does not belong to a group, it will be ignored.

!!! success "Sensor groups are fully flexible"
    You can define a group with sensors of the same type or different types.

    Within the program, you can enable or disable specific sensors within a group or an entire group.

For more details, check out the following documentation page:

[:fontawesome-solid-gear: &nbsp; Configuration file](software/legacy_qt/setup/config_file.md){ .md-button .md-button--secondary }
</div>

<div markdown>
=== "Settings section"

    *Just simple and straightforward settings.*
    
    *You can even import customized configuration files with different sensors and group setups.*

    ``` yaml
    settings:
      custom_config_path: null
      test:
        name: Name
        folder_path: /tests/
        results:
          save_raw: true
          save_calib: true
      recording:
        data_interval_ms: 10
        tare_data_amount: 300
      calibration:
        data_interval_ms: 10
        data_amount: 300
    ```

=== "Sensor groups section"
    
    *Group your sensors to get specific graphs based on the group type and enhance data organization in CSV exports.*

    ``` yaml
    sensor_groups:
      imus:
        name: Body IMUs
        type: GROUP_DEFAULT
        read: true
        sensor_list:
        - imu_1
        - imu_2
        - imu_3
      barbell_encoders:
        name: Barbell encoders
        type: GROUP_DEFAULT
        read: true
        sensor_list:
        - encoder_1
        - encoder_2
    ```

=== "Sensors section"
    
    *Define all your sensors in this section.*

    ``` yaml
    sensors:
      encoder_1:
        name: Encoder_Z_1
        type: SENSOR_ENCODER
        read: true
        connection:
          channel: 0
          serial: 641800
        initial_position: 0
        properties:
          serial_number: AAAA
          max_length: 2500mm
        calibration:
          slope: 0.01875
          intercept: 0.0
    ```
</div>

</div>

### Data graphs and CSV export

<div class="grid" markdown>

<div markdown>
![Software tab graphs page](images/fp_software_ui_compact_Pgraph.png)
</div>

<div markdown>

You can visualize the recorded data directly from the graph tabs.

There are graphs for each recorded sensor, as well as specific ones depending on the sensor group type, such as force platforms.

It is also possible to trim the data and adjust the Butterworth filter used for signal processing.

For data export, the CSV format is used, allowing both raw data export and processed data export using the sensors' calibration parameters.

</div>

</div>

## Software versions

<div class="grid" markdown>

<div markdown>

### Legacy version

[:fontawesome-brands-github: GitHub repository](https://github.com/AaronPB/force_platform){ .md-button .md-button--primary }

This version was originally developed for internal use, with Python and QT.

Install the required dependencies and clone the project into your workspace.
You can follow this steps to set it up in a few minutes.

!!! warning "Only Linux distributions are supported, preferably Ubuntu 22.04 LTS"
    The project has been developed and tested in Ubuntu 22.04 LTS. Phidget does support [Windows](https://www.phidgets.com/docs/OS_-_Windows#Quick_Downloads)
    and [MacOS](https://www.phidgets.com/docs/OS_-_macOS#Quick_Downloads), but Taobotics IMUs do not.

<div class="grid cards" markdown>

-   :fontawesome-solid-terminal:{ .lg .middle } __Step 1: Install dependencies, UV and clone the repository__

    ---

    === "Phidget22"

        ``` bash
        curl -fsSL https://www.phidgets.com/downloads/setup_linux | sudo -E bash - &&\
        sudo apt-get install -y libphidget22
        ```

    === "MRPT"

        ``` bash
        sudo add-apt-repository ppa:joseluisblancoc/mrpt &&\
        sudo apt install libmrpt-dev mrpt-apps &&\
        sudo apt install python3-pymrpt
        ```

    === "UV"

        ``` bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```
    
    === "`force_platform` repository"

        ``` bash
        git clone https://github.com/AaronPB/force_platform.git
        ```

-   :fontawesome-solid-file-lines:{ .lg .middle } __Step 2: UV install and run the software__

    ---

    ```bash
    cd to/the/force_platform/repository &&\
    uv venv &&\
    uv pip install -r uv.lock
    ```

    !!! warning "Enable `include-system-site-packages` in `.venv/pyvenv.cfg`"

    ```bash
    uv run python main.py
    ```

</div>
</div>

<div markdown>

### Docker version

[:fontawesome-brands-github: GitHub repository](https://github.com/AaronPB/force-platform-app){ .md-button .md-button--primary }
[:fontawesome-brands-docker: DockerHub](https://hub.docker.com/r/aaronrpb/force-platform-app){ .md-button .md-button--primary }

An optimized and comfortable option, with the main features.

Simple to install using Docker, and with all the documentation available inside the app, ready to go!

!!! success "Available for Windows and Linux distros"
    The project has been tested in Windows 11, Ubuntu 22.04 LTS and Fedora Workstation 41. It has not been tested in MacOS, but it has a high chance to also work, as it is a dockerized version.

<div class="grid cards" markdown>

-   :fontawesome-brands-docker:{ .lg .middle } __Step 1: Run a new docker container__

    ---

    Just a quick `docker run` in your docker environment and you are ready to go!

    === "From DockerHub"

        ``` bash
        docker run -d --name example_app \
            --device /dev/bus/usb \
            --device /dev/ttyUSB0 \
            --device /dev/ttyUSB1 \
            -p 8501:8501 \
            aaronrpb/force-platform-app
        ```

    === "From GHCR"

        ``` bash
        docker run -d --name example_app \
            --device /dev/bus/usb \
            --device /dev/ttyUSB0 \
            --device /dev/ttyUSB1 \
            -p 8501:8501 \
            ghcr.io/aaronpb/force-platform-app
        ```
    
    !!! note "Add or remove arguments depending on your setup. For more information click below."

    [:fontawesome-solid-download: Detailed docker setup steps](software/docker_streamlit/setup/project_linux.md){ .md-button .md-button--secondary }

</div>
</div>

</div>
