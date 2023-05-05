# Force Platform Data Reader

## Information
A python script for sensor data management of a force platform.

It supports currently the following sensor types:
- Phidget-Bridge compatible load sensors.

## Setup
To use this project, clone it and install the project requirements.
> Do it in a virtual environment to avoid module installation issues (using `virtualenv`, for example).
> 
> This project is developed with Python v3.10.6

Project requirements:
```bash
pip install -r requirements.txt
```

Download Phidget dependency:
For [Linux](https://www.phidgets.com/docs/OS_-_Linux#Quick_Downloads):
```bash
curl -fsSL https://www.phidgets.com/downloads/setup_linux | sudo -E bash - &&\
sudo apt-get install -y libphidget22
```
> For [Windows](https://www.phidgets.com/docs/OS_-_Windows#Quick_Downloads) or [MacOS](https://www.phidgets.com/docs/OS_-_macOS#Quick_Downloads)