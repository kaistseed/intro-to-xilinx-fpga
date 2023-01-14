# Analog Sensor (CO, NH<sub>3</sub> and NO<sub>2</sub> Sensor)
> <div align="justify"> This guide will help you to integrate analog sensor, specifically gas sensor (CO, NH<sub>3</sub> and NO<sub>2</sub>) with a PYNQ board. To be more specific, you will learn to design both hardware and software part that allows you to read data from analog sensor using AXI-stream protocol and integrate basic data filtering into data acquisition pipeline.</div>



## :bookmark_tabs: Table of Content

* [Context](#information_source-context)
* [Background](#mag-background)
* [AXI XADC Interface](#-axi-xadc-inteface)
* [Filtering Raw Sensor Data](#question-practice-filtering-raw-sensor-data)
* [References](#book-references)



## :information_source: Context

*Created by*: **Dalta Imam Maulana** </br>
*Document Version*: **January 14th, 2023**



## :mag: Background

### Analog to Digital Converter (ADC)

Analog to digital converter is a system that converts analog signals such as light captured by image sensor, or sound received by microphone into digital signal. In detail, an ADC converts continuous-time continuous-amplitude analog signal into discrete-time discrete-amplitude digital signal. ADC converts the signal by sampling the input signal at certain frequency and quantize the amplitude of input signal into several steps.

One of the performance parameters of the ADC is resolution. ADC resolution indicates the number of discrete steps or values the converter can convert the maximum allowable analog value to discrete value. In PYNQ board, there is a hard IP block that consists of dual 12-bit ADC with sampling rate up to 1 Mega sample per second (MSPS). It means that the PYNQ board can quantize the analog input into 4096 different amplitude level [1][2].

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/adc-conv-scheme.jpg" width="30%" />
</p>


### **MICS 6814**

MICS 6814 is an analog MEMS sensor that can detect the pollution from automobile exhaust or industrial pollution. This sensor can sense carbon monoxide (CO), ammonia (NH3), and nitrogen dioxide (NO2) gas [3].

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/mics-6814.jpg" width="35%" />
</p>



## <img style="vertical-align:middle" src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/bc75dd4823e71aa3921d17f8110f6a9771cd9d16/01-intro-to-vivado-and-pynq/resources/chip.png" width="32px" title=":chip:"/> AXI XADC Inteface

### Create New Vivado Project and System Block Diagram

To start this section, make a new Xilinx project for PYNQ Z1 board. Make sure to choose the correct board file during the project creation process. After that, create a new block diagram as in the previous project and also add a `ZYNQ Processing System`. Don't forget to run `Connection Automation` after adding `ZYNQ IP Core`.

In this section, you will create an interface between XADC IP core that receive analog data from external ports and ZYNQ processing system block. To connect both blocks, AXI Stream interface will be used as communication protocol and direct memory access (DMA) IP core will manage data transfer between both blocks.

In order to allow DMA IP core to handle the transaction between XADC IP core and ZYNQ processing system, you need to enable high performance AXI slave interface in the ZYNQ processing system. To do this, you can enable it by checking one of the `S AXI HP` interface under the `HP Slave AXI` Interface.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/axi-hp-slave-conf.jpg" width="65%" />
</p>

After enabling the `high performance AXI slave` interface, the `ZYNQ Processing System` block diagram should look like the figure below.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/axi-hp-slave.jpg" width="50%" />
</p>



### Adding XADC Wizard Block

In this section, you will add XADC wizard IP core to the design. Follow the instruction below to add XADC wizard IP core your design:

1. Click `Add IP` button or use (Ctrl + I) keyboard shortcut and search the `XADC Wizard` IP core.

2. Place `XADC Wizard` IP core inside your design.

3. Configure IP settings by double-clicking the IP and change the interface, sampling, and channel settings of the core.

4. In the basic setting section, you need to disable AXI-Lite interface and enable AXI-Stream interface, since you will connect this module to AXI DMA through AXI-Stream interface. In this section, you can also configure sampling rate of the block by changing `ADC Conversion Rate` parameter. By default, it is set to maximum value which is 1 Mega sample per second (MSPS). If you want, you can change the sampling rate to any number you want, but for this project, you can leave the conversion rate parameter at its default value.

   <p align="center">
       <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/xadc-conf.jpg" width="70%" />
   </p>

5. Next, in the `alarms` section, you need to disable all of the alarm signals since you’re not going to use it.

6. After that, you need to configure which XADC channel you’re going to use to sample the data. To configure the channel, go to `single channel` tab and change the channel to `VP VN` channel or `VAUX` channel. You can choose VP VN channel as input channel if you plan to connect analog input to VP and VN pin of PYNQ board. But, for this project, since the sensor is connected to A0 pin of the board, you need to select `VAUXP1 VAUXN1` channel.

7. After adding and configuring the XADC wizard block, you need to enable the `VAUXP1 VAUXN1` channel because by default those channels are disabled even though you’ve checked the enable channel setting when you configure XADC wizard block. To do this, you need to click the XADC wizard block you’ve added and under the `block properties` navigate to `properties` section and you need to change the value of `CHANNEL_ENABLE_VAUXP1_VAUXN1` to true. You can find the `CHANNEL_ENABLE_VAUXP1_VAUXN1` parameter under `config` option in the properties.

   <p align="center">
       <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/xadc-prop.jpg" width="75%" />
   </p>

8. After enabling the channel, you need to connect both `vauxp1` and `vauxn1` to port since you’re going to read external analog input with the XADC module. You can create external port by right click and choose `create port` menu. You can name your port anything you want but make sure to set the port as an input port. After adding the port, your diagram should look like similar to figure below.

   <p align="center">
       <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/xadc-port.jpg" width="50%" />
   </p>

9. In the XADC wizard configuration menu under basic section, you can see that by default the XADC module will run continuously (continuous mode), but if the XADC samples data and writes the data continuously to the memory through AXI DMA, it will be hard for you to check or interact with the data since the data keeps changing each time. So, instead you will control the operation of XADC module or control what data the DMA needs to store to memory via physical button.




### Adding Button, LED, and Debouncer

For this project, to control the sample data write process by AXI DMA, you will use physical button as an input device and LED for visual feedback.

1. In order to do that, first you need to enable the button and LED and add them into the design. You can add those buttons and LEDs just like what you did in the first project. For this case you only need to add one button and one LED (for visual feedback). So, you need to use slicer to slice the 4-bit buttons port to 1-bit port. But, before you connecting the output of the slicer with LED port and other block, you need to add `debouncer` module to remove unwanted signals when you press the button.
2. You can download the `debouncer` module from PYNQ GitHub repository (https://github.com/Xilinx/PYNQ) and add the custom IP core by clicking `settings` under project manager tab and in the settings menu, go to IP repository section and click `plus sign` to add the IP from PYNQ repository. When adding the repository, you can point to `<Your download directory>/PYNQ/boards/ip` folder, so that all of the IP inside the ip folder are automatically added to your project

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/ip-repo-add.jpg" width="100%" />
</p>



### **Adding XADC-DMA Flow Controller**

In this section, you will create a custom AXI Stream based module to control the data transfer between XADC – AXI DMA, and processing system. You can follow the steps below to create new custom AXI-Stream based module:

1. After adding button and LED, you need to create custom AXI stream module to control when DMA stores data from XADC to the memory. You can create custom AXI IP module by following the same steps as in the second project. But, for this project you need to create an AXI-stream based module with one AXIS slave port and one AXIS master port.

2. At the IP editor window, you need to edit top level module and you can also remove the master and slave template Verilog file under the top-level module. You can use the code below to replace top-level template code provided by Xilinx. The code below will receive input when button is pressed and the module will keep sending data from XADC to DMA as long as the data counter less than 1024. When the counter reach 1024, the module will stop sending data to DMA and will wait for another button input before start sending the data to DMA again.

3. When editing the code, don’t forget to change the module name to your IP core name and repackage the IP after finish editing the code.

   ```verilog
   module adc_chopper_v1_0 #
       (
           // Users to add parameters here
           // User parameters ends
           // Do not modify the parameters beyond this line
           // Parameters of Axi Slave Bus Interface S00_AXIS
           parameter integer C_S00_AXIS_TDATA_WIDTH    = 32,
           // Parameters of Axi Master Bus Interface M00_AXIS
           parameter integer C_M00_AXIS_TDATA_WIDTH    = 32,
           parameter integer C_M00_AXIS_START_COUNT    = 32
       )
       (
           // Users to add ports here
           input wire btn_input,
           // User ports ends
           // Do not modify the ports beyond this line
           
           // Ports of Axi Slave Bus Interface S00_AXIS
           input wire  s00_axis_aclk,
           input wire  s00_axis_aresetn,
           output wire  s00_axis_tready,
           input wire [C_S00_AXIS_TDATA_WIDTH-1 : 0] s00_axis_tdata,
           input wire [(C_S00_AXIS_TDATA_WIDTH/8)-1 : 0] s00_axis_tstrb,
           input wire  s00_axis_tlast,
           input wire  s00_axis_tvalid,
           // Ports of Axi Master Bus Interface M00_AXIS
           input wire  m00_axis_aclk,
           input wire  m00_axis_aresetn,
           output wire  m00_axis_tvalid,
           output wire [C_M00_AXIS_TDATA_WIDTH-1 : 0] m00_axis_tdata,
           output wire [(C_M00_AXIS_TDATA_WIDTH/8)-1 : 0] m00_axis_tstrb,
           output wire  m00_axis_tlast,
           input wire  m00_axis_tready
       );
       
       // Declare registers and wire
       reg start_sample;
       wire btn_pressed;
       reg prev_btn_input; 
       reg [9:0] data_counter;
       // AXI stream registers
       reg m00_axis_tlast_reg;
       reg s00_axis_tready_reg;
       reg m00_axis_tvalid_reg;
       reg [C_M00_AXIS_TDATA_WIDTH-1 : 0] m00_axis_tdata_reg;
   
       // AXIS control signal
       always @(posedge s00_axis_aclk)
       begin
           if (s00_axis_aresetn==0)
           begin
               s00_axis_tready_reg <= 0;
           end 
           else 
           begin
               s00_axis_tready_reg <= m00_axis_tready;
           end
       end
    
       // Data sampling logic
       always @(posedge m00_axis_aclk)
       begin
           // Sample button state
           prev_btn_input <= btn_input;
           // Set sampling status
           if (!start_sample && btn_pressed)
           begin
               start_sample <= 1;
           end 
           // AXIS control signal logic
           else if (start_sample)
           begin
               if (s00_axis_tvalid)
               begin
                   // Increment counter
                   data_counter <= data_counter +1;
                   if (data_counter == 'd1023)
                   begin
                       m00_axis_tlast_reg <= 1;
                       start_sample <= 0;
                   end 
                   else 
                   begin
                       m00_axis_tlast_reg <= 0;
                   end
               end
               m00_axis_tvalid_reg <= s00_axis_tvalid;
               m00_axis_tdata_reg <=s00_axis_tdata;
           end 
           else 
           begin
               m00_axis_tvalid_reg <= 0;
               m00_axis_tdata_reg <=s00_axis_tdata;
           end
       end
       // Assign value from AXIS registers to ports
       assign m00_axis_tvalid = m00_axis_tvalid_reg;
       assign m00_axis_tlast = m00_axis_tlast_reg;
       assign m00_axis_tdata = m00_axis_tdata_reg;
       assign s00_axis_tready = s00_axis_tready_reg;
       // Assign button state
       assign btn_pressed = btn_input && ~prev_btn_input;
   endmodule
   ```

4. Next add the newly created AXI stream module to block diagram and place it between XADC wizard and AXI DMA module. You need to connect the `M_AXIS` port of the XADC wizard to `S00_AXIS` port of the custom AXI stream module, `M00_AXIS` port to` AXI DMA S_AXIS_S2MM` port, and custom AXI stream `btn_input` port to one of the debouncer input. After connecting those modules, your diagram should look like the figure below.

   <p align="center">
       <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/unrouted-bd.jpg" width="80%" />
   </p>



### **Synthesize and Port Mapping Process**

After adding both `XADC wizard` IP core, `AXI DMA` IP core, and `your custom AXI-Stream` IP core, run design automation and validate the design. If there are warnings about debouncer reset port, you can connect the debouncer `reset_n` port to processor system reset module `peripheral_aresetn` port and the warning will be gone. You can ignore the warning about unmatched bit width between XADC wizard and custom AXI stream module. The final block diagram should look like the figure below. After that you can generate the block design wrapper and start `synthesizing` the design.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/routed-bd.jpg" width="100%" />
</p>

Before running implementation and bitstream generation process, you need to change the `board pin mapping`, so that the AXI IIC IP core and AXI Quad SPI core inputs and outputs are mapped to correct pins. To change the pin mapping, click `open synthesized design` in the left menu and after synthesized design opens, click `window > I/O ports` option from toolbar.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/io-window.jpg" width="80%" />
</p>

In the I/O ports menu, under the `Scalar ports`, you need to set `VN` pin ports to pin `D18` on the board and `VP` ports to pin `E17`. You also need to change the I/O std setting to `LVCMOS33`, since the maximum input voltage for the pin is 3.3 V. After changing the pin mapping, save the constraint and start generating design bitstream.



### Run Design on PYNQ Board

After generating bitstream, you need to connect the sensor to PYNQ board before you can run and test the design. For this module, you need to connect sensor shield to PYNQ Arduino pin header as you did in the previous project.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/sensor-board.jpg" width="40%" />
</p>
Once you connect the sensors, export the bitstream file and block diagram file and upload them to the PYNQ board, you need to create a new notebook and write Python code to control the behavior of XADC and DMA module. 

The first thing you need to do is to import the required `PYNQ library` and load the `overlay`. You can also check which IP core is connected to your system by using printing `ip_dict`variable from your overlay class. 

```python
import time
import numpy as np
import pynq.lib.dma
from pynq import Xlnk
from pynq import Overlay
import matplotlib.pyplot as plt

# Import overlay
ol = Overlay('./xadc_sensor.bit')
```

When you check the IP core list by printing `ip_dict` variable, you will get a result similar to the result below.

```python
{'axi_dma_0': {'phys_addr': 1077936128, 'addr_range': 65536, 'type': 'xilinx.com:ip:axi_dma:7.1', 'state': None, 'interrupts': {}, 'gpio': {}, 'fullpath': 'axi_dma_0', 'mem_id': 'SEG_axi_dma_0_Reg', 'device': <pynq.pl_server.device.XlnkDevice object at 0xaf7c5930>, 'driver': <class 'pynq.lib.dma.DMA'>}}
```

Next step is to assign controller to each IP core by using the code below

```python
# Print IP core list
print(ol.ip_dict)

# Instantiate DMA controller
dma_control = ol.axi_dma_0
```

After that, you need to create a function to plot the sampling result. In the code sample below, the sampled data is plotted using matplotlib library. If you want, you can also use another plotting library such as seaborn.

```python
# Declare plotting function
def plot_to_notebook(time_sec,in_signal,n_samples,):
    plt.figure()
    plt.subplot(1, 1, 1)
    plt.xlabel('Time in Microseconds')
    plt.grid()
    plt.plot(time_sec[:n_samples],in_signal[:n_samples],'y-',label='Signal')
    #plt.plot(time_sec[:n_samples]*1e6,in_signal[:n_samples],'y-',label='Signal')
    plt.legend()
def plot_time_series(time_sec,in_signal,n_samples,):
    plt.figure()
    plt.subplot(1, 1, 1)
    plt.xlabel('Samples')
    plt.grid()
    plt.plot(time_sec[:n_samples],in_signal[:n_samples],'y-',label='Signal')
    #plt.plot(time_sec[:n_samples]*1e6,in_signal[:n_samples],'y-',label='Signal')
    plt.legend()
```

After that, you can start sampling the sensor data by first starting DMA by using `dma_control.recvchannel.start()` command and after DMA runs, you need to create a buffer for storing sampled data from DMA. You can make the buffer by using `cma_array()` method on Xlnk() class. Finally, you need to pass the output buffer to dma_controller and wait for the sampled data result.

```python
# Start DMA
dma_control.recvchannel.start()
# Check DMA Styoatus
print("DMA running: ", dma_control.recvchannel.running)
print("DMA idle: ", dma_control.recvchannel.idle)

# Set parameter for plotting input signal
# Sampling frequency
fs = 100000000
# Number of samples
n = 1024#int(T * fs) 1024
#Total Time:
T = n*1.0/fs
# Time vector in seconds
ns = np.linspace(0,n,n,endpoint=False)

# Allocate buffers for the input and output signals
xlnk = Xlnk()
out_buffer = xlnk.cma_array(shape=(n,), dtype=np.int32)

# Start DMA transfer and wait for result
dma_control.recvchannel.transfer(out_buffer)
print("Please press the button to sample the data!")
start_time = time.time()
dma_control.recvchannel.wait()
stop_time = time.time()
hw_exec_time = stop_time-start_time
print("Total sampling time: " + str(hw_exec_time) + " seconds")
print("Sampled data mean: " + str(np.mean(out_buffer)))
# Plot to the notebook
plot_time_series(ns,out_buffer,20000)

# Free the buffers
out_buffer.close()
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

After reading the data from CO sensor, you will get the data similar to figure below

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/sensor-data.jpg" width="70%" />
</p>

From the figure above, you can see that the amplitude of both reading are different. Actually, it’s quite hard to test the sensor since you need to have pure CO gas to test the sensor functionality. For this project, if you don’t have access to such gas, you can just compare the sensor data with the XADC reading when the sensor is not connected to the board



## :question: [Practice] Filtering Raw Sensor Data 

For practice, you need to modify the block diagram to do following things:

- Add filter block to filter the raw ADC data.
- You can use `FIR Compiler` IP Core from Xilinx or you can create your own filter by modifying custom AXI stream IP core you’ve made earlier.

If you’re using `FIR compiler` IP core, you need to place the IP between your custom AXI-Stream module and AXI DMA. You can use the diagram below as a reference. 

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/fir-bd.jpg" width="100%" />
</p>

You also need to configure FIR compiler IP core as shown in the figure below

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/fir-coeff.jpg" width="70%" />
</p>

You can change the filter coefficient by replacing the value in the Coefficient Vector section. The filter coefficient can be obtained from [`online FIR filter design calculator`](http://t-filter.engineerjs.com/) by entering sampling frequency, passband frequency, and stopband frequency.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/fir-coeff-gen.jpg" width="80%" />
</p>

You also need to change input and output data width of the FIR compiler block to match with XADC output data width. Otherwise, an error message will appear when you validate the design.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/fir-coeff-type.jpg" width="70%" />
</p>

Finally, you need to configure the AXI interface setting of the FIR compiler as shown in the figure below.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/209dea91f96f43acbdc4e2250f3a2eeb88decdfb/04-analog-sensor/resources/fir-axi-conf.jpg" width="70%" />
</p>

If the tutorial for filtering is not clear enough, you can take a look at this [`FPGA tutorial website`](https://www.fpgadeveloper.com/2018/03/how-to-accelerate-a-python-function-with-pynq.html/). In that website, you’ll able to see a video about how to accelerate FIR filtering using FIR compiler IP block.



## :book: References

- *Analog-to-Digital Converter*, May 2021. Available: [**https://en.wikipedia.org/wiki/Analog-to-digital_converter**](https://en.wikipedia.org/wiki/Analog-to-digital_converter)
- *PYNQ-Z1 documentation*, May 2021. Available: [**https://pynq.readthedocs.io/en/v2.6.1/glossary.html**](https://pynq.readthedocs.io/en/v2.6.1/glossary.html) 
- *MICS 6814 – Datasheet*, May 2021. Available:  [**https://www.sgxsensortech.com/content/uploads/2015/02/1143_Datasheet-MiCS-6814-rev-8.pdf**](https://www.sgxsensortech.com/content/uploads/2015/02/1143_Datasheet-MiCS-6814-rev-8.pdf)
- *How to Accelerate Python Function with PYNQ,* May 2021. Available: [**https://www.fpgadeveloper.com/2018/03/how-to-accelerate-a-python-function-with-pynq.html/**](https://www.fpgadeveloper.com/2018/03/how-to-accelerate-a-python-function-with-pynq.html/)
