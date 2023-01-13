##################################################################
#                       [ Python Library ]
#  
#  Institution       : Korea Advanded Institute of Technology
#  Name              : Dalta Imam Maulana
# 
#  Project Name      : EE878 - Biomedical System Design - PYNQ
# 
#  Create Date       : 03/03/2020
#  File Name         : pybme280.py
#  Module Dependency : -
#  
#  Tool Version      : -
#  
#  Description:
#      High level python library which contain BME280 register
#      address and SPI protocol wrapper function 
#  
###################################################################
###################################################################
#                         Import Library                          #
###################################################################
import time
import cffi
import math
import numpy as np

###################################################################
#                     Constants Declaration                       #
###################################################################
# BME280 I2C Address
BME280_I2C_ADDR_PRIM   = 0x76
BME280_I2C_ADDR_SEC    = 0x77

# BME280 Chip ID
BME280_CHIP_ID         = 0x60

# Register Address
BME280_CHIP_ID_ADDR                = 0XD0
BME280_RESET_ADDR                  = 0XE0
BME280_TEMP_PRESS_CALIB_DATA_ADDR  = 0X88   
BME280_HUMIDITY_CALIB_DATA_ADDR    = 0XE1
BME280_PWR_CTRL_ADDR               = 0XF4
BME280_CTRL_HUM_ADDR               = 0XF2
BME280_CTRL_MEAS_ADDR              = 0XF4
BME280_CONFIG_ADDR                 = 0XF5
BME280_DATA_ADDR                   = 0XF7

# API Error Codes
BME280_E_NULL_PTR                  = -1
BME280_E_DEV_NOT_FOUND             = -2
BME280_E_INVALID_LEN               = -3
BME280_E_COMM_FAIL                 = -4
BME280_E_SLEEP_MODE_FAIL           = -5
BME280_E_NVM_COPY_FAILED           = -6

# API Warning Codes
BME280_W_INVALID_OSR_MACRO         = 1

# Sensor Data Size
BME280_TEMP_PRESS_CALIB_DATA_LEN   = 26
BME280_HUMIDITY_CALIB_DATA_LEN     = 7
BME280_P_T_H_DATA_LEN              = 8

# Sensor Power Modes
BME280_SLEEP_MODE                  = 0x00
BME280_FORCED_MODE                 = 0x01
BME280_NORMAL_MODE                 = 0x03

# Sensor Modes
BME280_PRESS                       = 0x01    
BME280_TEMP                        = 0x02      
BME280_HUM                         = 0x04      
BME280_ALL                         = 0x07    

# Oversampling Rate Register Selector
BME280_OSR_PRESS_SEL               = 1
BME280_OSR_TEMP_SEL                = 2
BME280_OSR_HUM_SEL                 = 4
BME280_FILTER_SEL                  = 8
BME280_STANDBY_SEL                 = 16
BME280_ALL_SETTINGS_SEL            = 0x1F

# Sensor Oversampling Macros
BME280_NO_OVERSAMPLING             = 0x00
BME280_OVERSAMPLING_1X             = 0x01
BME280_OVERSAMPLING_2X             = 0x02
BME280_OVERSAMPLING_4X             = 0x03
BME280_OVERSAMPLING_8X             = 0x04
BME280_OVERSAMPLING_16X            = 0x05

# Filter Coefficient Select
BME280_FILTER_COEFF_OFF            = 0x00
BME280_FILTER_COEFF_2              = 0x01
BME280_FILTER_COEFF_4              = 0x02
BME280_FILTER_COEFF_8              = 0x03
BME280_FILTER_COEFF_16             = 0x04

# Other Constants
BME280_STATUS_REG_ADDR             = 0xF3
BME280_SOFT_RESET_COMMAND          = 0xB6
BME280_STATUS_IM_UPDATE            = 0x01

# Measurement Delay Calculation Macros
BME280_MEAS_OFFSET                 = 1250
BME280_MEAS_DUR                    = 2300
BME280_PRES_HUM_MEAS_OFFSET        = 575
BME280_MEAS_SCALING_FACTOR         = 1000

# Standby Duration Select
BME280_STANDBY_TIME_0_5_MS         = 0x00
BME280_STANDBY_TIME_62_5_MS        = 0x01
BME280_STANDBY_TIME_125_MS         = 0x02
BME280_STANDBY_TIME_250_MS         = 0x03
BME280_STANDBY_TIME_500_MS         = 0x04
BME280_STANDBY_TIME_1000_MS        = 0x05
BME280_STANDBY_TIME_10_MS          = 0x06
BME280_STANDBY_TIME_20_MS          = 0x07

# Macros for selecting sensor settings
BME_280_OSR_SETTINGS        = 0x07
BME_280_FILTER_SETTINGS     = 0x18

# Macros for bitmasking
BME280_SENSOR_MODE_MSK      = 0x03
BME280_SENSOR_MODE_POS      = 0x00
BME280_CTRL_HUM_MSK         = 0x07
BME280_CTRL_HUM_POS         = 0x00
BME280_CTRL_PRESS_MSK       = 0x1C
BME280_CTRL_PRESS_POS       = 0x02
BME280_CTRL_TEMP_MSK        = 0xE0
BME280_CTRL_TEMP_POS        = 0x05
BME280_FILTER_MSK           = 0x1C
BME280_FILTER_POS           = 0x02
BME280_STANDBY_MSK          = 0xE0
BME280_STANDBY_POS          = 0x05

###################################################################
#                      Function Declaration                       #
###################################################################
class BME280:
    def __init__(self, master, cpol, cpha):
        """
            Create a new driver for BME280 sensor
            -------------------------------------
            Parameters
            master: Master SPI instance (AXI quad spi class)
            cpol: Clock polarity (0 - active high clock ; 1 - active low clock)
            cpha: Clock phase (0 - sample data at rising edge ; 1 - sample data at falling edge) 
        """
        # Initialize sensor
        self.uncomp_sensor_data = {
            "pressure":0,
            "temperature":0,
            "humidity":0
        }
        self.sensor_data = {
            "pressure":0,
            "temperature":0,
            "humidity":0
        }
        self.settings = {
            "pres_osr":0, 
            "temp_osr":0, 
            "humid_osr":0, 
            "filter_coef":0, 
            "stby_time":0
        }
        self.calib_data = {
            # Temperature sensor calibration coefficient
            "temp_coef_1":0,
            "temp_coef_2":0,
            "temp_coef_3":0,
            # Pressure sensor calibration coefficient
            "pres_coef_1":0,
            "pres_coef_2":0,
            "pres_coef_3":0,
            "pres_coef_4":0,
            "pres_coef_5":0,
            "pres_coef_6":0,
            "pres_coef_7":0,
            "pres_coef_8":0,
            "pres_coef_9":0,
            # Humidity sensor calibration coefficient
            "humid_coef_1":0,
            "humid_coef_2":0,
            "humid_coef_3":0,
            "humid_coef_4":0,
            "humid_coef_5":0,
            "humid_coef_6":0,
            # Intermediate temperature coefficient
            "temp_imm":0
        }
        
        # Initialize SPI Communication
        self.master = master
        self.spi_mode = 0 if (cpol == 0) else 1
        # Set SPI parameter
        if (self.spi_mode == 0):
            self.master.write(0x60,0b00_00000110)
        else:
            self.master.write(0x60,0b00_00011110) 

        # Read chip ID
        chip_id = self.SPIRead(BME280_CHIP_ID_ADDR, 1)
        
        # Check chip validity
        if (chip_id[0] == BME280_CHIP_ID):
            print("[Status] Chip is valid!")
        else:
            print("[Status] Chip isn't valid! Please check the sensor!")
            
    def SPIRead(self, reg_addr, read_len):
        """
            Method for reading from SPI slave
            -------------------------------------
            Parameters
            reg_addr: SPI slave register address 
        """
        # Declare internal variable
        count = 0
        receive_buffer = []
        slave_reg_addr = reg_addr
        
        # Set chip select to low (enable slave)
        self.master.write(0x70,0b1111_1110)
            
        # Send command to slave
        while (count < read_len):
            # Reset AXI quad SPI RX FIFO
            if (self.spi_mode == 0):
                self.master.write(0x60,0b00_01100110)
                self.master.write(0x60,0b00_00000110)
            else:
                self.master.write(0x60,0b00_01111110)
                self.master.write(0x60,0b00_00011110)

            # Write data to master TX FIFO
            tx_data  = (slave_reg_addr | 0x80) << 8
            self.master.write(0x68,tx_data)
            rx_data = self.master.read(0x6C)
            
            # Append data to received buffer
            receive_buffer.append(rx_data)
            
            # Increment counter and address
            count += 1
            slave_reg_addr += 1
        
        # Set chip select to high (disable slave)
        self.master.write(0x70,0b1111_1111)
        
        # Return value
        return receive_buffer
    
    def SPIWrite(self, reg_addr, data):
        """
            Method for writing to SPI slave
            -------------------------------------
            Parameters
            reg_addr: SPI slave register address
            data: Data to be written to SPI slave
        """
        # Set chip select to low (enable slave)
        self.master.write(0x70,0b1111_1110)
        
        # Reset AXI quad SPI RX FIFO
        if (self.spi_mode == 0):
            self.master.write(0x60,0b00_01100110)
            self.master.write(0x60,0b00_00000110)
        else:
            self.master.write(0x60,0b00_01111110)
            self.master.write(0x60,0b00_00011110)
        
        # Write data to master TX FIFO
        tx_data  = ((reg_addr & ~0x80) << 8) | data
        self.master.write(0x68,tx_data)
        
        # Set chip select to high (disable slave)
        self.master.write(0x70,0b1111_1111)

    def setSensorConfig(self, settings_sel):
        """
            Method for setting sensor configuration
            -------------------------------------
            Parameters
            settings_sel: Parameter for selecting which setting value to be overwritten
        """
        # Get sensor power mode
        sensor_mode = self.getSensorMode()
        # Set device to sleep mode
        if (sensor_mode != BME280_SLEEP_MODE):
            self.setSleepMode()
        
        # Check whether user wants to change oversampling or filter and standby settings
        if (BME_280_OSR_SETTINGS & settings_sel):
            self.setOSRSettings(settings_sel)
        if (BME_280_FILTER_SETTINGS & settings_sel):
            self.setFilterStby(settings_sel)

    def getSensorConfig(self):
        """
            Method for getting sensor configuration
            (pressure, humidity, temperature, filter, standby time)
            -------------------------------------
            Parameters
            -
        """
        # Declare internal variable
        bme_configs = []

        # Get humidity configuration
        hum_cfg = self.SPIRead(BME280_CTRL_HUM_ADDR, 1)
        bme_configs.append(hum_cfg[0])
        # Get status register data
        stat_cfg = self.SPIRead(BME280_STATUS_REG_ADDR, 1)
        bme_configs.append(stat_cfg[0])
        # Get pressure and temperature configuration
        temp_cfg = self.SPIRead(BME280_CTRL_MEAS_ADDR, 1)
        bme_configs.append(temp_cfg[0])
        # Get filter and standby time configuration
        filter_cfg = self.SPIRead(BME280_CONFIG_ADDR, 1)
        bme_configs.append(filter_cfg[0])

        # Parse data and store to its respective variables
        self.parseSensorConfig(bme_configs)

    def setSensorMode(self, sensor_mode):
        """
            Method for setting sensor power mode
            -------------------------------------
            Parameters
            sensor_mode: Operation mode of the sensor
        """
        # Read settings from slave
        sensor_config = self.SPIRead(BME280_PWR_CTRL_ADDR, 1)
        power_mode = self.getSensorMode()

        # Put device in sleep mode
        if (power_mode != BME280_SLEEP_MODE):
            self.setSleepMode()

        # Set new register value
        new_mode = self.setBitsPos(sensor_config[0], sensor_mode, BME280_SENSOR_MODE_MSK, BME280_SENSOR_MODE_POS)
        # Write result to slave
        self.SPIWrite(BME280_PWR_CTRL_ADDR, new_mode)

    def getSensorMode(self):
        """
            Method for getting sensor power mode
            -------------------------------------
            Parameters
            -
        """
        bme_settings = self.SPIRead(BME280_PWR_CTRL_ADDR, 1)
        sensor_mode = self.getBitsPos(bme_settings[0], BME280_SENSOR_MODE_MSK, BME280_SENSOR_MODE_POS)
        return sensor_mode

    def softReset(self):
        """
            Method for performing soft reset on the sensor
            -------------------------------------
            Parameters
            -
        """
        # Declare variable
        try_count = 5
        # Write self reset command to the sensor
        self.SPIWrite(BME280_RESET_ADDR, BME280_SOFT_RESET_COMMAND)

        # Wait for sensor to reboot
        while(True):
            # Startup time for the sensor is 2ms
            time.sleep(0.002)
            result = self.SPIRead(BME280_STATUS_REG_ADDR, 1)

            # Check sensor condition
            if ((try_count < 0) or ~(result[0] == BME280_STATUS_IM_UPDATE)):
                break

        # Check sensor condition
        if (result[0] == BME280_STATUS_IM_UPDATE):
            result = BME280_E_NVM_COPY_FAILED
        
        # Return result
        return result
    
    def getSensorData(self, comp_sel):
        """
            Method for reading data from sensor and compensate the received data
            -------------------------------------
            Parameters
            comp_sel: Parameter for selecting which data value to be compensated
        """
        # Read the pressure, temperature, and humidity data from the sensor
        pres_temp_data = self.SPIRead(BME280_DATA_ADDR, BME280_P_T_H_DATA_LEN)
        
        # Parse sensor data
        self.parseSensorData(pres_temp_data)
        # Compensate sensor data
        self.compensateData(comp_sel)

    def parseSensorData(self, reg_data):
        """
            Method for parsing raw sensor data and store it in the uncomp_data dictionary
            -------------------------------------
            Parameters
            reg_data: Array which contains the result from 
            getSensorData() method
        """
        # Parse pressure data
        msb_data = reg_data[0] << 12
        lsb_data =  reg_data[1] << 4
        xlsb_data = reg_data[2] >> 4
        self.uncomp_sensor_data["pressure"] = msb_data | lsb_data | xlsb_data

        # Parse temperature data
        msb_data = reg_data[3] << 12
        lsb_data =  reg_data[4] << 4
        xlsb_data = reg_data[5] >> 4
        self.uncomp_sensor_data["temperature"] = msb_data | lsb_data | xlsb_data
        
        # Parse humidity data
        msb_data = reg_data[6] << 8
        lsb_data =  reg_data[7]
        self.uncomp_sensor_data["humidity"] = msb_data | lsb_data

    def compensateData(self, comp_sel):
        """
            Method for compensating raw data reading from sensor
            -------------------------------------
            Parameters
            comp_sel: Parameter for selecting data value to be compensated
        """
        # Reset compensate data dictionary
        self.sensor_data["pressure"] = 0
        self.sensor_data["temperature"] = 0
        self.sensor_data["humidity"] = 0

        # Check which data to be compensated
        # Temperature compensation
        if (comp_sel & (BME280_PRESS | BME280_TEMP | BME280_HUM)):
            self.compensateTemperature()

        # Pressure compensation
        if (comp_sel & BME280_PRESS):
            self.compensatePressure()

        # Humidity compensation
        if (comp_sel & BME280_HUM):
            self.compensateHumidity()

    def maxMeasDelay(self):
        """
            Method for calculating maximum delay required for the sensor to finish
            the measurement (in milisecond)
            -------------------------------------
            Parameters
            -
        """
        # Declare variable
        osr_setting_map = [0, 1, 2, 4, 8, 16]

        # Map osr settings to actual osr values
        # Temperature osr
        if (self.settings["temp_osr"] <= 5):
            temp_osr = osr_setting_map[self.settings["temp_osr"]]
        else:
            temp_osr = 16
        # Pressure osr
        if (self.settings["pres_osr"] <= 5):
            pres_osr = osr_setting_map[self.settings["pres_osr"]]
        else:
            pres_osr = 16
        # Humidity osr
        if (self.settings["humid_osr"] <= 5):
            humid_osr = osr_setting_map[self.settings["humid_osr"]]
        else:
            humid_osr = 16

        # Calculate delay
        max_meas_delay = int((BME280_MEAS_OFFSET + (BME280_MEAS_DUR * temp_osr) +
                            ((BME280_MEAS_DUR * pres_osr) + BME280_PRES_HUM_MEAS_OFFSET) +
                            ((BME280_MEAS_DUR * humid_osr) + BME280_PRES_HUM_MEAS_OFFSET)) / BME280_MEAS_SCALING_FACTOR)

        # Return value
        return max_meas_delay

    def setOSRSettings(self, settings_sel):
        """
            Method for setting oversampling rate of the sensor
            -------------------------------------
            Parameters
            settings_sel: Parameter for selecting which setting value to be overwritten
        """
        # Check which register value to be updated
        # Update humidity oversampling value register
        if (settings_sel & BME280_OSR_HUM_SEL):
            self.setOSRHumid()
        # Update pressure and temperature oversampling value
        if ((settings_sel & BME280_OSR_PRESS_SEL) or (settings_sel & BME280_OSR_TEMP_SEL)):
            self.setOSRPresTemp(settings_sel)

    def setOSRHumid(self):
        """
            Method for setting humidity oversampling rate of the sensor
            -------------------------------------
            Parameters
            -
        """
        # Declare variable
        ctrl_hum = self.settings["humid_osr"] & BME280_CTRL_HUM_MSK
        # Write new register value to slave
        self.SPIWrite(BME280_CTRL_HUM_ADDR, ctrl_hum)

        # Write value to ctrl_meas register to update humidity oversampling 
        ctrl_meas = self.SPIRead(BME280_CTRL_MEAS_ADDR, 1)
        self.SPIWrite(BME280_CTRL_MEAS_ADDR, ctrl_meas[0])

    def setOSRPresTemp(self, settings_sel):
        """
            Method for setting pressure and temperature oversampling rate of the sensor
            -------------------------------------
            Parameters
            settings_sel: Parameter for selecting which oversampling value to be overwritten
        """
        # Get sensor setting value
        curr_settings = self.SPIRead(BME280_CTRL_MEAS_ADDR, 1)
        
        # Check which oversampling value to be updated
        # Pressure oversampling
        if (settings_sel & BME280_OSR_PRESS_SEL):
            curr_settings[0] = self.setBitsPos(curr_settings[0], self.settings["pres_osr"], BME280_CTRL_PRESS_MSK, BME280_CTRL_PRESS_POS)
        # Temperature oversampling
        if (settings_sel & BME280_OSR_TEMP_SEL):
            curr_settings[0] = self.setBitsPos(curr_settings[0], self.settings["temp_osr"], BME280_CTRL_TEMP_MSK, BME280_CTRL_TEMP_POS)
        
        # Write new value to register
        self.SPIWrite(BME280_CTRL_MEAS_ADDR, curr_settings[0])

    def setFilterStby(self, settings_sel):
        """
            Method for setting filter coefficient and standby time of the sensor
            -------------------------------------
            Parameters
            settings_sel: Parameter for selecting which setting value to be overwritten
        """
        # Get sensor setting value
        curr_settings = self.SPIRead(BME280_CONFIG_ADDR, 1)

        # Check which register value to be updated
        # Filter coefficient
        if (settings_sel & BME280_FILTER_SEL):
            curr_settings[0] = self.setBitsPos(curr_settings[0], self.settings["filter_coef"], BME280_FILTER_MSK, BME280_FILTER_POS)
        # Standby time
        if (settings_sel & BME280_STANDBY_SEL):
            curr_settings[0] = self.setBitsPos(curr_settings[0], self.settings["stby_time"], BME280_STANDBY_MSK, BME280_STANDBY_POS)

        # Write new value to register
        self.SPIWrite(BME280_CONFIG_ADDR, curr_settings[0])

    def parseSensorConfig(self, reg_data):
        """
            Method for parsing sensor configuration data
            -------------------------------------
            Parameters
            reg_data: Array which contains the result from 
            getSensorConfig() method
        """
        # Store data into sensor setting dictionary
        self.settings["pres_osr"] = self.getBitsPos(reg_data[2], BME280_CTRL_PRESS_MSK, BME280_CTRL_PRESS_POS)
        self.settings["temp_osr"] = self.getBitsPos(reg_data[2], BME280_CTRL_TEMP_MSK, BME280_CTRL_TEMP_POS)
        self.settings["humid_osr"] = self.getBitsPos(reg_data[0], BME280_CTRL_HUM_MSK, BME280_CTRL_HUM_POS)
        self.settings["filter_coef"] = self.getBitsPos(reg_data[3], BME280_FILTER_MSK, BME280_FILTER_POS)
        self.settings["stby_time"] = self.getBitsPos(reg_data[3], BME280_STANDBY_MSK, BME280_STANDBY_POS)

    def setSleepMode(self):
        """
            Method for putting device into sleep mode
            -------------------------------------
            Parameters
            -
        """
        # Get sensor configurations from slave
        self.getSensorConfig()
        # Soft reset the sensor
        self.softReset()
        # Reload sensor configurations
        self.reloadSensorSettings()
    
    def reloadSensorSettings(self):
        """
            Method for reloading sensor setting after soft reset
            -------------------------------------
            Parameters
            -
        """
        # Write oversampling settings to sensor
        self.setOSRSettings(BME280_ALL_SETTINGS_SEL)
        # Write filter coefficient and standby time to sensor
        self.setFilterStby(BME280_ALL_SETTINGS_SEL)
    
    def compensateTemperature(self):
        """
            Method for compensating raw temperature data
            -------------------------------------
            Parameters
            -
        """
        # Declare variables
        temp_min = -40
        temp_max = 85

        # Perform calculations
        comp_1 = np.double((self.uncomp_sensor_data["temperature"] / 16384.0) - (np.double(self.calib_data["temp_coef_1"]) / 1024.0))
        comp_1 = (comp_1 * np.double(self.calib_data["temp_coef_2"]))
        comp_2 = ((np.double(self.uncomp_sensor_data["temperature"]) / 131072.0) - (np.double(self.calib_data["temp_coef_1"]) / 8192.0))
        comp_2 = ((comp_2 * comp_2) * np.double(self.calib_data["temp_coef_3"]))

        # Store immediate temperature value
        self.calib_data["temp_imm"] = np.int32(comp_1 + comp_2)
        temperature = (comp_1 + comp_2) / 5120.0

        # Check temeperature value whether it pass threshold or not
        if (temperature < temp_min):
            temperature = temp_min
        elif (temperature > temp_max):
            temperature = temp_max
        else:
            temperature = temperature
            
        # Save temperature value
        self.sensor_data["temperature"] = temperature
    
    def compensatePressure(self):
        """
            Method for compensating raw pressure data
            -------------------------------------
            Parameters
            -
        """
        # Declare variables
        pressure_min = 30000.0
        pressure_max = 110000.0

        # Perform calculations
        comp_1 = (np.double(self.calib_data["temp_imm"]) / 2) - 64000.0
        comp_2 = comp_1 * comp_1 * np.double(self.calib_data["pres_coef_6"]) / 32768.0
        comp_2 = comp_2 + (comp_1 * np.double(self.calib_data["pres_coef_5"]) * 2.0)
        comp_2 = (comp_2 / 4.0) + (np.double(self.calib_data["pres_coef_4"]) * 65536.0)
        comp_3 = (np.double(self.calib_data["pres_coef_3"])) * comp_1 * comp_1 / 524288.0
        comp_1 = (comp_3 + (np.double(self.calib_data["pres_coef_3"]) * comp_1)) / 524288.0
        comp_1 = (1.0 + (comp_1 / 32768.0) * np.double(self.calib_data["pres_coef_1"]))

        # Avoid divide by zero oparation
        if (comp_1 > 0.0):
            pressure = 1048576.0 - self.uncomp_sensor_data["pressure"]
            pressure = (pressure - (comp_2 / 4096)) * 6250.0 / comp_1
            comp_1 = np.double(self.calib_data["pres_coef_9"]) * pressure * pressure / 2147483648.0
            comp_2 = pressure * np.double(self.calib_data["pres_coef_8"]) / 32768.0
            pressure = pressure + (comp_1 + comp_2 + np.double(self.calib_data["pres_coef_7"]) / 16.0)

            # Check whether pressure value is passing threshold or not
            if (pressure < pressure_min):
                pressure = pressure_min
            elif (pressure > pressure_max):
                pressure = pressure_max
            else:
                pressure = pressure
        else:
            pressure = pressure_min
        
        # Save pressure value
        self.sensor_data["pressure"] = pressure

    def compensateHumidity(self):
        """
            Method for compensating raw humidity data
            -------------------------------------
            Parameters
            -
        """
        # Declare variable
        humidity_min = 0.0
        humidity_max = 100.0

        # Perform calculations
        comp_1 = np.double(self.calib_data["temp_imm"]) - 76800.0
        comp_2 = (np.double(self.calib_data["humid_coef_4"]) * 64.0) + ((np.double(self.calib_data["humid_coef_5"]) / 16384.0) * comp_1)
        comp_3 = self.uncomp_sensor_data["humidity"] - comp_2
        comp_4 = np.double(self.calib_data["humid_coef_2"]) / 65536.0
        comp_5 = (1.0 + (np.double(self.calib_data["humid_coef_3"]) / 67108864.0) * comp_1)
        comp_6 = 1.0 + (np.double(self.calib_data["humid_coef_6"]) / 67108864.0) * comp_1 * comp_5
        comp_6 = comp_3 * comp_4 * comp_5 * comp_6
        humidity = comp_6 * (1.0 - np.double(np.double(self.calib_data["humid_coef_1"])) * comp_6 / 524288.0)

        # Check threshold value
        if (humidity > humidity_max):
            humidity = humidity_max
        elif (humidity < humidity_min):
            humidity = humidity_min
        else:
            humidity = humidity
        
        # Save humidity value
        self.sensor_data["humidity"] = humidity

    def getCalibData(self):
        """
            Method for getting calibration data from sensor and parse the data
            -------------------------------------
            Parameters
            -
        """
        # Get pressure and temperature calibration data
        pres_temp_calib = self.SPIRead(BME280_TEMP_PRESS_CALIB_DATA_ADDR, BME280_TEMP_PRESS_CALIB_DATA_LEN)
        self.parseTempPressCalib(pres_temp_calib)

        # Get humidity calibration data
        humid_calib = self.SPIRead(BME280_HUMIDITY_CALIB_DATA_ADDR, BME280_HUMIDITY_CALIB_DATA_LEN)
        self.parseHumidCalib(humid_calib)

    def parseTempPressCalib(self, reg_data):
        """
            Method for parsing sensor configuration data
            -------------------------------------
            Parameters
            reg_data: Array which contains the result from 
            getSensorConfig() method
        """
        # Parse calibration data
        self.calib_data["temp_coef_1"] = self.concatBytes(reg_data[1], reg_data[0])
        self.calib_data["temp_coef_2"] = self.concatBytes(reg_data[3], reg_data[2])
        self.calib_data["temp_coef_3"] = self.concatBytes(reg_data[5], reg_data[4])
        self.calib_data["pres_coef_1"] = self.concatBytes(reg_data[7], reg_data[6])
        self.calib_data["pres_coef_2"] = self.concatBytes(reg_data[9], reg_data[8])
        self.calib_data["pres_coef_3"] = self.concatBytes(reg_data[11], reg_data[10])
        self.calib_data["pres_coef_4"] = self.concatBytes(reg_data[13], reg_data[12])
        self.calib_data["pres_coef_5"] = self.concatBytes(reg_data[15], reg_data[14])
        self.calib_data["pres_coef_6"] = self.concatBytes(reg_data[17], reg_data[16])
        self.calib_data["pres_coef_7"] = self.concatBytes(reg_data[19], reg_data[18])
        self.calib_data["pres_coef_8"] = self.concatBytes(reg_data[21], reg_data[20])
        self.calib_data["pres_coef_9"] = self.concatBytes(reg_data[23], reg_data[22])
        self.calib_data["humid_coef_1"] = reg_data[25]

    def parseHumidCalib(self, reg_data):
        """
            Method for parsing sensor configuration data
            -------------------------------------
            Parameters
            reg_data: Array which contains the result from 
            getSensorConfig() method
        """
        # Parse calibration data
        self.calib_data["humid_coef_2"] = self.concatBytes(reg_data[1], reg_data[0])
        self.calib_data["humid_coef_3"] = reg_data[2]
        humid_coef_4_msb = reg_data[3] * 16
        humid_coef_4_lsb = reg_data[4] & 0x0F
        self.calib_data["humid_coef_4"] = humid_coef_4_msb | humid_coef_4_lsb
        humid_coef_5_msb = reg_data[5] * 16
        humid_coef_5_lsb = reg_data[4] >> 4
        self.calib_data["humid_coef_5"] = humid_coef_5_msb | humid_coef_5_lsb
        self.calib_data["humid_coef_6"] = reg_data[6]

    def setBitsPos(self, reg_data, data, bit_mask, mask_pos):
        """
            Method for writing new bit value to 
            register (bit-masking)
            -------------------------------------
            Parameters
            reg_data: Register data from slave
            mask_pos: Bit position of the data
            data: Data to be written to register
        """
        # Set new register value
        reg_mask = (reg_data & ~(bit_mask)) | ((data << mask_pos) & bit_mask)
        return reg_mask

    def getBitsPos(self, reg_data, bit_mask, mask_pos):
        reg_mask = (reg_data & bit_mask) >> mask_pos
        return reg_mask    
    
    def concatBytes(self, msb_data, lsb_data):
        """
            Method for combining two 8 bit data to 16 bit data
            -------------------------------------
            Parameters
            msb_data: 8 bit msb data
            lsb_data: 8 bit lsb data
        """
        result = (msb_data << 8) | lsb_data
        return result