:house: <kbd>[Back to Home](../home.md)</kbd>

# Calibration process
**Work in progress**

Previously, you need to connect the sensors you want to calibrate in the main GUI as shown in the following picture.

*TODO image*

Then, click on the `Calibrar células` button on the left panel. This button will be available if at least one of the selected sensors is connected.

## Calibration menu

This menu will replace the main GUI, with the compatible sensors. The appearance of the calibration menu is presented in the following image.

*TODO image*

The menu loads all compatible sensor lists defined in defined in `config.yaml`, but only the connected ones will be enabled.

> If the desired sensor to be calibrated is not enabled, close de calibration menu and try to reconnect the sensors. It needs to get a green check in the sensor information table.

The compatible sensors are:
- Phidget platform loadcells.
- Phidget encoders.

In order to preform a calibration test, click the enabled button of the connected sensor.

## Calibration test of a sensor

A new window will pop up when clicking an enabled sensor button. The displayed GUI is as shown here.

*TODO image*

The window is structured in the following sections:
- A table in which all measurements will be recorded and the most relevant data (such as the mean and variance of the data sample) are displayed.
- An empty field and graph in which the results of the linear regression will be presented.
- A control panel divided into two rows: the first row to manage the calibration test and the second row to exit the submenu.

*TODO Finish explaining the two types of calibration procedures.*

### Calibrate with manual inputs
*WIP*

### Calibrate with calibration sensor input
*WIP*

### Generate the calibration results
Once all measurements have been taken, linear regression can be performed by clicking on the `Calibrar` button.

> A minimum of two measurements must be taken for the `Calibrar` button to be available.

*TODO image*

This will generate a graph with the regression line obtained (in red) and the measurements taken (as blue dots). The values of the line are displayed above the graph.

It is possible to continue measuring and click the `Calibrar` button again to calculate a new regression line taking into account all the values.

### Save or discard the calibration
When the first regression line is calculated the `Guardar y cerrar` button in the second row will be enabled. Click here to close the window and overwrite the sensor calibration values in the config file with the calibration results.

If at any time you wish to cancel the calibration test, click the `Cancelar` button.

---

:house: <kbd>[Back to Home](../home.md)</kbd>