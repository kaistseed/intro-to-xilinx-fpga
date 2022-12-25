# Introduction to Vivado and PYNQ Framework
----------------------------------------------------------------------------------------------------------------------------------------
> <div align="justify"> This guide will help you to familiarize with Xilinx Vivado environment which is used to develop an FPGA-based project on Xilinx FPGA and System on Chip (SoC) boards. This tutorial also gives a basic introduction to the PYNQ framework which is an open-source project from Xilinx that helps the designers deploy their design easily by providing python libraries and environment to control the behavior of programmable logic (PL) and processing system (PS). </div>



## :bookmark_tabs: Table of Content

* [Context](#context)
* [Background](#background)
* [Programming an FPGA using Xilinx Vivado](#fpga-programming)
* [Creating a Python-based Software-Hardware Interface](#software-interface)
* [References](#references)



## :information_source: Context

*Created by*: **Dalta Imam Maulana**
*Document Version*: **December 23rd, 2022**



## :mag: Background

### Xilinx Vivado

<img src="C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\vivado-logo.jpg" alt="vivado-logo" style="zoom: 67%;" />



Vivado design suite is an integrated design environment (IDE) developed by Xilinx that provides a lot of features such as:

* Vivado high-level synthesis (HLS) compiler which transforms C, C++, and SystemC programs into RTL code.
* Vivado simulator that supports mixed-language simulation and verification.
* Vivado IP integrator that allows the designer to easily integrate and configure IP core either a pre-built library from Xilinx or custom-made IP cores.



### PYNQ Framework

<img src="C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\pynq-logo.png" style="zoom:33%;" />

PYNQ is an open-source framework from Xilinx that is designed for system designers, software developers, and hardware designers to easily use Xilinx platforms. With the support of Python language and libraries, designers can get the huge benefits of using programmable logic and microprocessors to build more interesting and powerful embedded systems. For now, the PYNQ framework can be used with Zynq, Zynq UltraScale+, Zynq RFSoC, and Alveo accelerator boards.



## Programming an FPGA using Xilinx Vivado

### Installing Vivado

To install Xilinx Vivado on your computer, first, you need to download the installer from the Xilinx website. You can download the software through this link: **https://www.xilinx.com/support/download.html** . On the download page, you can choose either the online installer or offline installer. If you choose an offline installer, then the downloaded software can be used in either Linux or Windows operating systems. 

![](C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\vivado-install.jpg)

During the installation process, you need to choose the `Vivado HL Webpack edition` since it doesn't require any license to use the software. If you are using an online installer, please make sure that you have around 40 GB of free space left on your computer since the installer will download a couple of files with a total size of around 35 GB.



### PYNQ Board Setup

In order to set up the PYNQ board, you need to prepare the following items:

* PYNQ Z1 board
* Computer with browser
* Ethernet cable
* Micro USB cable
* Micro SD with a minimum of 8 GB capacity

After preparing those items, the first thing to do is to download the correct PYNQ image file for the board from the following link                                                        **http://www.pynq.io/board.html**. For this tutorial, you will use the PYNQ Z1 board from Digilent. So, download the PYNQ image for the PYNQ Z1 board.

<img src="C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\pynq-download.jpg" style="zoom: 67%;" />

After downloading the PYNQ Image, flash the image into the SD card using an OS flasher tool such as `Balena Etcher`. You can download Balena Etcher software from **https://www.balena.io/etcher/**. After flashing the PYNQ image to an SD card, now you can try to connect the board to your computer by following the steps below:

<img src="C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\pynq-setup.jpg" style="zoom:80%;" />

1.	Set the JP4 jumper to SD position by placing the jumper over the top two pins as in the figure above.
2.	If you use a micro USB cable to supply power to the board, place the JP5 jumper in a USB position. You can also power the board with a 12 V external power supply by configuring the JP5 jumper to REG position.
3.	Insert microSD card with PYNQ image to the micro SD card slot in the bottom of the board.
4.	Connect the micro USB cable to the board and computer.
5.	Connect the board to the network by using an ethernet cable. The connection can be done directly to the computer or via a network router.
6.	Turn on the board and check whether the board is operating correctly by looking at the LED indicator in the board. After turning on the board, RED LD13 LED will turn on immediately indicating that the board has power. Shortly after that, Yellow LD12 LED will also turn on to show up that the board is working correctly. After a minute, two BLUE LD4 & LD5 LED will start flashing to indicate that the system is now booted and ready to use.
7.	To access the PYNQ board via a direct connection, you must set the IP address of your computer to a static IP address in the range of 192.168.2.00 to 192.168.2.255 (except for 192.168.2.99 since it is used by the board).
8.	After setting the IP address, open the browser and enter `192.168.2.99` in the address bar.
9.	If the board is configured correctly, you will see a login screen with a password field in it. The username for the board is `xilinx` and the password is also `xilinx`.

For more detailed information about how the board and how to set up it, you can access the documentation at this link:                                                                 **https://pynq.readthedocs.io/en/latest/getting_started/pynq_z1_setup.html**.



### Implementing and Synthesizing a Design using Vivado

This guide will teach you how to build a basic Zynq system containing processing systems (PS) and programmable logic (PL). You will also learn how to make a simple memory-mapped interface that controls the programmable logic (PL) part connected to the onboard LED via Python program in the processing system (PS).

#### Create New Vivado Project 
First, open up Vivado application and create a new project.
1.	Click next on Create a New Project.
2.	Enter the name of your project, for example, led_chaser.
3.	Select RTL project and click next.
4.	If you already have Verilog source, you can add it in the add source window. Otherwise, just skip the process and click next.
5.	Add board constraint file by choosing pynq_z1.xdc file and make sure to check copy constrains files into project option.
6.	In the board selection section, choose PYNQ-Z1 board if it is available. Otherwise, you should download the PYNQ-Z1 board file and copy the board files folder to `<Xilinx installation directory>\Vivado\<version>\data\xhub\boards\XilinxBoardStore\boards\Xilinx\`                                         (**Note:** for older Vivado version, you can copy the board files to `<Xilinx installation directory>\Vivado\<version>\data\boards`).                                                                     You can find PYNQ-Z1 board files on **https://pynq.readthedocs.io/en/latest/overlay_design_methodology/board_settings.html**. You need to restart Vivado after copying the board file.

<img src="C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\pynq-board.png" style="zoom:80%;" />



#### Create System Block Diagram
In this tutorial, you will create the system block diagram which control the onboard LED operation via pushbuttons as follows.

<img src="C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\led-chaser-bd.png" style="zoom: 60%;" />

In order to recreate the block diagram above in your Vivado project, you can follow the steps below:

1. Under the IP Integrator section on Flow Navigator, click on `Create Block Diagram`. You can change the name of the block diagram, but make sure to keep the directory location to `local to the project`.

2. A blank diagram window will appear on the right pane. In this blank diagram pane, you can add any kind of IP core provided by Xilinx or add your custom IP core.

3. To add IP core into the design, you can click `Add IP` button or by using (Ctrl + I) keyboard shortcut.

4. Add `ZYNQ Processing System IP` by entering zynq keyword on the search bar. 

5. After you add the ZYNQ IP core, you will see a green option window with `Run Block Automation` text in it. This block automation option will help you to connect the IP core in the design. But sometimes, the connection created by this automation process is not correct. So, make sure to recheck the connection after performing a block automation operation.

![](C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\block-automation.png)

6. After running block automation, some new wires and `external interfaces` such as `DDR` and `FIXED_IO` will appear in the design which corresponds to the board output pins.

7. The next step is to customize the `ZYNQ Processing System` core to meet the design requirement. For this project, you need to disable AXI ports that connect the processing system (PS) and programmable logic (PL) directly. You can disable those ports by double-clicking the ZYNQ IP core and click `PS-PL Configuration` section. In the PS-PL configuration, make sure to uncheck all of the available options.

![](C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\ps-pl-config.png)

8. After that, you need to enable some GPIO on the processing system (PS). To enable the GPIO, click on the `Peripheral I/O Pins` tab and check the `GPIO MIO` and `GPIO EMIO` option. You can also disable several unused ports such as flash and SPI ports.

<img src="C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\io-config.png" style="zoom:60%;" />

9. The last configuration you need to take care of is the clock configuration. To configure the clock signal of the system, select the `Clock Configuration` option on the page navigator, and under `PL Fabric Clocks`, set `FCLK_CLK0` to 50 MHz frequency as shown in the figure below.

<img src="C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\clock-config.png" style="zoom:60%;" />

10. After finish configuring the ZYNQ IP core parameter, click `OK` and Vivado will update the ZYNQ IP core block diagram and the ZYNQ block should look like the figure below.

<img src="C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\zynq-ip.png" style="zoom:80%;" />



#### Create LED Controller using Verilog

In this project, you need to create two modules using Verilog which are clock divider module and LED controller module. To create a new module, go to `PROJECT MANAGER`, select `Add Sources`, click `Add or Create Design Sources`, and then select `Create File`option. After naming the file, click `Finish`button, and then `Define Module`window will show up. Just skip this part by clicking `OK`button, since it's faster to type the Verilog code by yourself.

##### Clock Divider Module

For clock divider module, you will be given a sample Verilog code as below:

```verilog
module clock_div
    // Declare module ports
    (
        // Input ports
        input wire I_CLK, I_RSTN,
        // Output port
        output wire O_CLK
    );

    // Declare register
    reg [31:0] r_counter;

    // Logic for performing 1 to 1 million clock divider
    always @(posedge I_CLK) 
    begin
        if (!I_RSTN)
        begin
            r_counter <= 32'd0;
        end
        else
        begin
            if (r_counter == 32'd1000000)
            begin
                r_counter <= 32'd0;
            end
            else
            begin
                r_counter <= r_counter + 1;
            end
        end
    end

    // Assign value to output port
    assign O_CLK = (r_counter == 32'd1000000);
    
endmodule
```

Add the code into your Verilog file and save it. You can simulate the clock divider module if you want using any kind of RTL simulators such as `ModelSim` or `IVerilog`. After checking the functionality of the module, you can integrate the module into the existing block diagram by following the steps below:

1. Right-click on the block diagram editor window and click `Add Module`option. After that, select your clock divider module and your clock divider block will appear in the block diagram editor.

2. After placing clock divider block, you can use the `Block Design Automation`option to automate the connection creation process between ZYNQ Processing System and clock divider module.




##### LED Controller Module

To control LED behavior, you need to make another module that will control the LED movement by using clock divider output and it can go either in the left direction, the right direction, or stop depend on control signals:

- `Stop signal` will come from ZYNQ Processing System (PS). This signal is controlled through Python.

- `Left signal` will come from the button connected to the programmable logic (PL).

- `Right signal` will come from another button connected to the programmable logic (PL).

To create the module, you can follow the same steps when you are making the clock divider module. For this module, you will be given a skeleton code for the module and **you need to write the main logic for controlling the LED behavior**. You can use the skeleton code below:

```verilog
`timescale 1ns / 1ps
module led_control
    // Declare module ports
    (
        // Input ports
        input wire I_CLK, I_RSTN,
        input wire I_STOP,
        input wire I_GO_LEFT,
        input wire I_GO_RIGHT,

        // Output port
        output wire [3:0] O_LED_CTRL
    );

    // Write the LED control logic here

endmodule
```

After making sure that the module operates correctly, add the LED controller module to the block diagram by doing the same steps as you did when you added clock divider module to the block diagram. You can check the video to see how the led controller works.

When you are creating the connection to this module, you will encounter a problem since the input pin on the LED controller module is 1-bit wide whereas the buttons signal is a 4-bit wide vector, and the GPIO out from the ZYNQ Processing System (PS) is a 64-bit wide vector. To solve this problem, Xilinx provides `Slice` IP core to slice/demultiplexing input signals. To add `Slice` IP core, go to `Add IP` window and search for `Slice`.  You need three Slice IP core with a different configuration. 

The configuration of each Slice IP core can be seen below:

- For ZYNQ Processing System (PS) GPIO slicer, set slicer input width `Din Width` to 64 bits, `Din From` and `Din Down To` value to 2. This configuration makes the slicer take 64-bit input data and only put the third-bit value to the output port.

- For the first button slicer, add another Slice IP and configure it to receive 4 bits of data and slice the input data from 0 down to 0.

- For the second button slicer, add another Slice IP and configure it to also receive 4 bits of data and slice the input data from 1 down to 1.

Before connecting the slicer module with another module, you need to enable the interface to board peripheral such as buttons and LEDs, so that programmable logic (PL) can receive and send data to those peripheral. To enable the interface, you can follow the steps below:

1. Open the pynq_z1.xdc file (you can find it under `Sources` -> `Constraints`)

2. Uncomment the set of lines related to the LEDs and buttons. After configuring the constraint file, your XDC file should look like the figure below.

<img src="C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\pynq-constraint.png" style="zoom:70%;" />

3. After that, go back to the block diagram window and do `Right Click`and select `Create Port` option. Selecting `Create Port` option will bring up new windows to create input and output ports to programmable logic (PL). For this project, create an input port for the buttons and output ports for the LEDs. The configuration of each port can be seen below:
   - Create output port with Port name set to `led`, Direction set to `Output`, and check `Create vector` option with the value from 3 to 0.
   - Create input port with Port name set to `btn`, Direction set to `Input`, and check `Create vector` option with the value from 3 to 0.

<img src="C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\create-port.png" style="zoom:50%;" />

4. The last step is to create connections between each module and external port interfaces. When completed, your block diagram should look similar to the block diagram in the figure below.

<img src="C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\final-bd.png" style="zoom:40%;" />



#### Generate Output Bitstream

After creating the block diagram, you need to generate an output bitstream file to run the design on the PYNQ board. To generate an output bitstream file, you can follow the steps below:

1. Click on the `Optimize Routing` button at the top of the diagram window (right angle wire with reload symbol). This process will clean up your block diagram layout.

2. Click on the `Validate Design` button at the top of the diagram window (a square with a checkmark symbol). This process will perform a sanity check of your system and flag any potential problems in the design such as unconnected wires, incompatible pins, etc. For this specific project, if you get a warning related to the reset signal, you can ignore it. But, if there are any other warnings after design validation, you need to fix the problem in the design.

3. After validating the design, under the `Sources` menu, right-click on the block diagram file (file with .bd extension), and click on `Create HDL Wrapper option`. For the sake of simplicity, let Vivado manage and automatically update the design. The `Create HDL Wrapper` process will create a high-level Verilog file that represents your block diagram.

4. If there are no errors, you can proceed to generate bitstream process by clicking `Generate Bitstream` option under Program and Debug menu in Flow navigator. Choosing `Generate Bitstream` option will start the whole build process from module synthesizing process up to generating output bitstream product. This process may take a couple of minutes depending on your computer and design complexity. Errors may appear during this process. So, pay attention to it and try to fix the error if there is an error in your design.

5. When the build is complete, you need to export the bitstream file by choosing `Export Bitstream File` option under the `Export` option under `File` menu. Make sure that your block diagram window is open before exporting the block diagram. Otherwise, the `Export Bitstream File` option will not show up. Make sure to name the `bitstream file (file with .bit extension)` with the block design name (by default it is design_1). Otherwise, an error message will appear when you are trying to load the design into PYNQ board.

<img src="C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\bd-name.png" style="zoom:80%;" />

6. If you encounter any error during exporting process such as `Too many positional options when parsing` (**you can look for the error message in tcl console**), copy the `write_bd_tcl` line in tcl console, add double quotes (") symbol before and after your folder path, and run the command again using tcl console.



## Creating a Python-based Software-Hardware Interface
### Uploading Design from PC to PYNQ Board

To run the design on the PYNQ board, first, you need to upload the bitstream and tcl file into the PYNQ board. You can upload the files to the board by following the steps below:

1. Open PYNQ board Jupyter Notebook by entering 192.168.2.99 in the host computer browser address bar. If you can’t access PYNQ board Jupyter Notebook, please refer to `PYNQ Board Setup`section.

2. Create a new folder called `project` by clicking `New` button in the Jupyter Notebook interface.

3. If you want, you can create another folder inside project folder which is designated for each project you create. In this case `led_chaser` folder.

4. Upload project bitstream into `led_chaser` folder by clicking `Upload` button beside New button in Jupyter Notebook. 

5. Upload `.hwh` file and `.tcl` file into `led_chaser` folder. You can find those files in `<project_name>\<project_name>.srcs\sources_1\bd\<block_design_name>\hw_handoff`

<img src="C:\Users\dalta\OneDrive - kaist.ac.kr\KAIST\Research\Projects\Digital System Guide\resources\upload-files.png" style="zoom:67%;" />



### Creating Python Interface

To control the programmable logic (PL) operation, you need to create a software-hardware interface based on Python. You can do this by creating a `python3 notebook` inside the `led_chaser` folder, put the following code into the notebook and run them in sequence.

The first code chunks you need to run are written below. This code imports libraries such as Overlay, GPIO, and Clocks library which are provided by the PYNQ framework. `Overlay` library is used to load the bitstream file that is generated by the Vivado application. `GPIO`library can be used to write or read the value from GPIO ports, and you can use `Clocks` library to change or modify clock frequency of the programmable logic (PL).

```python
# Import library
from pynq import Overlay
from pynq import GPIO
from pynq import Clocks

# Import overlay
ol = Overlay("./design_1.bit")
```

Next, you need to establish an interface between the Python program and GPIO pins by using the `GPIO` library. In the code below, GPIO pin 2 is set as an 'out' pin since GPIO pin 2 is used to send a stop signal to the LED controller module. You can write a value to the GPIO pin by using the write method. In this code, the stop signal is set to 0. `If you want to send a stop signal, call the write method and write "1" to the stop pin`.

```python
# Set stop GPIO
stop = GPIO(GPIO.get_gpio_pin(2),'out')

# Set stop value
stop.write(0)
```

Finally, you can change the frequency of programmable logic (PL) clocks from Python by using `Clocks` library. This library gives you the capability to perform debugging at some level without having to rebuild the bitstream.  

```python
# Change clock frequency
Clocks.fclk0_mhz = 10
print(f"FCLK0: {Clocks.fclk0_mhz:.6f} MHZ")
```



## :book: References

- *PYNQ main website*, February 2021. Available: [**http://www.pynq.io/**](http://www.pynq.io/)

- *PYNQ-Z1 documentation*, February 2021. Available: [**https://pynq.readthedocs.io/en/v2.6.1/getting_started/pynq_z1_setup.html**](https://pynq.readthedocs.io/en/v2.6.1/getting_started/pynq_z1_setup.html) -
- *PYNQ example of controlling IP via GPIO*, February 2021. Available: [h**ttps://www.youtube.com/watch?v=UBsCNPWudww&ab_channel=MohammadS.Sadri**](https://www.youtube.com/watch?v=UBsCNPWudww&ab_channel=MohammadS.Sadri)
