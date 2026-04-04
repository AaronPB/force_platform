<p align="center">
  <a href="#readme"><img alt="Force platform reader logo" src="docs/assets/project_logo_name.png"></a>
</p>
<p align="center">
  <a href="#readme"><img alt="Python tested versions" src="https://img.shields.io/badge/python-3.10_3.11-blue?style=flat-square"></a>
  <a href="https://github.com/psf/black"><img alt="Python formatter" src="https://img.shields.io/badge/code%20style-black-000000?style=flat-square"></a>
  <a href="https://github.com/AaronPB/force_platform/actions/workflows/project_test.yaml"><img alt="Project test status" src="https://img.shields.io/github/actions/workflow/status/AaronPB/force_platform/project_test.yaml?branch=develop&logo=github&label=project_test&style=flat-square"></a>
  <a href="https://aaronpb.github.io/force_platform/"><img alt="Documentation link" src="https://img.shields.io/badge/docs-available-44CC11?logo=materialformkdocs&logoColor=white&style=flat-square"></a>
  <a href="https://squidfunk.github.io/mkdocs-material/"><img alt="MkDocs material theme support" src="https://img.shields.io/badge/Material_for_MkDocs-526CFE?style=flat-square"></a>
</p>

## Information

A python software for synchronized data management of specific force platforms sensors compatible with Phidget API and other sensor types such as IMUs.

This project is part of the author's master's thesis in industrial engineering at the University of Almería. force_platform is licensed under de GNU General Public License v3.0.

![Main UI](docs/images/mainUI.png)

It supports currently the following sensor types:

- Phidget-Bridge compatible load sensors. (Requires Phidget dependency).
- Phidget encoders. (Requires Phidget dependency).
- Taobotics IMU sensors. (Requires MRPT dependency).
- USB webcams for video recording with opencv.

## Documentation

Program documentation is available to learn how the program works and its usage.

Check it out [here](https://aaronpb.github.io/force_platform/).

## Quick setup

> [!note]
> There is a simplified and **dockerized** version of the software!
>
> [Check it out in this repository](https://github.com/AaronPB/force-platform-app)

Install the dependencies and clone the project into your workspace.

> [!WARNING]\
> The project has been developed and tested in Ubuntu 22.04 LTS. Phidget does support [Windows](https://www.phidgets.com/docs/OS_-_Windows#Quick_Downloads) and [MacOS](https://www.phidgets.com/docs/OS_-_macOS#Quick_Downloads), but Taobotics IMUs do not.

### Phidget dependency

```bash
curl -fsSL https://www.phidgets.com/downloads/setup_linux | sudo -E bash - &&\
sudo apt-get install -y libphidget22
```

> Phidget documentation of the [Linux Installer](https://www.phidgets.com/docs/OS_-_Linux#Quick_Downloads).

### MRPT dependency

```bash
sudo add-apt-repository ppa:joseluisblancoc/mrpt &&\
sudo apt install libmrpt-dev mrpt-apps &&\
sudo apt install python3-pymrpt
```

> For more information, refer to the [MRPT Documentation](https://docs.mrpt.org/reference/latest/download-mrpt.html#debian-ubuntu-ppa).

### Project requirements

This project uses [UV](https://docs.astral.sh/uv/), a very powerfull tool to setup and manage python projects.

Install UV:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone the `force_platform` repository and install the project requirements.

Clone using the web URL:

```bash
git clone https://github.com/AaronPB/force_platform.git
```

Or clone with SSH:

```bash
git clone git@github.com:AaronPB/force_platform.git
```

Install the project requirements, going to the project's folder and entering:

```bash
uv venv &&\
uv pip install -r uv.lock
```

> [!WARNING]\
> MRPT cannot be installed by pip. As a temporary solution, set `include-system-site-packages = true` in your `.venv/pyvenv.cfg` file.

### Run the sofware

Run it using the following command:

```bash
uv run python main.py
```

## Citation

If you use this software, please cite this work using the following BibTeX citation:

```bibtex
@article{POYATOSBAKKER2026120933,
title = {An affordable open-source 3D force platform and a wide force range calibration method},
journal = {Measurement},
volume = {271},
pages = {120933},
year = {2026},
issn = {0263-2241},
doi = {https://doi.org/10.1016/j.measurement.2026.120933},
url = {https://www.sciencedirect.com/science/article/pii/S0263224126006421},
author = {Aarón-Raúl Poyatos-Bakker and Javier López-Martínez and Daniel García-Vallejo and José M. Muyor and José-Luis Blanco-Claraco},
keywords = {Force platform, Ground reaction forces, Open software, In-situ calibration, Calibration matrix, Biomechanical analysis}
}
```

## Acknowledgements

This work has been funded by the "[Programa Operativo FEDER 2014-2020](https://www.miteco.gob.es/es/ministerio/servicios/ayudas-subvenciones/fondos_feder.html)" and the Andalusian "Consejería de Transformación Económica, Industria, Conocimiento y Universidades", under the project UAL2020-CTS-A2100.

<p align="center">
  <a href="https://www.miteco.gob.es/es/ministerio/servicios/ayudas-subvenciones/fondos_feder.html"><img alt="EU and Junta de Andalucia logos" src="docs/assets/union_europea-junta_de_andalucia.png" width="500"></a>
</p>
