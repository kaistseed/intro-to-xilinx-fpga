# AXI Memory Mapped Interface
> <div align="justify"> This guide will help you to design your AXI memory-mapped-based IP core. The AXI memory-mapped IP core is essential in the accelerator and embedded system design since it can be easily controlled by the processing system (PS) through Python code. In addition, you can easily integrate the AXI memory-mapped IP core with other IP core which uses the AXI protocol. </div>



## :bookmark_tabs: Table of Content

* [Context](#information_source-context)
* [Background](#mag-background)
* [Programming an FPGA using Xilinx Vivado](#-programming-an-fpga-using-xilinx-vivado)
* [Creating a Python-based Software-Hardware Interface](#-creating-a-python-based-software-hardware-interface)
* [References](#book-references)



## :information_source: Context

*Created by*: **Dalta Imam Maulana** </br>
*Document Version*: **December 27th, 2022**



## :mag: Background

### Memory Mapped I/O

In the modern system, processing system communicate with another peripheral through bus. There are different kind of scheme that can be used to control I/O ports via bus. One of the schemes is called memory mapped I/O scheme. In the memory mapped I/O scheme, I/O devices are mapped into the system memory space along with memory blocks (RAM and ROM). To access those, I/O devices, one can simply read and write to dedicated memory addresses using normal memory address command or instruction.


### AXI4 Interface

AXI is part of ARM AMBA, a family of microcontroller buses first introduced in 1996. AMBA 4.0 is released in 2010 which includes AXI4 interface. There are three types of AXI4 Interface namely:
- AXI4 for high performance memory-mapped requirements.
- AXI4 Lite for simple, low throughput memory-mapped operation.
- AXI4 Stream for high speed streaming data.
AXI4-Lite interface consists of five channels: `Read Address`, `Read Data`, `Write Address`, `Write Data`, and `Write Response`. In `read transaction`, AXI4-Lite uses `Read Address `and `Read Data` channels. Meanwhile, in `write transaction`, AXI4-Lite uses `Write Address`, `Write Data`, and `Write Response` channels.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/ba2040c2c0f33598618073df356e9ae9206edcfd/01-intro-to-vivado-and-pynq/resources/pynq-logo.png" width="40%" />
</p>

All of the five channels use VALID-READY handshake process to transfer data, address, and control information. The source block generates VALID signal whenever address, data, or control information are available. Whereas sink block generates READY signal whenever the block can receive data from source. Data transfer process is happened when both VALID and READY signal are asserted.



### AXI4-Lite Read Operation

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/ba2040c2c0f33598618073df356e9ae9206edcfd/01-intro-to-vivado-and-pynq/resources/pynq-logo.png" width="40%" />
</p>

The operation sequence of AXI4-Lite read operation is described below:
1. `Master` set the address on the `Read Address` channel, asserting `ARVALID` to indicate read address is valid, and also asserts `RREADY` which indicates that master is ready to receive data from `slave`.
2.	`Slave` assert `ARREADY` to indicate that slave is ready to receive address from master.
3.	On the next rising edge clock, handshake process happens since both `ARREADY` and `ARVALID` are asserted. After this process, both `ARVALID` and `ARREADY` are de-asserted by `master` and `slave` respectively (by this time, `slave` has received the request address).
4.	`Slave` puts requested data on the `Read Data` channel and asserts `RVALID` signal to indicate that the data on the `Read Data` channel is valid.
5.	Since both `RVALID` and `RREADY` signals are asserted, in the next clock cycle, data transaction happens and after that both `RVALID` and `RREADY` can be deasserted.




### AXI4-Lite Write Operation

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/ba2040c2c0f33598618073df356e9ae9206edcfd/01-intro-to-vivado-and-pynq/resources/pynq-logo.png" width="40%" />
</p>

The operation sequence of AXI4-Lite write operation is described below:
1.	`Master` puts data on the `Write Data` channel and address on the `Write Address` channel. Master also asserts `WVALID` and `AWVALID` signals to indicate that the data and address are valid. `BREADY` signal is also asserted to indicates that master ready to receive response from slave.
2.	`Slave` asserts `WREADY` and `AWREADY` signals to indicate that the slave ready to receive data from master.
3.	On the next rising edge clock, handshake process happens since both `AWVALID` - `AWREADY` and `WVALID` - `WREADY` are asserted. After this process, both `AWVALID` - `AWREADY` and `WVALID` - `WREADY` are de-asserted by `master` and `slave` (by this time, slave has received the data from master).
4.	`Slave` asserts `BVALID` signal indicating there is a valid response on the write response channel.
5.	In the next clock cycle, the transaction is completed and another operation can take place between master and slave.



## <img style="vertical-align:middle" src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/bc75dd4823e71aa3921d17f8110f6a9771cd9d16/01-intro-to-vivado-and-pynq/resources/chip.png" width="32px" title=":chip:"/> Simple Memory-Mapped Interface

### Create New Vivado Project and Configure ZYNQ IP Core

To start this section, make a new Xilinx project for PYNQ Z1 board. Make sure to choose the correct board file during the project creation process. After that, create a new block diagram as in the previous project and also add a `ZYNQ Processing System`. Don't forget to run `Connection Automation` after adding `ZYNQ IP Core`.

In this section, you will create a memory-mapped interface that can be accessed from the Python environment. There are many ways to create a memory-mapped interface. But, for this section, you will use one of the General Purpose AXI Interfaces, specifically `Processing System (PS) AXI Master Ports`.

By default, the `Processing System (PS) AXI Master Ports` is enabled when you are adding `ZYNQ Processing System Core` to the design, but if it’s disabled, you can configure it by double-clicking the `ZYNQ Processing System Core` and under the `AXI Non-Secure Enablement` section in the `PS-PL Configuration`, enable a `General Purpose AXI Master Interface`.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/ba2040c2c0f33598618073df356e9ae9206edcfd/01-intro-to-vivado-and-pynq/resources/vivado-install.jpg" width="70%" />
</p>

After enabling the `AXI Master port` the `ZYNQ Processing System` block diagram should look like the figure below.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/ba2040c2c0f33598618073df356e9ae9206edcfd/01-intro-to-vivado-and-pynq/resources/vivado-install.jpg" width="70%" />
</p>



### Create Custom AXI Memory Mapped IP Core

In this section, you will make a custom IP core with AXI interface in it. Follow the instruction below to start creating the custom IP core:

1. Go to `Tools` menu and click `Create and Package New IP`.

2. Select `Create AXI4 Peripheral`.

3. Give a name to the IP core and set the directory for storing the IP core-related files.

4. In the next window, it will show a default module that has a single AXI4-LITE Slave Interface. You can add another AXI interface to the IP core. But, for this specific project, a single AXI4-LITE Slave Interface with a data width of 32 bits and 4 registers is enough.

5. At the next window, you are going to edit the IP core immediately. So, select `Edit IP` option and it will take you to IP editor window.

6. At the editor window, navigate to the source menu and double-click on the inner file (the one with `S00_AXI_inst`). This Verilog file contains all of the AXI-LITE timing and state machine template. So, you only need to add your logic to interact with this AXI interface.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/ba2040c2c0f33598618073df356e9ae9206edcfd/01-intro-to-vivado-and-pynq/resources/pynq-download.jpg" width="70%" />
</p>

7. For this tutorial, you will make an IP block that takes a set of three numbers: `a`, `b`, and `c`. Those values are used to compute `d` given by the equation below. 
   $$
   d = 3 + (a + b) c^2
   $$
   During AXI IP core creation process, you set the register depth of the module to 4. So, you can think the module as an AXI module with four read/write accessible memory locations as shown in the figure below.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/ba2040c2c0f33598618073df356e9ae9206edcfd/01-intro-to-vivado-and-pynq/resources/pynq-setup.jpg" width="50%" />
</p>

​	   You will store the `a`, `b` and `c` values in the address `0x00`, `0x04`, `0x08` respectively. While the computation result `d` will be stored at address `0x0C`.

8. To perform the calculation, you will be provided a Verilog module that performs the arithmetic operation in a pipelined fashion. It means that the value of c<sup>2</sup> is calculated in one clock cycle and the rest of the computation will be computed on the next clock cycle. 

   ```verilog
   `timescale 1ns / 1ps
   module math_op
       // Declare ports
       (
           // Input ports
           input wire I_CLK, I_RSTN,
           input wire signed  [31:0] IN_A,
           input wire signed  [31:0] IN_B,
           input wire signed  [31:0] IN_C,
   
           // Output ports
           output wire signed  [31:0] OUT_D
       );
   
       // Declare registers
       reg [31:0] r_c_square;
       reg [31:0] r_out;
   
       // Main logic
       always @(posedge I_CLK) 
       begin
           if (!I_RSTN)
           begin
               r_c_square <= 32'd0;
               r_out <= 32'd0;
           end
           else
           begin
               r_c_square <= IN_C * IN_C;
               r_out <= 3 + r_c_square * (IN_A + IN_B);
           end
       end
   
       // Assign value to ports
       assign OUT_D = r_out;
       
   endmodule
   ```

   9. In order to integrate the `math_op` module into AXI IP core, while in the IP editor, create a new source by using `Add Sources` button and create a new Verilog file that contains `math_op` Verilog code above.

   10. After that, call the `math_op` instance inside the AXI template Verilog file (the one with `S00_AXI_inst`). You can call the `math_op` instance by copying the code below on the area below the `Add user logic here`. Things to note that in the module instantiation, the input of the `math_op` module is connected to the AXI registers namely `slv_reg0`, `slv_reg1`, `slv_reg2`. Those registers correspond to the first, second, and third memory location in the AXI module, and those values are always filled with the most recent values written to them.

       ```verilog
       // Add user logic here
       // Declare wire
       wire [31:0] w_math_op_out;
       
       // Call math_op module
       math_op math_op_module (
       // Input ports
           .I_CLK(S_AXI_ACLK), 
           .I_RSTN(S_AXI_ARESETN),
           .IN_A(slv_reg0),
           .IN_B(slv_reg1),
           .IN_C(slv_reg2),
       
           // Output ports
           .OUT_D(w_math_op_out)
       );
       // User logic ends
       ```

   11. In the code above, you can also see that the output value is connected to `w_math_op_out wire`. This wire is used to link the `math_op` output value `d` to an output register that will be placed into a memory-mapped location. To link the output, you need to connect the other end of `w_math_op_out` wire into the appropriate register location. In this case, you need to connect the wire to `slv_reg3`, and this connection can be done by replacing the line in the AXI template file as you can see in the code below.

       ```verilog
       	// Implement memory mapped register select and read logic generation
           // Slave register read enable is asserted when valid address is available
           // and the slave is ready to accept the read address.
           assign slv_reg_rden = axi_arready & S_AXI_ARVALID & ~axi_rvalid;
           always @(*)
           begin
                 // Address decoding for reading registers
                 case ( axi_araddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] )
                   2'h0   : reg_data_out <= slv_reg0;
                   2'h1   : reg_data_out <= slv_reg1;
                   2'h2   : reg_data_out <= slv_reg2;
                   2'h3   : reg_data_out <= w_math_op_out;
                   default : reg_data_out <= 0;
                 endcase
           end
       ```

   12. The next step is to package the newly created custom AXI IP core that you have made. This can be done by first looking at the `Packaging Steps` tab in IP Editor window. In the `Packaging Steps` you need to make sure that all of the tabs have green checkmarks in it. Otherwise, you need to resolve those issues by clicking on the unchecked tab and click on the text with blue color and yellow background. For example, in `File Groups` tab, you need to click `Merge Changes from File Groups Wizard` text to resolve the issue and after that you can repackage the IP by clicking on `Review and Package` tab and click the `Re-Package IP` button.

   13. If there are no errors in the design, you will be asked if you want to return to your main project. You just need to click `OK` to exit IP editor. Upon exit, a pop-up window about `Generating Output Products` may appear. If it’s showing, then you need to click `Global` and also click `Generate`.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/ba2040c2c0f33598618073df356e9ae9206edcfd/01-intro-to-vivado-and-pynq/resources/pynq-download.jpg" width="70%" />
</p>


### Add AXI IP Core to System Block Diagram

After creating a custom AXI IP core, you need to add and integrate the newly created module into the block diagram. You can add it by clicking `Add IP` button or by using (Ctrl + I) keyboard shortcut and search the IP by name, in the example below, the IP core can be added by entering `memory_map_ip` keyword on the search bar. After that, you can let Vivado do automate wiring operation and the overall diagram of the system should look like the figure below.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/ba2040c2c0f33598618073df356e9ae9206edcfd/01-intro-to-vivado-and-pynq/resources/pynq-download.jpg" width="70%" />
</p>

If there are no errors, you can do a sanity check of your system by clicking on a button with a check-mark as you did in the previous project. After that, right-click on the block diagram file under the Sources tab and click Create HDL Wrapper. The last thing you need to do in Vivado is to Generate Bitstream and export both of Bitstream File, Block Design, and Hardware File as in the previous project.



### Run Design on PYNQ Board

Once you export the bitstream file and block diagram file and upload them to the PYNQ board, you need to create a new notebook and write Python code to control the behavior of your custom AXI memory-mapped interface. The first thing you need to do is to import the required `PYNQ library` and load the `overlay`. You can also check which IP core is connected to your system by using printing `ip_dict` variable from your overlay class. 

```python
# Import library
from pynq import Overlay
# Import overlay
ol = Overlay("./memory_mapped.bit")
# Check IP List
print(ol.ip_dict)
```

When you check the IP core list by printing **ip_dict** variable, you will get a result similar to the result below.

```python
{'memory_map_ip_0': {'phys_addr': 1136656384, 'addr_range': 65536, 'type': 'xilinx.com:user:memory_map_ip:1.0', 'state': None, 'interrupts': {}, 'gpio': {}, 'fullpath': 'memory_map_ip_0', 'mem_id': 'SEG_memory_map_ip_0_S00_AXI_reg', 'device': <pynq.pl_server.device.XlnkDevice object at 0xb02ae410>, 'driver': <class 'pynq.overlay.DefaultIP'>}}
```

From the result above, you can see that for this system, there is only one custom IP core connected to the system which is `memory_map_ip_0`. You can also see the properties of the IP core such as physical address and address range of the core. For this project module, you won’t need that information, but that information sometimes can be useful especially in a complex system with multiple custom IP core and complex memory accessing scheme.

Next step is to test the functionality of your custom memory-mapped IP core. You can do that by first assigning the memory-mapped IP core into a variable and perform a write and read operation from the variable. In order to do the write operation, you will use the write method that receives two arguments which are register address and data value. As for the read method, you only need to pass the register address argument when you call the read method. 

When you read the math operation result from your custom IP core register, don’t forget to do two’s complement operation since the register output is in a raw form. You can use the code below to test the functionality of your design.

```python
# Call memory map IP module
mmioIP = ol.memory_map_ip_0

# Write data to the memory mapped register
mmioIP.write(0x00,4) # Write A value
mmioIP.write(0x04,-9) # Write B value
mmioIP.write(0x08,2) # Write C value

# Read result
calcRes = mmioIP.read(0x0C) # Read D value

# Two's complement conversion
if (calcRes > 0x7FFFFFFF):
    calcRes -= 0x100000000
    
# Print output result
print("Output result: {}".format(calcRes))
```

You can also make a Python function to “hide” the complexity of memory transaction operation and just call the function whenever you want without rewriting the entire memory write and read command. You can see the sample function in the code below.

```python
# Create function to encapsulate read and write process
def mathOp(a, b, c):
    mmioIP.write(0x00, a) # Write A value
    mmioIP.write(0x04, b) # Write B value
    mmioIP.write(0x08, c) # Write C value
    
    # Read result
    calcRes = mmioIP.read(0x0C) # Read D value

    # Two's complement conversion
    if (calcRes > 0x7FFFFFFF):
        calcRes -= 0x100000000
        
    return calcRes

# Test function
# Print output result
print("Output result: {}".format(mathOp(4, -9, 2)))
```



## :question: [Practice] Pattern Matching using Custom AXI Memory-Mapped IP 

After successfully implementing the basic AXI Memory Mapped Interface above, you need to implement a module to count number of pattern occurrence in a data. The input of this module are one 32-bit data and one 4-bit pattern data. The output of the module is number of pattern occurrence in the 32-bit data. For example, if you have 32-bit data `10100000101000001010000010100000` and 4-bit input pattern `1010`, the output of this module are 4 because there are 4 `1010` pattern occurrence in input data.

<p align="center">
    <img src="https://github.com/kaistseed/intro-to-xilinx-fpga/blob/ba2040c2c0f33598618073df356e9ae9206edcfd/01-intro-to-vivado-and-pynq/resources/pynq-download.jpg" width="70%" />
</p>
If the explanation is not clear enough, you can take a look at video in the link below:

- [**Creating Custom AXI Slave Interfaces Part 1 (Lesson 6)**](https://www.youtube.com/watch?v=meQcwzC4Vtk&ab_channel=MicroelectronicSystemsDesignResearchGroup)

- [**Creating Custom AXI Slave Interfaces Part 2 (Lesson 6)**](https://www.youtube.com/watch?v=Vs0h0kue7p4&ab_channel=MicroelectronicSystemsDesignResearchGroup)

In those videos, the author tries to implement pattern counter using AXI-Lite slave and AXI-Full slave. For the sake of simplicity, you only required to implement the pattern counter using AXI-Lite slave similar to math operation module you’ve previously made.




## :book: References

- *PYNQ main website*, February 2021. Available: [**http://www.pynq.io/**](http://www.pynq.io/)
- *PYNQ-Z1 documentation*, February 2021. Available: [**https://pynq.readthedocs.io/en/v2.6.1/getting_started/pynq_z1_setup.html**](https://pynq.readthedocs.io/en/v2.6.1/getting_started/pynq_z1_setup.html) -
- *A Simple Memory-Mapped Interface,* March 2021. Available: **http://eecs6111.mit.edu/6s193/pynq_lab2/**
