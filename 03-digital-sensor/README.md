# Digital Sensor (SPI and I2C Interface)
> <div align="justify"> This guide will help you to integrate digital sensors such as a gyroscope, accelerometer, temperature, and humidity sensor with a PYNQ board. To be more specific, you will learn to design both hardware and software part that allows performing read and write operation from and to the sensor through a serial peripheral interface (SPI) and inter-integrated circuit (I2C) interface.</div>



## :bookmark_tabs: Table of Content

* [Context](#information_source-context)
* [Background](#mag-background)
* [AXI-based I2C and SPI Interface](#-axi-based-i2c-and-spi-interface)
* [Postprocessing Sensor Data](#question-practice-postprocessing-sensor-data)
* [References](#book-references)



## :information_source: Context

*Created by*: **Dalta Imam Maulana** </br>
*Document Version*: **January 13th, 2023**



## :mag: Background

### Serial Peripheral Interface (SPI)

Serial peripheral interface (SPI) is a synchronous serial communication protocol that commonly used in embedded systems. SPI protocol is based on master-slave architecture with a single master and multiple slave. This multiple slave capability are supported by selecting specific slave to communicate through slave select (SS) line.

In general, SPI bus contains four logic signals:

- `SCLK`: serial clock (output from master)
- `MISO`: master input slave output (output from slave to master)
- `MOSI`: master output slave input (output from master to slave)
- `SS`: slave select (output from master to slave, active low)

To start communication, master device configures the transaction clock using a frequency that is supported by slave device (usually up to few MHz). After that, master selects the slave device by driving slave select (SS) line to logic low. After initial configuration, in each SPI clock cycle, master device sends a bit through MOSI port and slave read the data. In this clock cycle, slave device also sends a bit through MISO port for master device to read it.

The SPI transmission usually involves two shift register, one in each master and slave device which connected to each other in ring topology. Usually, the most significant bit of data is shifted out first from both master and slave device. This shift and send process will continue to run until master device stops sending the clock signal.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/91db9570a2c6f66e5b13f714534b07b04eb42133/03-digital-sensor/resources/spi-interface.png" width="45%" />
</p>

Beside setting clock frequency, master device also need to configure clock polarity (CPOL) and clock phase (CPHA). Clock polarity (CPOL) determines the polarity of clock signal. If CPOL is 0, it means that the clock is idle at 0, the leading edge is a rising edge, and trailing edge is a falling edge. Otherwise, the clock signal idle at 1, falling edge is leading edge, and rising edge is trailing edge of the clock signal.

Meanwhile, clock phase (CPHA) determines the timing of data bits relative to clock signal. If CPHA is 0, the output data will change during trailing edge of preceding clock cycle and input data will be received during next leading edge of clock signal. As for SPI interface with CPHA value of 1, the output data will change during leading edge of clock cycle and input data will be received during trailing edge of the clock cycle [1].

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/91db9570a2c6f66e5b13f714534b07b04eb42133/03-digital-sensor/resources/spi-timing.png" width="45%" />
</p>




### Inter-Integrated Circuit (I2C)

Inter-integrated circuit (I2C) is a multi-master, multi-slave, serial communication protocol which is widely used in embedded systems to connect low speed peripheral devices with processors or microcontrollers. I2C protocol uses two bidirectional open collector or open drain lines which are serial data line (SDA) and serial clock line (SCL). These lines are connected with pull-up resistor and typically the resistor is connected to 5V or 3.3V voltage source.

There are four possible configurations of I2C which are:

- `Master transmit`: master device is sending data to slave device.
- `Master receive`: master device is receiving data from slave device.
- `Slave transmit`: slave device is sending data to master device.
- `Slave receive`: slave device is receiving data from master device.

To begin the transaction, master device sends START signal followed by 7-bit address of the slave device, which then followed by single bit representing whether the master wants to write data (0) or read data (1) from slave. If the slave device exists, it will send back ACK signal bit for that address. After receiving ACK signal from slave, master will continue to read or write data from or to slave. The START signal is usually indicated by high-to-low transition of SDA line with SCL being high. Meanwhile, the STOP signal is indicated by a low-to-high transition of SDA with SCL in high [2].

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/91db9570a2c6f66e5b13f714534b07b04eb42133/03-digital-sensor/resources/i2c-timing.png" width="60%" />
</p>



### MPU6050 - Gyroscope and Accelerometer Sensor

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/91db9570a2c6f66e5b13f714534b07b04eb42133/03-digital-sensor/resources/mpu6050.jpg" width="30%" />
</p>
MPU6050 is a sensor which consists of 3-axis accelerometer and 3-axis gyroscope sensor. This sensor can be used to measure acceleration, velocity, and orientation of an object. This module also contains digital motion processor (DMP) which can perform complex calculation such as sampling and data filtering.

The MPU6050 module support I2C protocol, so that the processor or microcontroller can read data through I2C bus. This module contains 16-bit ADC which is used to read the voltage changes caused by any kind of movements and will store the data in the internal FIFO buffer [3].




### BME280 - Temperature, Pressure, and Humidity Sensor

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/91db9570a2c6f66e5b13f714534b07b04eb42133/03-digital-sensor/resources/bme280.png" width="25%" />
</p>
BME280 is a temperature, humidity, and pressure sensor which can measure relative humidity from 0 to 100% scale with ±3% accuracy, barometric pressure from 300Pa to 1100 hPa with ±1hPa absolute accuracy, and temperature from -40°C to 85°C with accuracy of ±1°C. This sensor supports SPI interface and also contains internal voltage level translator. So, the module can be connected either with 5V or 3.3V supply voltage [4].




## <img style="vertical-align:middle" src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/bc75dd4823e71aa3921d17f8110f6a9771cd9d16/01-intro-to-vivado-and-pynq/resources/chip.png" width="32px" title=":chip:"/> AXI-based I2C and SPI Interface

### Create New Vivado Project and System Block Diagram

To start this section, make a new Xilinx project for PYNQ Z1 board. Make sure to choose the correct board file during the project creation process. After that, create a new block diagram as in the previous project and also add a `ZYNQ Processing System`. Don't forget to run `Connection Automation` after adding `ZYNQ IP Core`.

In this section, you will create a memory-mapped interface that can be accessed from the Python environment. There are many ways to create a memory-mapped interface. But, for this section, you will use one of the General Purpose AXI Interfaces, specifically `Processing System (PS) AXI Master Ports`.

By default, the `Processing System (PS) AXI Master Ports` is enabled when you are adding `ZYNQ Processing System Core` to the design, but if it’s disabled, you can configure it by double-clicking the `ZYNQ Processing System Core` and under the `AXI Non-Secure Enablement` section in the `PS-PL Configuration`, enable a `General Purpose AXI Master Interface`.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/91db9570a2c6f66e5b13f714534b07b04eb42133/03-digital-sensor/resources/axi-master-config.png" width="60%" />
</p>

After enabling the `AXI Master port` the `ZYNQ Processing System` block diagram should look like the figure below.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/5ceb245d80d7923ccb2bec1f2a86b3dcb2e3e36b/02-axi-mmio/resources/zynq-axi-master.png" width="40%" />
</p>



### Adding AXI IIC Interface

In this section, you will add AXI IIC interface to the design. Follow the instruction below to add AXI IIC interface IP core your design:

1. Click `Add IP` button or use (Ctrl + I) keyboard shortcut and search the AXI IIC IP core.

2. Place `AXI IIC` IP core inside your design.

3. Configure IP settings by double-clicking the IP and change `IIC parameters` of the AXI IIC core.

4. In the IIC parameters, you need to change `SCL clock frequency` to match the SCL clock frequency of the sensor or IIC device. In this module, you will use MPU6050 sensor as IIC slave. So, set the SCL clock frequency to `400 KHz`. For other sensors, you can read the sensor datasheet to determine proper SCL clock frequency value.

5. Next step is to adjust the `address mode` and `SDA active state` configuration. For MPU6050 sensor, you need to set `address mode` to `7-bit` since MPU6050 address is 7-bit long and `active state of SDA` to `0`. These configurations depend on the sensor setting. So, make sure to check the sensor datasheet before changing the `AXI IIC IP configuration`.

   <p align="center">
       <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/91db9570a2c6f66e5b13f714534b07b04eb42133/03-digital-sensor/resources/axi-iic-ip.png" width="55%" />
   </p>

6. After that, you need to add IIC interface port in order to map the `AXI IIC` core output to the board pins. To add interface port, right click at the block diagram window and click `Create Interface Port` or use `Ctrl+L` keyboard shortcut. In the interface port window, set `interface name`, select `IIC interface`, and set the mode to `Master`. Finally, connect the `newly created interface port` with `IIC port`of AXI IIC IP core.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/91db9570a2c6f66e5b13f714534b07b04eb42133/03-digital-sensor/resources/axi-iic-port.png" width="30%" />
</p>



### Adding AXI Quad SPI Interface

After adding AXI IIC to your design, you also need to add an SPI interface in order to communicate with SPI-based sensor. In this case, you need to add `AXI Quad SPI` IP core. To add the IP core, you can just follow the steps when you add the `AXI IIC` IP core. For AXI Quad SPI core configurations, you just need to `disable STARTUP Primitive` option.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/91db9570a2c6f66e5b13f714534b07b04eb42133/03-digital-sensor/resources/axi-qspi.png" width="55%" />
</p>
After adding the core, you also need to add the interface port to map AXI Quad SPI core output to the board pins. To add SPI interface port, go to `board` section next to diagram window and find `SPI connector J6`, right click after selecting SPI connector J6, and choose `Auto Connect` option. This step allows Vivado to map existing IP core in the block diagram, in this case `AXI Quad SPI block` with available port in the PYNQ-Z1 board.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/91db9570a2c6f66e5b13f714534b07b04eb42133/03-digital-sensor/resources/axi-qspi-port.png" width="80%" />
</p>



### Synthesize and Port Mapping Process

After adding both `AXI IIC` IP core and `AXI Quad SPI` IP core, run design automation and validate the design. If there are no errors, then you can generate the block design wrapper and start `synthesizing` the design.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/91db9570a2c6f66e5b13f714534b07b04eb42133/03-digital-sensor/resources/final-bd.png" width="70%" />
</p>

Before running implementation and bitstream generation process, you need to change the `board pin mapping`, so that the AXI IIC IP core and AXI Quad SPI core inputs and outputs are mapped to correct pins. To change the pin mapping, click `open synthesized design` in the left menu and after synthesized design opens, click `window > I/O ports` option from toolbar.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/91db9570a2c6f66e5b13f714534b07b04eb42133/03-digital-sensor/resources/io-port-window.png" width="80%" />
</p>

In the I/O ports menu, you need to change board pin mapping as follows:

<div align="center">

| Port Name  | Board Pin Name | Package Pin Name |  I/O Std  |
| :--------: | :------------: | :--------------: | :-------: |
| IIC_scl_io |      SCL       |       P16        | LVCMOS33* |
| IIC_sda_io |      SDA       |       P15        | LVCMOS33* |
| SPI_io0_io |   spi_mosi_i   |       R17        | LVCMOS33* |
| SPI_io1_io |   spi_miso_i   |       P18        | LVCMOS33* |
| SPI_sck_io |   spi_sclk_i   |       N17        | LVCMOS33* |
| SPI_ss_io  |    spi_ss_i    |       T16        | LVCMOS33* |

</div>

After changing the pin mapping, save the constraint, resynthesize the design and start generating design bitstream.



### Run Design on PYNQ Board

After generating bitstream, you need to connect the sensor to PYNQ board before you can run and test the design. For this module, you will connect MPU6050 sensor to the board via IIC interface. Meanwhile, SPI interface is used to connect BME280 sensor with PYNQ board. If you connect those sensors directly without Arduino shield, you can follow the schematic below.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/91db9570a2c6f66e5b13f714534b07b04eb42133/03-digital-sensor/resources/sensor-no-shield.png" width="40%" />
</p>

Otherwise, just plug the Arduino shield with sensors to the PYNQ Arduino pin header.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/91db9570a2c6f66e5b13f714534b07b04eb42133/03-digital-sensor/resources/sensor-shield.png" width="40%" />
</p>

Once you connect the sensors, export the bitstream file and block diagram file and upload them to the PYNQ board, you need to create a new notebook and write Python code to control the behavior of your custom AXI memory-mapped interface. 

The first thing you need to do is to import the required `PYNQ library`, [pybme280](https://github.com/kaistseed/intro-to-xilinx-fpga/blob/b92d1f3470d12a6fab190918205a11a8bdf126c2/03-digital-sensor/pybme280.py) and [pympu6050](https://github.com/kaistseed/intro-to-xilinx-fpga/blob/b92d1f3470d12a6fab190918205a11a8bdf126c2/03-digital-sensor/pympu6050.py) library, and load the `overlay`. You can also check which IP core is connected to your system by using printing `ip_dict` variable from your overlay class. 

```python
# Import library
import cffi
import math
import time
import numpy as np
import datetime as dt
from pynq import Overlay
from pynq.lib.iic import AxiIIC

# Import library for MPU6050 and BME280 sensor
from pybme280 import *
from pympu6050 import *

# Import overlay
ol = Overlay("./multi_sensor_swapped.bit") # Filename might be different
# Print IP core list
print(ol.ip_dict)
```

When you check the IP core list by printing `ip_dict` variable, you will get a result similar to the result below.

```python
{'axi_iic_0': {'phys_addr': 1096810496, 'addr_range': 65536, 'type': 'xilinx.com:ip:axi_iic:2.0', 'state': None, 'interrupts': {}, 'gpio': {}, 'fullpath': 'axi_iic_0', 'mem_id': 'SEG_axi_iic_0_Reg', 'device': <pynq.pl_server.device.XlnkDevice object at 0xb02b0650>, 'driver': <class 'pynq.lib.iic.AxiIIC'>}, 'axi_quad_spi_0': {'phys_addr': 1105199104, 'addr_range': 65536, 'type': 'xilinx.com:ip:axi_quad_spi:3.2', 'state': None, 'interrupts': {}, 'gpio': {}, 'fullpath': 'axi_quad_spi_0', 'mem_id': 'SEG_axi_quad_spi_0_Reg', 'device': <pynq.pl_server.device.XlnkDevice object at 0xb02b0650>, 'driver': <class 'pynq.overlay.DefaultIP'>}}
```

Next step is to assign controller to each IP core by using the code below

```python
# Instantiate i2c controller
spi_control = ol.axi_quad_spi_0
i2c_control = ol.ip_dict['axi_iic_0']
```

After that, basically you can access both of the sensor using SPI and I2C protocol by writing command to the AXI quad SPI and AXI IIC IP core. For this module, you will be given libraries which contain function to write and read data to sensor using SPI and I2C protocol. So, you don’t need to write the function for SPI and I2C transactions.

To test the I2C protocol, first you want to check whether the MPU6050 can receive the data from PYNQ board by using code below. The code below initialize communication with MPU6050 sensor and set initial sensor parameter.

```python
# Declare AXI I2C Instance
AXII2C = AxiIIC(i2c_control)
MPUI2C = MPU6050(AXII2C, MPU6050_SCALE_2000DPS, MPU6050_RANGE_2G)
```

Then, you can do MPU6050 sensor calibration using the code below

```python
# Calibrate sensor
MPUI2C.calibrateGyro(100)

# Set threshold
MPUI2C.setThreshold(3)

# Check sensor settings
# Check sleep mode
print("Sleep mode: {}".format("Enabled" if (MPUI2C.getSleepMode()) else "Disabled"))

# Check clock source
clk_source = MPUI2C.getSensorClock()
if (clk_source == MPU6050_CLOCK_KEEP_RESET):
    print("Clock source: Reset mode")
elif (clk_source == MPU6050_CLOCK_EXTERNAL_19MHZ):
    print("Clock source: External 19.2 MHz clock")
elif (clk_source == MPU6050_CLOCK_EXTERNAL_32KHZ):
    print("Clock source: External 32.768 MHz clock")
elif (clk_source == MPU6050_CLOCK_PLL_XGYRO):
    print("Clock source: X-axis gyroscope reference")
elif (clk_source == MPU6050_CLOCK_PLL_YGYRO):
    print("Clock source: Y-axis gyroscope reference")
elif (clk_source == MPU6050_CLOCK_PLL_ZGYRO):
    print("Clock source: Z-axis gyroscope reference")
elif (clk_source == MPU6050_CLOCK_INTERNAL_8MHZ):
    print("Clock source: Internal 8 MHz oscillator")
else:
    print("Invalid clock source")
    
# Check gyroscope scale
gyro_scale = MPUI2C.getSensorScale()
if (gyro_scale == MPU6050_SCALE_250DPS):
    print("Gyroscope scale: 250 dps")
elif (gyro_scale == MPU6050_SCALE_500DPS):
    print("Gyroscope scale: 500 dps")
elif (gyro_scale == MPU6050_SCALE_1000DPS):
    print("Gyroscope scale: 1000 dps")
elif (gyro_scale == MPU6050_SCALE_2000DPS):
    print("Gyroscope scale: 2000 dps")
else:
    print("Invalid gyroscope scale setting")
    
# Check gyroscope offset
gyro_x_offset = MPUI2C.getGyroOffsetX()
gyro_y_offset = MPUI2C.getGyroOffsetY()
gyro_z_offset = MPUI2C.getGyroOffsetZ()
print("Gyroscope offset X: {} - Y: {} - Z: {}".format(gyro_x_offset, gyro_y_offset, gyro_z_offset))
```

After calibration, you can try to read some data from sensor. For example, you can read raw gyroscope data using code below

```python
while(1):
    # Get normalized gyroscope readings
    MPUI2C.getRawGyro()
    # Print result
    print("X-axis: {}, Y-axis: {}, Z-axis: {}".format(MPUI2C.raw_gyro["x_axis"], MPUI2C.raw_gyro["y_axis"], MPUI2C.raw_gyro["z_axis"]))
    # Delay
    time.sleep(0.25)
```

For the BME280 sensor with SPI interface, you can test the sensor using code below

```python
# Declare BME280 controller
BMESPI = BME280(spi_control, 0, 0)

# Check power mode
bme_mode = BMESPI.getSensorMode()
print("Sensor mode: {0:b}".format(bme_mode))

# Get sensor configuration
BMESPI.getSensorConfig()
# Print sensor configuration
print("Sensor Humidity Oversampling: {}".format(BMESPI.settings["humid_osr"]))
print("Sensor Pressure Oversampling: {}".format(BMESPI.settings["pres_osr"]))
print("Sensor Temperature Oversampling: {}".format(BMESPI.settings["temp_osr"]))
print("Sensor Filter Coefficient: {}".format(BMESPI.settings["filter_coef"]))
print("Sensor Standby Time: {}\n".format(BMESPI.settings["stby_time"]))

# Set sensor configuration
BMESPI.settings["pres_osr"] = BME280_OVERSAMPLING_1X
BMESPI.settings["temp_osr"] = BME280_OVERSAMPLING_16X
BMESPI.settings["humid_osr"] = BME280_OVERSAMPLING_2X
BMESPI.settings["filter_coef"] = BME280_FILTER_COEFF_16
BMESPI.settings["stby_time"] = BME280_STANDBY_TIME_62_5_MS

# Print sensor configuration
print("User Humidity Oversampling: {}".format(BMESPI.settings["humid_osr"]))
print("User Pressure Oversampling: {}".format(BMESPI.settings["pres_osr"]))
print("User Temperature Oversampling: {}".format(BMESPI.settings["temp_osr"]))
print("User Filter Coefficient: {}".format(BMESPI.settings["filter_coef"]))
print("User Standby Time: {}\n".format(BMESPI.settings["stby_time"]))

# Set sensor configuration settings selector
settings_sel = BME280_OSR_PRESS_SEL
settings_sel |= BME280_OSR_TEMP_SEL
settings_sel |= BME280_OSR_HUM_SEL
settings_sel |= BME280_STANDBY_SEL
settings_sel |= BME280_FILTER_SEL

# Write sensor configuration to slave device
BMESPI.setSensorConfig(settings_sel)
# Set sensor power mode
BMESPI.setSensorMode(BME280_NORMAL_MODE)

# Check power mode
bme_mode = BMESPI.getSensorMode()
print("Sensor mode: {0:b}".format(bme_mode))

# Get sensor configuration
BMESPI.getSensorConfig()
# Print sensor configuration
print("Final Humidity Oversampling: {}".format(BMESPI.settings["humid_osr"]))
print("Final Pressure Oversampling: {}".format(BMESPI.settings["pres_osr"]))
print("Final Temperature Oversampling: {}".format(BMESPI.settings["temp_osr"]))
print("Final Filter Coefficient: {}".format(BMESPI.settings["filter_coef"]))
print("Final Standby Time: {}\n".format(BMESPI.settings["stby_time"]))

# Get sensor calibration data
BMESPI.getCalibData()

# Get data from sensor
while(True):
    time.sleep(0.5)
    BMESPI.getSensorData(BME280_ALL)
    print("Temperature: {:.2f}°C - Pressure: {:.2f} Pa - Humidity: {:.2f}%\n".format(BMESPI.sensor_data["temperature"], BMESPI.sensor_data["pressure"], BMESPI.sensor_data["humidity"]))
```



## :question: [Practice] Postprocessing Sensor Data 

For practice, you can write a program to do following things:

- Read accelerometer data from MPU6050 sensor and plot the result.
- Get Pitch, Yaw, and Roll data from MPU6050 sensor and plot the result.
- Change BME280 sensor configuration such as oversampling ratio and compare the data with initial configuration. It is better if you can plot both data in one chart.

For plotting data, you can use any kind of libraries such as matplotlib or seaborn. You can also take a look at sensor datasheet `BME280`: **https://cdn.sparkfun.com/assets/e/7/3/b/1/BME280_Datasheet.pdf** and `MPU6050`: **https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf**. 

For other example program, you can find at this GitHub link `MPU6050`: **https://github.com/jarzebski/Arduino-MPU6050** and `BME280`: **https://github.com/adafruit/Adafruit_BME280_Library**. In the GitHub link, all of the example code and libraries are written in C. So, you need to write equivalent program in Python. But, you don’t need to write all of the function because you will be given a source code containing both MPU6050 and BME280 function written in Python language. 




## :book: References

- *PYNQ main website*, February 2021. Available: [**http://www.pynq.io/**](http://www.pynq.io/)
- *PYNQ-Z1 documentation*, February 2021. Available: [**https://pynq.readthedocs.io/en/v2.6.1/getting_started/pynq_z1_setup.html**](https://pynq.readthedocs.io/en/v2.6.1/getting_started/pynq_z1_setup.html) 
- *MPU6050 – Accelerometer and Gyroscope Module,* April 2021. Available:  [**https://components101.com/sensors/mpu6050-module**](https://components101.com/sensors/mpu6050-module)
- *Interface BME280 Sensor with Arduino,* April 2021. Available: [**https://lastminuteengineers.com/bme280-arduino-tutorial/**](https://lastminuteengineers.com/bme280-arduino-tutorial/)
- *Adafruit BME280 Library*, April 2021. Available: [**https://github.com/adafruit/Adafruit_BME280_Library**](https://github.com/adafruit/Adafruit_BME280_Library)
- *Arduino-MPU6050*, April 2021. Available: [**https://github.com/jarzebski/Arduino-MPU6050**](https://github.com/jarzebski/Arduino-MPU6050)
