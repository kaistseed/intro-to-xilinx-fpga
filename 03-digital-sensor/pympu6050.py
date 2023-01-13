##################################################################
#                       [ Python Library ]
#  
#  Institution       : Korea Advanded Institute of Technology
#  Name              : Dalta Imam Maulana
# 
#  Project Name      : EE878 - Biomedical System Design - PYNQ
# 
#  Create Date       : 03/16/2020
#  File Name         : pympu6050.py
#  Module Dependency : -
#  
#  Tool Version      : -
#  
#  Description:
#      High level python library which contain MPU6050 register
#      address and I2C protocol wrapper function 
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
# MPU6050 I2C Address
MPU6050_I2C_ADDR_PRIM   = 0x68
MPU6050_I2C_ADDR_SEC    = 0x69

# Register Address
MPU6050_REG_ACCEL_XOFFS_H     = 0x06
MPU6050_REG_ACCEL_XOFFS_L     = 0x07
MPU6050_REG_ACCEL_YOFFS_H     = 0x08
MPU6050_REG_ACCEL_YOFFS_L     = 0x09
MPU6050_REG_ACCEL_ZOFFS_H     = 0x0A
MPU6050_REG_ACCEL_ZOFFS_L     = 0x0B
MPU6050_REG_GYRO_XOFFS_H      = 0x13
MPU6050_REG_GYRO_XOFFS_L      = 0x14
MPU6050_REG_GYRO_YOFFS_H      = 0x15
MPU6050_REG_GYRO_YOFFS_L      = 0x16
MPU6050_REG_GYRO_ZOFFS_H      = 0x17
MPU6050_REG_GYRO_ZOFFS_L      = 0x18
MPU6050_REG_CONFIG            = 0x1A
MPU6050_REG_GYRO_CONFIG       = 0x1B
MPU6050_REG_ACCEL_CONFIG      = 0x1C 
MPU6050_REG_FF_THRESHOLD      = 0x1D
MPU6050_REG_FF_DURATION       = 0x1E
MPU6050_REG_MOT_THRESHOLD     = 0x1F
MPU6050_REG_MOT_DURATION      = 0x20
MPU6050_REG_ZMOT_THRESHOLD    = 0x21
MPU6050_REG_ZMOT_DURATION     = 0x22
MPU6050_REG_INT_PIN_CFG       = 0x37 
MPU6050_REG_INT_ENABLE        = 0x38 
MPU6050_REG_INT_STATUS        = 0x3A
MPU6050_REG_ACCEL_XOUT_H      = 0x3B
MPU6050_REG_ACCEL_XOUT_L      = 0x3C
MPU6050_REG_ACCEL_YOUT_H      = 0x3D
MPU6050_REG_ACCEL_YOUT_L      = 0x3E
MPU6050_REG_ACCEL_ZOUT_H      = 0x3F
MPU6050_REG_ACCEL_ZOUT_L      = 0x40
MPU6050_REG_TEMP_OUT_H        = 0x41
MPU6050_REG_TEMP_OUT_L        = 0x42
MPU6050_REG_GYRO_XOUT_H       = 0x43
MPU6050_REG_GYRO_XOUT_L       = 0x44
MPU6050_REG_GYRO_YOUT_H       = 0x45
MPU6050_REG_GYRO_YOUT_L       = 0x46
MPU6050_REG_GYRO_ZOUT_H       = 0x47
MPU6050_REG_GYRO_ZOUT_L       = 0x48
MPU6050_REG_MOT_DETECT_STATUS = 0x61
MPU6050_REG_MOT_DETECT_CTRL   = 0x69
MPU6050_REG_USER_CTRL         = 0x6A 
MPU6050_REG_PWR_MGMT_1        = 0x6B 
MPU6050_REG_WHO_AM_I          = 0x75 

# Macro for Configuring Clock Settings
MPU6050_CLOCK_KEEP_RESET      = 0b111
MPU6050_CLOCK_EXTERNAL_19MHZ  = 0b101
MPU6050_CLOCK_EXTERNAL_32KHZ  = 0b100
MPU6050_CLOCK_PLL_ZGYRO       = 0b011
MPU6050_CLOCK_PLL_YGYRO       = 0b010
MPU6050_CLOCK_PLL_XGYRO       = 0b001
MPU6050_CLOCK_INTERNAL_8MHZ   = 0b000

# Macro for configuring low pass filter settings
MPU6050_DLPF_6                = 0b110
MPU6050_DLPF_5                = 0b101
MPU6050_DLPF_4                = 0b100
MPU6050_DLPF_3                = 0b011
MPU6050_DLPF_2                = 0b010
MPU6050_DLPF_1                = 0b001
MPU6050_DLPF_0                = 0b000

# Macro for configuring high pass filter settings
MPU6050_DHPF_HOLD             = 0b111
MPU6050_DHPF_0_63HZ           = 0b100
MPU6050_DHPF_1_25HZ           = 0b011
MPU6050_DHPF_2_5HZ            = 0b010
MPU6050_DHPF_5HZ              = 0b001
MPU6050_DHPF_RESET            = 0b000

# Macro for configuring sensor sampling time
MPU6050_DELAY_3MS             = 0b11
MPU6050_DELAY_2MS             = 0b10
MPU6050_DELAY_1MS             = 0b01
MPU6050_NO_DELAY              = 0b00

# Macros for configuring gyroscope sensitivity
MPU6050_SCALE_2000DPS         = 0b11
MPU6050_SCALE_1000DPS         = 0b10
MPU6050_SCALE_500DPS          = 0b01
MPU6050_SCALE_250DPS          = 0b00

# Macros for configuring accelerator sensitivity
MPU6050_RANGE_16G             = 0b11
MPU6050_RANGE_8G              = 0b10
MPU6050_RANGE_4G              = 0b01
MPU6050_RANGE_2G              = 0b00


###################################################################
#                      Function Declaration                       #
###################################################################
# Call FFI function
ffi = cffi.FFI()

class MPU6050:
    def __init__(self, master, sensor_scale, sensor_range):
        """
            Create a new driver for MPU6050 sensor
            -------------------------------------
            Parameters
            master: I2C master instance (AXIIIC Module)
            slv_addr: I2C slave address 
        """
        # Initialize sensor
        self.master = master
        self.slv_addr = MPU6050_I2C_ADDR_PRIM
        self.buffer = ffi.new("unsigned char [32]")
        
        # Declare dictionary for storing status and data
        # Raw accelerometer and gyroscope data
        self.raw_accel = {
            "x_axis":0,
            "y_axis":0,
            "z_axis":0
        }
        self.raw_gyro = {
            "x_axis":0,
            "y_axis":0,
            "z_axis":0
        }
        # Normalized accelerometer and gyroscope data
        self.norm_accel = {
            "x_axis":0,
            "y_axis":0,
            "z_axis":0
        }
        self.norm_gyro = {
            "x_axis":0,
            "y_axis":0,
            "z_axis":0
        }
        # Threshold and delta value for gyroscope
        self.threshold_gyro = {
            "x_axis":0,
            "y_axis":0,
            "z_axis":0
        }
        self.delta_gyro = {
            "x_axis":0,
            "y_axis":0,
            "z_axis":0
        }
        # Threshold value data
        self.threshold_data = {
            "x_axis":0,
            "y_axis":0,
            "z_axis":0
        }
        # Sensor status
        self.sensor_activities = {
            "data_overflow":False,
            "sensor_freefall":False,
            "sensor_inactive":False,
            "sensor_active":False,
            "pos_value_x":False,
            "pos_value_y":False,
            "pos_value_z":False,
            "neg_value_x":False,
            "neg_value_y":False,
            "neg_value_z":False,
            "sensor_data_ready":False
        }

        # Internal config variables
        self.use_calibrate = False
        self.actual_threshold = 0
        self.dps_per_digit = 0.0
        self.range_per_digit = 0.0

        # Read chip ID
        chip_id = self.I2CRead(MPU6050_REG_WHO_AM_I, 1)
        
        # Check chip validity
        if (chip_id[0] == 0x98):
            print("[Status] Chip is valid!")
        else:
            print("[Status] Chip isn't valid! Please check the sensor!")
            print("Chip ID: {}".format(hex(chip_id[0])))
            return

        # Set clock source
        self.setSensorClock(MPU6050_CLOCK_PLL_XGYRO)

        # Set scale and range
        self.setSensorScale(sensor_scale)
        self.setSensorRange(sensor_range)

        # Disable sleep mode
        self.setSleepMode(False)

    def I2CRead(self, reg_addr, len):
        """
            Method for reading from I2C slave
            -------------------------------------
            Parameters
            reg_addr: I2C slave register address 
        """
        # Declare internal variable
        count = 0
        receive_buffer = []
        slave_reg_addr = reg_addr

        # Send command to slave
        while (count < len):
            self.buffer[0] = slave_reg_addr
            self.master.send(self.slv_addr, self.buffer, 1, 1)
            self.master.receive(self.slv_addr, self.buffer, 1)
            self.master.wait()

            # Clear interrupt register
            self.master.write(0x20, self.master.read(0x20))
            
            # Append data to received buffer
            receive_buffer.append(self.buffer[0])
            
            # Increment counter and address
            count += 1
            slave_reg_addr += 1
        
        # Return value
        return receive_buffer

    def I2CWrite(self, reg_addr, data):
        """
            Method for writing to I2C slave
            -------------------------------------
            Parameters
            reg_addr: I2C slave register address
            data: Data to be written to I2C slave
        """
        # Send data to slave
        self.buffer[0] = reg_addr
        self.buffer[1] = data
        self.master.send(self.slv_addr, self.buffer, 2)
        self.master.wait()

        # Clear interrupt register
        self.master.write(0x20, self.master.read(0x20))
    
    def readRegisterBit(self, reg_addr, bit_pos):
        """
            Method for reading bit value from specific position
            ---------------------------------------------------
            Parameters
            reg_addr: I2C slave register address
            bit_pos: Bit position in the data
        """
        # Read data from register
        reg_data = self.I2CRead(reg_addr, 1)
        # Get desired bit
        bit_data = (reg_data[0] >> bit_pos) & 1
        # Return value
        return bit_data

    def writeRegisterBit(self, reg_addr, bit_pos, bit_state):
        """
            Method for writing bit value from specific position
            ---------------------------------------------------
            Parameters
            reg_addr: I2C slave register address
            bit_pos: Bit position in the data
            bit_state: State of bit (set to True or False) 
        """
        # Read data from register
        reg_data = self.I2CRead(reg_addr, 1)
        # Set bit state
        if (bit_state):
            new_data = reg_data[0] | (1 << bit_pos)
        else:
            new_data = reg_data[0] & ~(1 << bit_pos)
        # Write data back to sensor
        self.I2CWrite(reg_addr, new_data)
    
    def getSensorClock(self):
        """
            Method for getting sensor clock configuration
            -------------------------------------
            Parameters
            -
        """
        # Read current clock setting from sensor
        current_setting = self.I2CRead(MPU6050_REG_PWR_MGMT_1, 1)
        # Mask clock setting
        clock_config = current_setting[0] & 0b00000111
        # Return result
        return clock_config

    def setSensorClock(self, clock_mode):
        """
            Method for setting sensor clock source
            -------------------------------------
            Parameters
            clock_mode: Sensor clock source
        """
        # Read current clock setting from sensor
        current_setting = self.I2CRead(MPU6050_REG_PWR_MGMT_1, 1)
        # Mask clock setting
        new_setting = current_setting[0] & 0b11111000
        # Write new clock setting
        new_setting = new_setting | clock_mode
        # Write data to sensor
        self.I2CWrite(MPU6050_REG_PWR_MGMT_1, new_setting)
    
    def getSensorScale(self):
        """
            Method for getting sensor scale configuration
            -------------------------------------
            Parameters
            -
        """
        # Read current clock setting from sensor
        current_setting = self.I2CRead(MPU6050_REG_GYRO_CONFIG, 1)
        # Mask clock setting
        scale_config = (current_setting[0] & 0b00011000) >> 3
        # Return result
        return scale_config

    def setSensorScale(self, scale_setting):
        """
            Method for setting sensor scale parameter
            -------------------------------------
            Parameters
            scale_setting: Sensor scale configuration
        """
        # Change internal config for calculation
        if (scale_setting == MPU6050_SCALE_250DPS):
            self.dps_per_digit = 0.007633
        elif (scale_setting == MPU6050_SCALE_500DPS):
            self.dps_per_digit = 0.015267
        elif (scale_setting == MPU6050_SCALE_1000DPS):
            self.dps_per_digit = 0.030487
        elif (scale_setting == MPU6050_SCALE_2000DPS):
            self.dps_per_digit = 0.060975
        else:
            self.dps_per_digit = 0.007633

        # Read current clock setting from sensor
        current_setting = self.I2CRead(MPU6050_REG_GYRO_CONFIG, 1)
        # Mask clock setting
        new_setting = current_setting[0] & 0b11100111
        # Write new clock setting
        new_setting = new_setting | (scale_setting << 3)
        # Write data to sensor
        self.I2CWrite(MPU6050_REG_GYRO_CONFIG, new_setting)

    def getSensorRange(self):
        """
            Method for getting sensor range configuration
            -------------------------------------
            Parameters
            -
        """
        # Read current clock setting from sensor
        current_setting = self.I2CRead(MPU6050_REG_ACCEL_CONFIG, 1)
        # Mask clock setting
        range_config = (current_setting[0] & 0b00011000) >> 3
        # Return result
        return range_config

    def setSensorRange(self, range_setting):
        """
            Method for setting sensor range parameter
            -------------------------------------
            Parameters
            scale_setting: Sensor range configuration
        """
        # Change internal config for calculation
        if (range_setting == MPU6050_RANGE_2G):
            self.range_per_digit = 0.000061
        elif (range_setting == MPU6050_RANGE_4G):
            self.range_per_digit = 0.000122
        elif (range_setting == MPU6050_RANGE_8G):
            self.range_per_digit = 0.000244
        elif (range_setting == MPU6050_RANGE_16G):
            self.range_per_digit = 0.0004882
        else:
            self.range_per_digit = 0.000061

        # Read current clock setting from sensor
        current_setting = self.I2CRead(MPU6050_REG_ACCEL_CONFIG, 1)
        # Mask clock setting
        new_setting = current_setting[0] & 0b11100111
        # Write new clock setting
        new_setting = new_setting | (range_setting << 3)
        # Write data to sensor
        self.I2CWrite(MPU6050_REG_ACCEL_CONFIG, new_setting)

    def setDHPFMode(self, dhpf_mode):
        """
            Method for configuring high pass filter setting
            -----------------------------------------------
            Parameters
            dhpf_mode: High pass filter mode
        """
        # Read current high pass filter mode from sensor
        current_setting = self.I2CRead(MPU6050_REG_ACCEL_CONFIG, 1)
        # Mask clock setting
        new_setting = current_setting[0] & 0b11111000
        # Write new clock setting
        new_setting = new_setting | dhpf_mode
        # Write data to sensor
        self.I2CWrite(MPU6050_REG_ACCEL_CONFIG, new_setting)

    def setDLPFMode(self, dlpf_mode):
        """
            Method for configuring low pass filter setting
            ----------------------------------------------
            Parameters
            dlpf_mode: Low pass filter mode
        """
        # Read current clock setting from sensor
        current_setting = self.I2CRead(MPU6050_REG_CONFIG, 1)
        # Mask clock setting
        new_setting = current_setting[0] & 0b11111000
        # Write new clock setting
        new_setting = new_setting | dlpf_mode
        # Write data to sensor
        self.I2CWrite(MPU6050_REG_CONFIG, new_setting)

    def getSleepMode(self):
        """
            Method for getting sensor sleep mode status
            -------------------------------------------
            Parameters
            -
        """
        # Read data from sensor
        sleep_mode = self.readRegisterBit(MPU6050_REG_PWR_MGMT_1, 6)
        # Return data
        return sleep_mode
    
    def setSleepMode(self, sleep_state):
        """
            Method for setting sensor sleep mode 
            ------------------------------------
            Parameters
            sleep_state: Set to TRUE for sleep, wake up otherwise
        """
        # Write data to sensor
        self.writeRegisterBit(MPU6050_REG_PWR_MGMT_1, 6, sleep_state)
    
    def getIntZeroMotion(self):
        """
            Method for getting zero motion mode status
            -------------------------------------------
            Parameters
            -
        """
        # Read data from sensor
        zero_motion = self.readRegisterBit(MPU6050_REG_INT_ENABLE, 5)
        # Return data
        return zero_motion

    def setIntZeroMotion(self, zero_motion_state):
        """
            Method for getting zero motion mode status
            -------------------------------------------
            Parameters
            zero_motion_state: Set to TRUE to enable, disable otherwise
        """
        # Write data to sensor
        self.writeRegisterBit(MPU6050_REG_INT_ENABLE, 5, zero_motion_state)

    def getIntMotion(self):
        """
            Method for getting motion mode status
            -------------------------------------------
            Parameters
            -
        """
        # Read data from sensor
        zero_motion = self.readRegisterBit(MPU6050_REG_INT_ENABLE, 6)
        # Return data
        return zero_motion

    def setIntMotion(self, motion_state):
        """
            Method for setting motion mode
            -------------------------------------------
            Parameters
            motion_state: Set to TRUE to enable, disable otherwise
        """
        # Write data to sensor
        self.writeRegisterBit(MPU6050_REG_INT_ENABLE, 6, motion_state)

    def getIntFreefall(self):
        """
            Method for getting freefall mode status
            -------------------------------------------
            Parameters
            -
        """
        # Read data from sensor
        free_fall = self.readRegisterBit(MPU6050_REG_INT_ENABLE, 7)
        # Return data
        return free_fall

    def setIntFreefall(self, freefall_state):
        """
            Method for setting freefall mode
            -------------------------------------------
            Parameters
            freefall_state: Set to TRUE to enable, disable otherwise
        """
        # Write data to sensor
        self.writeRegisterBit(MPU6050_REG_INT_ENABLE, 7, freefall_state)

    def getMotionDetectionThreshold(self):
        """
            Method for getting motion detection threshold value
            ---------------------------------------------------
            Parameters
            -
        """
        # Read data from sensor
        current_data = self.I2CRead(MPU6050_REG_MOT_THRESHOLD, 1)
        threshold_value = current_data[0]
        # Return data
        return threshold_value

    def setMotionDetectionThreshold(self, threshold):
        """
            Method for setting motion detection threshold value
            -------------------------------------------
            Parameters
            threshold: Motion detection threshold value
        """
        # Write data to sensor
        self.I2CWrite(MPU6050_REG_MOT_THRESHOLD, threshold)

    def getZeroMotionDetectionThreshold(self):
        """
            Method for getting zero motion detection threshold value
            --------------------------------------------------------
            Parameters
            -
        """
        # Read data from sensor
        current_data = self.I2CRead(MPU6050_REG_ZMOT_THRESHOLD, 1)
        threshold_value = current_data[0]
        # Return data
        return threshold_value

    def setZeroMotionDetectionThreshold(self, threshold):
        """
            Method for setting zero motion detection threshold value
            --------------------------------------------------------
            Parameters
            threshold: Motion detection threshold value
        """
        # Write data to sensor
        self.I2CWrite(MPU6050_REG_ZMOT_THRESHOLD, threshold)

    def getFreefallDetectionThreshold(self):
        """
            Method for getting freefall detection threshold value
            --------------------------------------------------------
            Parameters
            -
        """
        # Read data from sensor
        current_data = self.I2CRead(MPU6050_REG_FF_THRESHOLD, 1)
        threshold_value = current_data[0]
        # Return data
        return threshold_value

    def setFreefallDetectionThreshold(self, threshold):
        """
            Method for setting zero motion detection threshold value
            --------------------------------------------------------
            Parameters
            threshold: Freefall threshold value
        """
        # Write data to sensor
        self.I2CWrite(MPU6050_REG_FF_THRESHOLD, threshold)

    def getMotionDetectionDuration(self):
        """
            Method for getting motion detection duration value
            ---------------------------------------------------
            Parameters
            -
        """
        # Read data from sensor
        current_data = self.I2CRead(MPU6050_REG_MOT_DURATION, 1)
        duration_value = current_data[0]
        # Return data
        return duration_value

    def setMotionDetectionDuration(self, duration):
        """
            Method for setting motion detection duration value
            ---------------------------------------------------
            Parameters
            duration: Motion detection duration value
        """
        # Write data to sensor
        self.I2CWrite(MPU6050_REG_MOT_DURATION, duration)

    def getZeroMotionDetectionDuration(self):
        """
            Method for getting zero motion detection duration value
            -------------------------------------------------------
            Parameters
            -
        """
        # Read data from sensor
        current_data = self.I2CRead(MPU6050_REG_ZMOT_DURATION, 1)
        duration_value = current_data[0]
        # Return data
        return duration_value

    def setZeroMotionDetectionDuration(self, duration):
        """
            Method for setting zero motion detection duration value
            --------------------------------------------------------
            Parameters
            duration: Motion detection duration value
        """
        # Write data to sensor
        self.I2CWrite(MPU6050_REG_ZMOT_DURATION, duration)

    def getFreefallDetectionDuration(self):
        """
            Method for getting freefall detection duration value
            ---------------------------------------------------
            Parameters
            -
        """
        # Read data from sensor
        current_data = self.I2CRead(MPU6050_REG_FF_DURATION, 1)
        duration_value = current_data[0]
        # Return data
        return duration_value

    def setFreefallDetectionDuration(self, duration):
        """
            Method for setting freefall detection duration value
            ---------------------------------------------------
            Parameters
            duration: Freefall detection duration value
        """
        # Write data to sensor
        self.I2CWrite(MPU6050_REG_FF_DURATION, duration)

    def getI2CMasterMode(self):
        """
            Method for getting I2C master mode status
            -------------------------------------------
            Parameters
            -
        """
        # Read data from sensor
        i2c_mode = self.readRegisterBit(MPU6050_REG_USER_CTRL, 5)
        # Return data
        return i2c_mode

    def setI2CMasterMode(self, i2c_mode):
        """
            Method for setting I2C master mode
            -------------------------------------------
            Parameters
            i2c_mode: Set to TRUE to enable, disable otherwise
        """
        # Write data to sensor
        self.writeRegisterBit(MPU6050_REG_USER_CTRL, 5, i2c_mode)

    def getI2CBypass(self):
        """
            Method for getting I2C master mode status
            -------------------------------------------
            Parameters
            -
        """
        # Read data from sensor
        i2c_bypass = self.readRegisterBit(MPU6050_REG_INT_PIN_CFG, 1)
        # Return data
        return i2c_bypass

    def setI2CBypass(self, i2c_bypass):
        """
            Method for setting I2C master mode
            -------------------------------------------
            Parameters
            i2c_bypass: Set to TRUE to enable, disable otherwise
        """
        # Write data to sensor
        self.writeRegisterBit(MPU6050_REG_INT_PIN_CFG, 1, i2c_bypass)
    
    def getPowerOnDelay(self):
        """
            Method for getting power on delay status
            ---------------------------------------------------
            Parameters
            -
        """
        # Read data from sensor
        current_data = self.I2CRead(MPU6050_REG_MOT_DETECT_CTRL, 1)
        on_delay = (current_data[0] & 0b00110000) >> 4
        # Return data
        return on_delay

    def setPowerOnDelay(self, delay):
        """
            Method for setting power on delay status
            ---------------------------------------------------
            Parameters
            delay: power on delay value
        """
        # Read data from sensor
        current_data = self.I2CRead(MPU6050_REG_MOT_DETECT_CTRL, 1)
        new_data = (current_data[0] & 0b11001111) | (delay << 4)
        # Write data to sensor
        self.I2CWrite(MPU6050_REG_MOT_DETECT_CTRL, new_data)

    def getIntStatus(self):
        """
            Method for getting sensor status
            ---------------------------------------------------
            Parameters
            -
        """
        # Read data from sensor
        current_data = self.I2CRead(MPU6050_REG_INT_STATUS, 1)
        sensor_status = current_data[0]
        # Return data
        return sensor_status
    
    def getSensorActivities(self):
        """
            Method for getting sensor activities
            ---------------------------------------------------
            Parameters
            -
        """
        # Read data from sensor
        reg_status = self.I2CRead(MPU6050_REG_INT_STATUS, 1)
        detect_status = self.I2CRead(MPU6050_REG_MOT_DETECT_STATUS, 1)

        # Parse data from sensor
        self.sensor_activities["data_overflow"] = (reg_status[0] >> 4) & 1
        self.sensor_activities["sensor_freefall"] = (reg_status[0] >> 7) & 1
        self.sensor_activities["sensor_inactive"] = (reg_status[0] >> 5) & 1
        self.sensor_activities["sensor_active"] = (reg_status[0] >> 6) & 1
        self.sensor_activities["sensor_data_ready"] = (reg_status[0]) & 1

        self.sensor_activities["neg_value_x"] = (detect_status[0] >> 7) & 1
        self.sensor_activities["pos_value_x"] = (detect_status[0] >> 6) & 1
        self.sensor_activities["neg_value_y"] = (detect_status[0] >> 5) & 1
        self.sensor_activities["pos_value_y"] = (detect_status[0] >> 4) & 1
        self.sensor_activities["neg_value_z"] = (detect_status[0] >> 3) & 1
        self.sensor_activities["pos_value_z"] = (detect_status[0] >> 2) & 1

    def getRawAccel(self):
        """
            Method for getting raw accelerometer data
            ---------------------------------------------------
            Parameters
            -
        """
        # Read data from sensor (6 register address)
        raw_accel_data = self.I2CRead(MPU6050_REG_ACCEL_XOUT_H, 6)

        # Shift and concate data
        self.raw_accel["x_axis"] = (raw_accel_data[0] << 8) | raw_accel_data[1]
        self.raw_accel["y_axis"] = (raw_accel_data[2] << 8) | raw_accel_data[3]
        self.raw_accel["z_axis"] = (raw_accel_data[4] << 8) | raw_accel_data[5]
    
    def getNormAccel(self):
        """
            Method for getting normalized accelerometer data
            ---------------------------------------------------
            Parameters
            -
        """
        # Read raw accelerometer data
        self.getRawAccel()

        # Normalize data
        self.norm_accel["x_axis"] = self.raw_accel["x_axis"] * self.range_per_digit * 9.80665
        self.norm_accel["y_axis"] = self.raw_accel["y_axis"] * self.range_per_digit * 9.80665
        self.norm_accel["z_axis"] = self.raw_accel["z_axis"] * self.range_per_digit * 9.80665

    def getScaledAccel(self):
        """
            Method for getting scaled accelerometer data
            ---------------------------------------------------
            Parameters
            -
        """
        # Read raw accelerometer data
        self.getRawAccel()

        # Normalize data
        self.norm_accel["x_axis"] = self.raw_accel["x_axis"] * self.range_per_digit
        self.norm_accel["y_axis"] = self.raw_accel["y_axis"] * self.range_per_digit
        self.norm_accel["z_axis"] = self.raw_accel["z_axis"] * self.range_per_digit

    def getRawGyro(self):
        """
            Method for getting raw gyroscope data
            ---------------------------------------------------
            Parameters
            -
        """
        # Read data from sensor (6 register address)
        raw_gyro_data = self.I2CRead(MPU6050_REG_GYRO_XOUT_H, 6)

        # Shift and concate data
        self.raw_gyro["x_axis"] = (raw_gyro_data[0] << 8) | raw_gyro_data[1]
        self.raw_gyro["y_axis"] = (raw_gyro_data[2] << 8) | raw_gyro_data[3]
        self.raw_gyro["z_axis"] = (raw_gyro_data[4] << 8) | raw_gyro_data[5]
    
    def getNormGyro(self):
        """
            Method for getting normalized gyroscope data
            ---------------------------------------------------
            Parameters
            -
        """
        # Read raw accelerometer data
        self.getRawGyro()

        # Check for calibration
        if (self.use_calibrate):
            self.norm_gyro["x_axis"] = (self.raw_gyro["x_axis"] - self.delta_gyro["x_axis"]) * self.dps_per_digit
            self.norm_gyro["y_axis"] = (self.raw_gyro["y_axis"] - self.delta_gyro["y_axis"]) * self.dps_per_digit
            self.norm_gyro["z_axis"] = (self.raw_gyro["z_axis"] - self.delta_gyro["z_axis"]) * self.dps_per_digit
        else:
            self.norm_gyro["x_axis"] = self.raw_gyro["x_axis"] * self.dps_per_digit
            self.norm_gyro["y_axis"] = self.raw_gyro["y_axis"] * self.dps_per_digit
            self.norm_gyro["z_axis"] = self.raw_gyro["z_axis"] * self.dps_per_digit

        # Check for threshold
        if (self.actual_threshold):
            if (abs(self.norm_gyro["x_axis"]) < self.threshold_gyro["x_axis"]):
                self.norm_gyro["x_axis"] = 0.0
            if (abs(self.norm_gyro["y_axis"]) < self.threshold_gyro["y_axis"]):
                self.norm_gyro["y_axis"] = 0.0
            if (abs(self.norm_gyro["z_axis"]) < self.threshold_gyro["z_axis"]):
                self.norm_gyro["z_axis"] = 0.0


    def getTemperature(self):
        """
            Method for getting temperature data
            ---------------------------------------------------
            Parameters
            -
        """
        # Read temperature data
        sensor_data = self.I2CRead(MPU6050_REG_TEMP_OUT_H, 2)
        
        # Process raw data
        temp_data = ((sensor_data[0] << 8) | sensor_data[1])
        temp_data = (temp_data / 340) + 36.53

        # Return data
        return temp_data

    def getGyroOffsetX(self):
        """
            Method for getting gyroscope X offset value
            ---------------------------------------------------
            Parameters
            -
        """
        # Read register data
        register_data = self.I2CRead(MPU6050_REG_GYRO_XOFFS_H, 2)
        # Process raw data
        gyro_x_offset = ((register_data[0] << 8) | register_data[1])
        # Return data
        return gyro_x_offset
    
    def getGyroOffsetY(self):
        """
            Method for getting gyroscope Y offset value
            ---------------------------------------------------
            Parameters
            -
        """
        # Read register data
        register_data = self.I2CRead(MPU6050_REG_GYRO_YOFFS_H, 2)
        # Process raw data
        gyro_y_offset = ((register_data[0] << 8) | register_data[1])
        # Return data
        return gyro_y_offset

    def getGyroOffsetZ(self):
        """
            Method for getting gyroscope Z offset value
            ---------------------------------------------------
            Parameters
            -
        """
        # Read register data
        register_data = self.I2CRead(MPU6050_REG_GYRO_ZOFFS_H, 2)
        # Process raw data
        gyro_z_offset = ((register_data[0] << 8) | register_data[1])
        # Return data
        return gyro_z_offset

    def setGyroOffsetX(self, high_offset, low_offset):
        """
            Method for setting gyroscope X offset value
            ---------------------------------------------------
            Parameters
            -
        """
        # Write first 8-bit (high bit) data to register
        self.I2CWrite(MPU6050_REG_GYRO_XOFFS_H, high_offset)
        # Write second 8-bit (low bit) data to register
        self.I2CWrite(MPU6050_REG_GYRO_XOFFS_L, low_offset)
    
    def setGyroOffsetY(self, high_offset, low_offset):
        """
            Method for setting gyroscope Y offset value
            ---------------------------------------------------
            Parameters
            -
        """
        # Write first 8-bit (high bit) data to register
        self.I2CWrite(MPU6050_REG_GYRO_YOFFS_H, high_offset)
        # Write second 8-bit (low bit) data to register
        self.I2CWrite(MPU6050_REG_GYRO_YOFFS_L, low_offset)
    
    def setGyroOffsetZ(self, high_offset, low_offset):
        """
            Method for setting gyroscope Z offset value
            ---------------------------------------------------
            Parameters
            -
        """
        # Write first 8-bit (high bit) data to register
        self.I2CWrite(MPU6050_REG_GYRO_ZOFFS_H, high_offset)
        # Write second 8-bit (low bit) data to register
        self.I2CWrite(MPU6050_REG_GYRO_ZOFFS_L, low_offset)

    def getAccelOffsetX(self):
        """
            Method for getting accelerometer X offset value
            ---------------------------------------------------
            Parameters
            -
        """
        # Read register data
        register_data = self.I2CRead(MPU6050_REG_ACCEL_XOFFS_H, 2)
        # Process raw data
        accel_x_offset = ((register_data[0] << 8) | register_data[1])
        # Return data
        return accel_x_offset
    
    def getAccelOffsetY(self):
        """
            Method for getting accelerometer Y offset value
            ---------------------------------------------------
            Parameters
            -
        """
        # Read register data
        register_data = self.I2CRead(MPU6050_REG_ACCEL_YOFFS_H, 2)
        # Process raw data
        accel_y_offset = ((register_data[0] << 8) | register_data[1])
        # Return data
        return accel_y_offset

    def getAccelOffsetZ(self):
        """
            Method for getting accelerometer Z offset value
            ---------------------------------------------------
            Parameters
            -
        """
        # Read register data
        register_data = self.I2CRead(MPU6050_REG_ACCEL_ZOFFS_H, 2)
        # Process raw data
        accel_z_offset = ((register_data[0] << 8) | register_data[1])
        # Return data
        return accel_z_offset

    def setAccelOffsetX(self, high_offset, low_offset):
        """
            Method for setting accelerometer X offset value
            ---------------------------------------------------
            Parameters
            -
        """
        # Write first 8-bit (high bit) data to register
        self.I2CWrite(MPU6050_REG_ACCEL_XOFFS_H, high_offset)
        # Write second 8-bit (low bit) data to register
        self.I2CWrite(MPU6050_REG_ACCEL_XOFFS_H, low_offset)
    
    def setAccelOffsetY(self, high_offset, low_offset):
        """
            Method for setting accelerometer Y offset value
            ---------------------------------------------------
            Parameters
            -
        """
        # Write first 8-bit (high bit) data to register
        self.I2CWrite(MPU6050_REG_ACCEL_YOFFS_H, high_offset)
        # Write second 8-bit (low bit) data to register
        self.I2CWrite(MPU6050_REG_ACCEL_YOFFS_H, low_offset)
    
    def setAccelOffsetZ(self, high_offset, low_offset):
        """
            Method for setting accelerometer Z offset value
            ---------------------------------------------------
            Parameters
            -
        """
        # Write first 8-bit (high bit) data to register
        self.I2CWrite(MPU6050_REG_ACCEL_ZOFFS_H, high_offset)
        # Write second 8-bit (low bit) data to register
        self.I2CWrite(MPU6050_REG_ACCEL_ZOFFS_H, low_offset)

    def calibrateGyro(self, sample_num):
        """
            Method for calibrating gyroscope sensor
            ---------------------------------------------------
            Parameters
            sample_num: number of sample data
        """ 
        # Set calibrate value
        self.use_calibrate = True

        # Declare internal variables
        sum_x = 0.0
        sum_y = 0.0
        sum_z = 0.0
        sigma_x = 0.0
        sigma_y = 0.0
        sigma_z = 0.0

        # Read n-samples
        for i in range(sample_num):
            # Read raw gyro data
            self.getRawGyro()

            # Sum each sample data
            sum_x += self.raw_gyro["x_axis"]
            sum_y += self.raw_gyro["y_axis"]
            sum_z += self.raw_gyro["z_axis"]

            # Calculate sigma
            sigma_x += (self.raw_gyro["x_axis"] * self.raw_gyro["x_axis"])
            sigma_y += (self.raw_gyro["y_axis"] * self.raw_gyro["y_axis"])
            sigma_z += (self.raw_gyro["z_axis"] * self.raw_gyro["z_axis"])

            # Delay
            time.sleep(0.005)

        # Calculate delta vectors
        self.delta_gyro["x_axis"] = sum_x / sample_num
        self.delta_gyro["y_axis"] = sum_y / sample_num
        self.delta_gyro["z_axis"] = sum_z / sample_num
        
        # Calculate threshold vectors
        self.threshold_data["x_axis"] = math.sqrt((sigma_x / 50) - (self.delta_gyro["x_axis"] * self.delta_gyro["x_axis"]))
        self.threshold_data["y_axis"] = math.sqrt((sigma_y / 50) - (self.delta_gyro["y_axis"] * self.delta_gyro["y_axis"]))
        self.threshold_data["z_axis"] = math.sqrt((sigma_z / 50) - (self.delta_gyro["z_axis"] * self.delta_gyro["z_axis"]))

        # Set threshold value
        if (self.actual_threshold > 0):
            self.setThreshold(self.actual_threshold)

    def getThreshold(self):
        """
            Method for getting threshold value
            ---------------------------------------------------
            Parameters
            -
        """
        # Return data
        return self.actual_threshold

    def setThreshold(self, multiple):
        """
            Method for setting threshold value
            ---------------------------------------------------
            Parameters
            multiple
        """
        # Check multiple value
        if (multiple > 0):
            # Check calibration status
            if (not(self.use_calibrate)):
                self.calibrateGyro(100)
            
            # Calculate gyroscope threshold vectors
            self.threshold_gyro["x_axis"] = self.threshold_data["x_axis"] * multiple
            self.threshold_gyro["y_axis"] = self.threshold_data["y_axis"] * multiple
            self.threshold_gyro["z_axis"] = self.threshold_data["z_axis"] * multiple
        else:
            # No threshold value
            self.threshold_gyro["x_axis"] = 0
            self.threshold_gyro["y_axis"] = 0
            self.threshold_gyro["z_axis"] = 0
        
        # Store previous threshold value
        self.actual_threshold = multiple