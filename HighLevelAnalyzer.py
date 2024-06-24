from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting
import ctypes

class Hla(HighLevelAnalyzer):
    result_types = {
        'address': {
            'format': 'Address: {{data.address}}, {{data.read_write}}'
        },
        'register': {
            'format': 'Register: {{data.description}}'
        },
        'data': {
            'format': 'Data: {{data.value}}'
        }
    }

    def __init__(self):
        self.state = 'WAIT_ADDRESS'
        self.address = 0
        self.read_write = ''
        self.current_register = ''

        self.registers = {
            0x00: {'name': 'RA_XG_OFFS_TC', 'alias': 'XG OFFSET TC'},
            0x01: {'name': 'RA_YG_OFFS_TC', 'alias': 'YG OFFSET TC'},
            0x02: {'name': 'RA_ZG_OFFS_TC', 'alias': 'ZG OFFSET TC'},
            0x06: {'name': 'RA_XA_OFFS_H', 'alias':  'XA OFFSET'},
            0x08: {'name': 'RA_YG_OFFS_TC', 'alias': 'YA OFFSET'},           
            0x0A: {'name': 'RA_ZG_OFFS_TC', 'alias': 'ZA OFFSET'},
            0x13: {'name': 'RA_XG_OFFS',    'alias': 'XG OFFSET'},
            0x15: {'name': 'RA_YG_OFFS',    'alias': 'YG OFFSET'},
            0x17: {'name': 'RA_ZG_OFFS',    'alias': 'ZG OFFSET'},
            0x0D: {'name': 'SELF_TEST_X', 'alias': 'Self-Test Registers - X-axis'},
            0x0E: {'name': 'SELF_TEST_Y', 'alias': 'Self-Test Registers - Y-axis'},
            0x0F: {'name': 'SELF_TEST_Z', 'alias': 'Self-Test Registers - Z-axis'},
            0x10: {'name': 'SELF_TEST_A', 'alias': 'Self-Test Register - Accelerometer'},
            0x19: {'name': 'SMPLRT_DIV', 'alias': 'Sample Rate Divider'},
            0x1A: {'name': 'CONFIG', 'alias': 'Configuration', 'fields': {
                'EXT_SYNC_SET': {
                    0: 'Input Disabled',
                    1: 'TEMP_OUT_L[0]',
                    2: 'GYRO_XOUT_L[0]',
                    3: 'GYRO_YOUT_L[0]',
                    4: 'GYRO_ZOUT_L[0]',
                    5: 'ACCEL_XOUT_L[0]',
                    6: 'ACCEL_YOUT_L[0]',
                    7: 'ACCEL_ZOUT_L[0]'
                },
                'DLPF_CFG': {
                    0: '260 Hz',
                    1: '184 Hz',
                    2: '94 Hz',
                    3: '44 Hz',
                    4: '21 Hz',
                    5: '10 Hz',
                    6: '5 Hz',
                    7: 'Reserved'
                }
            }},
            0x1B: {'name': 'GYRO_CONFIG', 'alias': 'Gyroscope Configuration', 'fields': {
                'FS_SEL': {
                    0: '±250 °/s',
                    1: '±500 °/s',
                    2: '±1000 °/s',
                    3: '±2000 °/s'
                }
            }},
            0x1C: {'name': 'ACCEL_CONFIG', 'alias': 'Accelerometer Configuration', 'fields': {
                'AFS_SEL': {
                    0: '±2g',
                    1: '±4g',
                    2: '±8g',
                    3: '±16g'
                }
            }},
            0x23: {'name': 'FIFO_EN', 'alias': 'FIFO Enable'},
            0x24: {'name': 'I2C_MST_CTRL', 'alias': 'I2C Master Control', 'fields': {
                'I2C_MST_CLK': {
                    0: '348 kHz',
                    1: '333 kHz',
                    2: '320 kHz',
                    3: '308 kHz',
                    4: '296 kHz',
                    5: '286 kHz',
                    6: '276 kHz',
                    7: '267 kHz',
                    8: '258 kHz',
                    9: '500 kHz',
                    10: '471 kHz',
                    11: '444 kHz',
                    12: '421 kHz',
                    13: '400 kHz',
                    14: '381 kHz',
                    15: '364 kHz'
                }
            }},
            0x25: {'name': 'I2C_SLV0_ADDR', 'alias': 'I2C Slave 0 Address'},
            0x26: {'name': 'I2C_SLV0_REG', 'alias': 'I2C Slave 0 Register'},
            0x27: {'name': 'I2C_SLV0_CTRL', 'alias': 'I2C Slave 0 Control'},
            0x28: {'name': 'I2C_SLV1_ADDR', 'alias': 'I2C Slave 1 Address'},
            0x29: {'name': 'I2C_SLV1_REG', 'alias': 'I2C Slave 1 Register'},
            0x2A: {'name': 'I2C_SLV1_CTRL', 'alias': 'I2C Slave 1 Control'},
            0x2B: {'name': 'I2C_SLV2_ADDR', 'alias': 'I2C Slave 2 Address'},
            0x2C: {'name': 'I2C_SLV2_REG', 'alias': 'I2C Slave 2 Register'},
            0x2D: {'name': 'I2C_SLV2_CTRL', 'alias': 'I2C Slave 2 Control'},
            0x2E: {'name': 'I2C_SLV3_ADDR', 'alias': 'I2C Slave 3 Address'},
            0x2F: {'name': 'I2C_SLV3_REG', 'alias': 'I2C Slave 3 Register'},
            0x30: {'name': 'I2C_SLV3_CTRL', 'alias': 'I2C Slave 3 Control'},
            0x31: {'name': 'I2C_SLV4_ADDR', 'alias': 'I2C Slave 4 Address'},
            0x32: {'name': 'I2C_SLV4_REG', 'alias': 'I2C Slave 4 Register'},
            0x33: {'name': 'I2C_SLV4_DO', 'alias': 'I2C Slave 4 Data Out'},
            0x34: {'name': 'I2C_SLV4_CTRL', 'alias': 'I2C Slave 4 Control'},
            0x35: {'name': 'I2C_SLV4_DI', 'alias': 'I2C Slave 4 Data In'},
            0x36: {'name': 'I2C_MST_STATUS', 'alias': 'I2C Master Status'},
            0x37: {'name': 'INT_PIN_CFG', 'alias': 'INT Pin / Bypass Enable Configuration'},
            0x38: {'name': 'INT_ENABLE', 'alias': 'Interrupt Enable'},
            0x3A: {'name': 'INT_STATUS', 'alias': 'Interrupt Status'},
            0x3B: {'name': 'ACCEL_XOUT_H', 'alias': 'Accelerometer and Gyroscope Measurements'},
            0x3C: {'name': 'ACCEL_XOUT_L', 'alias': 'Accelerometer Measurements - X-axis (Low Byte)'},
            0x3D: {'name': 'ACCEL_YOUT_H', 'alias': 'Accelerometer Measurements - Y-axis (High Byte)'},
            0x3E: {'name': 'ACCEL_YOUT_L', 'alias': 'Accelerometer Measurements - Y-axis (Low Byte)'},
            0x3F: {'name': 'ACCEL_ZOUT_H', 'alias': 'Accelerometer Measurements - Z-axis (High Byte)'},
            0x40: {'name': 'ACCEL_ZOUT_L', 'alias': 'Accelerometer Measurements - Z-axis (Low Byte)'},
            0x41: {'name': 'TEMP_OUT_H', 'alias': 'Temperature Measurement (High Byte)'},
            0x42: {'name': 'TEMP_OUT_L', 'alias': 'Temperature Measurement (Low Byte)'},
            0x43: {'name': 'GYRO_XOUT_H', 'alias': 'Gyroscope Measurements - X-axis (High Byte)'},
            0x44: {'name': 'GYRO_XOUT_L', 'alias': 'Gyroscope Measurements - X-axis (Low Byte)'},
            0x45: {'name': 'GYRO_YOUT_H', 'alias': 'Gyroscope Measurements - Y-axis (High Byte)'},
            0x46: {'name': 'GYRO_YOUT_L', 'alias': 'Gyroscope Measurements - Y-axis (Low Byte)'},
            0x47: {'name': 'GYRO_ZOUT_H', 'alias': 'Gyroscope Measurements - Z-axis (High Byte)'},
            0x48: {'name': 'GYRO_ZOUT_L', 'alias': 'Gyroscope Measurements - Z-axis (Low Byte)'},
            0x49: {'name': 'EXT_SENS_DATA_00', 'alias': 'External Sensor Data 00'},
            0x4A: {'name': 'EXT_SENS_DATA_01', 'alias': 'External Sensor Data 01'},
            0x4B: {'name': 'EXT_SENS_DATA_02', 'alias': 'External Sensor Data 02'},
            0x4C: {'name': 'EXT_SENS_DATA_03', 'alias': 'External Sensor Data 03'},
            0x4D: {'name': 'EXT_SENS_DATA_04', 'alias': 'External Sensor Data 04'},
            0x4E: {'name': 'EXT_SENS_DATA_05', 'alias': 'External Sensor Data 05'},
            0x4F: {'name': 'EXT_SENS_DATA_06', 'alias': 'External Sensor Data 06'},
            0x50: {'name': 'EXT_SENS_DATA_07', 'alias': 'External Sensor Data 07'},
            0x51: {'name': 'EXT_SENS_DATA_08', 'alias': 'External Sensor Data 08'},
            0x52: {'name': 'EXT_SENS_DATA_09', 'alias': 'External Sensor Data 09'},
            0x53: {'name': 'EXT_SENS_DATA_10', 'alias': 'External Sensor Data 10'},
            0x54: {'name': 'EXT_SENS_DATA_11', 'alias': 'External Sensor Data 11'},
            0x55: {'name': 'EXT_SENS_DATA_12', 'alias': 'External Sensor Data 12'},
            0x56: {'name': 'EXT_SENS_DATA_13', 'alias': 'External Sensor Data 13'},
            0x57: {'name': 'EXT_SENS_DATA_14', 'alias': 'External Sensor Data 14'},
            0x58: {'name': 'EXT_SENS_DATA_15', 'alias': 'External Sensor Data 15'},
            0x59: {'name': 'EXT_SENS_DATA_16', 'alias': 'External Sensor Data 16'},
            0x5A: {'name': 'EXT_SENS_DATA_17', 'alias': 'External Sensor Data 17'},
            0x5B: {'name': 'EXT_SENS_DATA_18', 'alias': 'External Sensor Data 18'},
            0x5C: {'name': 'EXT_SENS_DATA_19', 'alias': 'External Sensor Data 19'},
            0x5D: {'name': 'EXT_SENS_DATA_20', 'alias': 'External Sensor Data 20'},
            0x5E: {'name': 'EXT_SENS_DATA_21', 'alias': 'External Sensor Data 21'},
            0x5F: {'name': 'EXT_SENS_DATA_22', 'alias': 'External Sensor Data 22'},
            0x60: {'name': 'EXT_SENS_DATA_23', 'alias': 'External Sensor Data 23'},
            0x63: {'name': 'I2C_SLV0_DO', 'alias': 'I2C Slave 0 Data Out'},
            0x64: {'name': 'I2C_SLV1_DO', 'alias': 'I2C Slave 1 Data Out'},
            0x65: {'name': 'I2C_SLV2_DO', 'alias': 'I2C Slave 2 Data Out'},
            0x66: {'name': 'I2C_SLV3_DO', 'alias': 'I2C Slave 3 Data Out'},
            0x67: {'name': 'I2C_MST_DELAY_CTRL', 'alias': 'I2C Master Delay Control'},
            0x68: {'name': 'SIGNAL_PATH_RESET', 'alias': 'Signal Path Reset'},
            0x6A: {'name': 'USER_CTRL', 'alias': 'User Control'},
            0x6B: {'name': 'PWR_MGMT_1', 'alias': 'Power Management 1', 'fields': {
                'CLKSEL': {
                    0: 'Internal 8MHz oscillator',
                    1: 'PLL with X axis gyroscope reference',
                    2: 'PLL with Y axis gyroscope reference',
                    3: 'PLL with Z axis gyroscope reference',
                    4: 'PLL with external 32.768kHz reference',
                    5: 'PLL with external 19.2MHz reference',
                    6: 'Reserved',
                    7: 'Stops the clock and keeps the timing generator in reset'
                }
            }},
            0x6C: {'name': 'PWR_MGMT_2', 'alias': 'Power Management 2', 'fields': {
                'LP_WAKE_CTRL': {
                    0: '1.25 Hz',
                    1: '5 Hz',
                    2: '20 Hz',
                    3: '40 Hz'
                }
            }},
            0x6D: {'name': 'RA_BANK_SEL', 'alias': 'Memory Bank Select'},
            0x6E: {'name': 'RA_MEM_START_ADDR', 'alias': 'Memory Bank Start Address'},
            0x6F: {'name': 'RA_MEM_R_W', 'alias': 'Memory Bank Read/Write'},
            0x70: {'name': 'RA_DMP_CFG_1', 'alias': 'DMP Configuration 1'},
            0x71: {'name': 'RA_DMP_CFG_2', 'alias': 'DMP Configuration 2'},
            0x72: {'name': 'FIFO_COUNTH', 'alias': 'FIFO Count Registers (High Byte)'},
            0x73: {'name': 'FIFO_COUNTL', 'alias': 'FIFO Count Registers (Low Byte)'},
            0x74: {'name': 'FIFO_R_W', 'alias': 'FIFO Read Write'},
            0x75: {'name': 'WHO_AM_I', 'alias': 'Who Am I'}
        }

    def decode(self, frame: AnalyzerFrame):
        if frame.type == 'address':
            self.address = frame.data['address'][0]
            self.read_write = 'Read' if frame.data['read'] else 'Write'
            self.state = 'WAIT_REGISTER' if self.read_write == 'Write' else 'WAIT_DATA'
            self.burst_data = []
            self.id = ''
            return AnalyzerFrame('address', frame.start_time, frame.end_time, {
                'address': hex(self.address),
                'read_write': self.read_write
            })

        elif frame.type == 'data':
            data = frame.data['data'][0]

            if self.state == 'WAIT_REGISTER':
                if data in self.registers:
                    self.current_register = self.registers[data]['alias']
                    self.id = data
                    self.state = 'WAIT_DATA'
                    return AnalyzerFrame('register', frame.start_time, frame.end_time, {
                        'description': self.current_register
                    })
                else:
                    return AnalyzerFrame('data_write', frame.start_time, frame.end_time, {
                        'register': 'Unknown',
                        'value': hex(data),
                        'description': 'Unknown register'
                    })

            elif self.state == 'WAIT_DATA':
                self.burst_data.append(data)

        elif frame.type == 'stop':
            if self.state == 'WAIT_DATA':
                if len(self.burst_data) == 0:
                       return
                data = self.burst_data[0]
                description = ''
                print(self.read_write, "to Address:", hex(self.address))
                if self.read_write == 'Write':
                    #for i, data in enumerate(self.burst_data):
                    description += self.get_description(self.current_register, self.burst_data, self.id, len(self.burst_data))
                    print(f"\t {description}")
                    print("\n")
                    self.state = 'WAIT_ADDRESS'
                    self.burst_data = []
                    return AnalyzerFrame('data_write', frame.start_time, frame.end_time, {
                        'register': self.current_register,
                        'value': hex(data),
                        'description': description
                    })
                else:
                    #for i, data in enumerate(self.burst_data):
                    description += self.get_description(self.current_register, self.burst_data, self.id, len(self.burst_data))
                    
                    print(f"\t {description}")
                    print("\n")
                    self.state = 'WAIT_ADDRESS'
                    self.burst_data = []
                    return AnalyzerFrame('data_read', frame.start_time, frame.end_time, {
                        'register': self.current_register,
                        'value': hex(data),
                        'description': description
                    })

    def get_description(self, register, data, reg_id, dataSize):

        description = f'Register: {register} \n\t Data:'
        
        for i, hexData in enumerate(data):
            if i == dataSize - 1:
                description += f'{hex(hexData)}\n'
            else:
                description += f'{hex(hexData)}, '

        if register == 'Self-Test Registers - X-axis':
            xa_test = data[0] & 0x1F
            description += f'\t XA_TEST[4:0]: {xa_test}, XG_TEST[4:0]: {data[0] >> 5}\n'
        elif register == 'Self-Test Registers - Y-axis':
            ya_test = data[0] & 0x1F
            description += f'\t YA_TEST[4:0]: {ya_test}, YG_TEST[4:0]: {data[0] >> 5}\n'
        elif register == 'XG OFFSET':
            XG_OFFSET= ((data[0] << 8) | data[1])
            description += f'\t OFFSET: {ctypes.c_int16(XG_OFFSET).value}\n'
        elif register == 'YG OFFSET':
            YG_OFFSET= ((data[0] << 8) | data[1])
            description += f'\t OFFSET: {ctypes.c_int16(YG_OFFSET).value}\n'
        elif register == 'ZG OFFSET':
            ZG_OFFSET= ((data[0] << 8) | data[1])
            description += f'\t OFFSET: {ctypes.c_int16(ZG_OFFSET).value}\n'
        elif register == 'XA OFFSET':
            XA_OFFSET=  ((data[0] << 8) | data[1])
            description += f'\t OFFSET: {ctypes.c_int16(XA_OFFSET).value}\n'
        elif register == 'YA OFFSET':
            YA_OFFSET=  ((data[0] << 8) | data[1])
            description += f'\t OFFSET: {ctypes.c_int16(YA_OFFSET).value}\n'
        elif register == 'ZA OFFSET':
            ZA_OFFSET=  ((data[0] << 8) | data[1])
            description += f'\t OFFSET: {ctypes.c_int16(ZA_OFFSET).value}\n'
        elif register == 'Self-Test Registers - Z-axis':
            za_test = data[0] & 0x1F
            description += f'\t ZA_TEST[4:0]: {za_test}, ZG_TEST[4:0]: {data[0] >> 5}\n'
        elif register == 'Self-Test Register - Accelerometer':
            description += f'\t XA_TEST[1:0]: {data[0] & 0x03}, YA_TEST[1:0]: {(data[0] >> 2) & 0x03}, ZA_TEST[1:0]: {(data[0] >> 4) & 0x03}\n'
        elif register == 'Sample Rate Divider':
            description += f'\t Sample Rate Divider: {data[0]}\n'
        elif register == 'Configuration':
            ext_sync_set = (data[0] >> 3) & 0x07
            dlpf_cfg = data[0] & 0x07
            description += f"\t EXT_SYNC_SET: {ext_sync_set} [{self.registers[reg_id]['fields']['EXT_SYNC_SET'][ext_sync_set]}], "
            description += f"DLPF_CFG: {dlpf_cfg} [{self.registers[reg_id]['fields']['DLPF_CFG'][dlpf_cfg]}]\n"
        elif register == 'Gyroscope Configuration':
            xg_st = (data[0] >> 7) & 0x01
            yg_st = (data[0] >> 6) & 0x01
            zg_st = (data[0] >> 5) & 0x01
            fs_sel = (data[0] >> 3) & 0x03
            description += f"\t XG_ST: {xg_st}, YG_ST: {yg_st}, ZG_ST: {zg_st}, FS_SEL: {fs_sel} [{self.registers[reg_id]['fields']['FS_SEL'][fs_sel]}]\n"
        elif register == 'Accelerometer Configuration':
            xa_st = (data[0] >> 7) & 0x01
            ya_st = (data[0] >> 6) & 0x01
            za_st = (data[0] >> 5) & 0x01
            afs_sel = (data[0] >> 3) & 0x03
            description += f"\t XA_ST: {xa_st}, YA_ST: {ya_st}, ZA_ST: {za_st}, AFS_SEL: {afs_sel} [{self.registers[reg_id]['fields']['AFS_SEL'][afs_sel]}]\n"
        elif register == 'FIFO Enable':
            temp_fifo_en = (data[0] >> 7) & 0x01
            xg_fifo_en = (data[0] >> 6) & 0x01
            yg_fifo_en = (data[0] >> 5) & 0x01
            zg_fifo_en = (data[0] >> 4) & 0x01
            accel_fifo_en = (data[0] >> 3) & 0x01
            slv2_fifo_en = (data[0] >> 2) & 0x01
            slv1_fifo_en = (data[0] >> 1) & 0x01
            slv0_fifo_en = data[0] & 0x01
            description += f'\t TEMP_FIFO_EN: {temp_fifo_en}, XG_FIFO_EN: {xg_fifo_en}, YG_FIFO_EN: {yg_fifo_en}, ZG_FIFO_EN: {zg_fifo_en}, '
            description += f'ACCEL_FIFO_EN: {accel_fifo_en}, SLV2_FIFO_EN: {slv2_fifo_en}, SLV1_FIFO_EN: {slv1_fifo_en}, SLV0_FIFO_EN: {slv0_fifo_en}\n'
        elif register == 'I2C Master Control':
            mult_mst_en = (data[0] >> 7) & 0x01
            wait_for_es = (data[0] >> 6) & 0x01
            slv_3_fifo_en = (data[0] >> 5) & 0x01
            i2c_mst_p_nsr = (data[0] >> 4) & 0x01
            i2c_mst_clk = data[0] & 0x0F
            description += f"\t MULT_MST_EN: {mult_mst_en}, WAIT_FOR_ES: {wait_for_es}, SLV_3_FIFO_EN: {slv_3_fifo_en}, I2C_MST_P_NSR: {i2c_mst_p_nsr}, "
            description += f"I2C_MST_CLK: {i2c_mst_clk} [{self.registers[reg_id]['fields']['I2C_MST_CLK'][i2c_mst_clk]}]\n"
        elif register == 'I2C Slave 0 Address':
            i2c_slv0_rw = (data[0] >> 7) & 0x01
            i2c_slv0_addr = data[0] & 0x7F
            description += f'\t I2C_SLV0_RW: {i2c_slv0_rw}, I2C_SLV0_ADDR: {i2c_slv0_addr}\n'
        elif register == 'I2C Slave 0 Register':
            description += f'\t I2C_SLV0_REG: {data[0]}\n'
        elif register == 'I2C Slave 0 Control':
            i2c_slv0_en = (data[0] >> 7) & 0x01
            i2c_slv0_byte_sw = (data[0] >> 6) & 0x01
            i2c_slv0_reg_dis = (data[0] >> 5) & 0x01
            i2c_slv0_grp = (data[0] >> 4) & 0x01
            i2c_slv0_len = data[0] & 0x0F
            description += f'\t I2C_SLV0_EN: {i2c_slv0_en}, I2C_SLV0_BYTE_SW: {i2c_slv0_byte_sw}, I2C_SLV0_REG_DIS: {i2c_slv0_reg_dis}, '
            description += f'I2C_SLV0_GRP: {i2c_slv0_grp}, I2C_SLV0_LEN: {i2c_slv0_len}\n'
        elif register == 'I2C Slave 1 Address':
            i2c_slv1_rw = (data[0] >> 7) & 0x01
            i2c_slv1_addr = data[0] & 0x7F
            description += f'\t I2C_SLV1_RW: {i2c_slv1_rw}, I2C_SLV1_ADDR: {i2c_slv1_addr}\n'
        elif register == 'I2C Slave 1 Register':
            description += f'\t I2C_SLV1_REG: {data[0]}\n'
        elif register == 'I2C Slave 1 Control':
            i2c_slv1_en = (data[0] >> 7) & 0x01
            i2c_slv1_byte_sw = (data[0] >> 6) & 0x01
            i2c_slv1_reg_dis = (data[0] >> 5) & 0x01
            i2c_slv1_grp = (data[0] >> 4) & 0x01
            i2c_slv1_len = data[0] & 0x0F
            description += f'\t I2C_SLV1_EN: {i2c_slv1_en}, I2C_SLV1_BYTE_SW: {i2c_slv1_byte_sw}, I2C_SLV1_REG_DIS: {i2c_slv1_reg_dis}, '
            description += f'I2C_SLV1_GRP: {i2c_slv1_grp}, I2C_SLV1_LEN: {i2c_slv1_len}\n'
        elif register == 'I2C Slave 2 Address':
            i2c_slv2_rw = (data[0] >> 7) & 0x01
            i2c_slv2_addr = data[0] & 0x7F
            description += f'\t I2C_SLV2_RW: {i2c_slv2_rw}, I2C_SLV2_ADDR: {i2c_slv2_addr}\n'
        elif register == 'I2C Slave 2 Register':
            description += f'\t I2C_SLV2_REG: {data[0]}\n'
        elif register == 'I2C Slave 2 Control':
            i2c_slv2_en = (data[0] >> 7) & 0x01
            i2c_slv2_byte_sw = (data[0] >> 6) & 0x01
            i2c_slv2_reg_dis = (data[0] >> 5) & 0x01
            i2c_slv2_grp = (data[0] >> 4) & 0x01
            i2c_slv2_len = data[0] & 0x0F
            description += f'\t I2C_SLV2_EN: {i2c_slv2_en}, I2C_SLV2_BYTE_SW: {i2c_slv2_byte_sw}, I2C_SLV2_REG_DIS: {i2c_slv2_reg_dis}, '
            description += f'I2C_SLV2_GRP: {i2c_slv2_grp}, I2C_SLV2_LEN: {i2c_slv2_len}\n'
        elif register == 'I2C Slave 3 Address':
            i2c_slv3_rw = (data[0] >> 7) & 0x01
            i2c_slv3_addr = data[0] & 0x7F
            description += f'\t I2C_SLV3_RW: {i2c_slv3_rw}, I2C_SLV3_ADDR: {i2c_slv3_addr}\n'
        elif register == 'I2C Slave 3 Register':
            description += f'\t I2C_SLV3_REG: {data[0]}\n'
        elif register == 'I2C Slave 3 Control':
            i2c_slv3_en = (data[0] >> 7) & 0x01
            i2c_slv3_byte_sw = (data[0] >> 6) & 0x01
            i2c_slv3_reg_dis = (data[0] >> 5) & 0x01
            i2c_slv3_grp = (data[0] >> 4) & 0x01
            i2c_slv3_len = data[0] & 0x0F
            description += f'\t I2C_SLV3_EN: {i2c_slv3_en}, I2C_SLV3_BYTE_SW: {i2c_slv3_byte_sw}, I2C_SLV3_REG_DIS: {i2c_slv3_reg_dis}, '
            description += f'I2C_SLV3_GRP: {i2c_slv3_grp}, I2C_SLV3_LEN: {i2c_slv3_len}\n'
        elif register == 'I2C Slave 4 Address':
            i2c_slv4_rw = (data[0] >> 7) & 0x01
            i2c_slv4_addr = data[0] & 0x7F
            description += f'\t I2C_SLV4_RW: {i2c_slv4_rw}, I2C_SLV4_ADDR: {i2c_slv4_addr}\n'
        elif register == 'I2C Slave 4 Register':
            description += f'\t I2C_SLV4_REG: {data[0]}\n'
        elif register == 'I2C Slave 4 Data Out':
            description += f'\t I2C_SLV4_DO: {data[0]}\n'
        elif register == 'I2C Slave 4 Control':
            i2c_slv4_en = (data[0] >> 7) & 0x01
            i2c_slv4_int_en = (data[0] >> 6) & 0x01
            i2c_slv4_reg_dis = (data[0] >> 5) & 0x01
            i2c_mst_dly = data[0] & 0x1F
            description += f'\t I2C_SLV4_EN: {i2c_slv4_en}, I2C_SLV4_INT_EN: {i2c_slv4_int_en}, I2C_SLV4_REG_DIS: {i2c_slv4_reg_dis}, '
            description += f'I2C_MST_DLY: {i2c_mst_dly}\n'
        elif register == 'I2C Slave 4 Data In':
            description += f'\t I2C_SLV4_DI: {data[0]}\n'
        elif register == 'I2C Master Status':
            pass_through = (data[0] >> 7) & 0x01
            i2c_slv4_done = (data[0] >> 6) & 0x01
            i2c_lost_arb = (data[0] >> 5) & 0x01
            i2c_slv4_nack = (data[0] >> 4) & 0x01
            i2c_slv3_nack = (data[0] >> 3) & 0x01
            i2c_slv2_nack = (data[0] >> 2) & 0x01
            i2c_slv1_nack = (data[0] >> 1) & 0x01
            i2c_slv0_nack = data[0] & 0x01
            description += f'\t PASS_THROUGH: {pass_through}, I2C_SLV4_DONE: {i2c_slv4_done}, I2C_LOST_ARB: {i2c_lost_arb}, '
            description += f'I2C_SLV4_NACK: {i2c_slv4_nack}, I2C_SLV3_NACK: {i2c_slv3_nack}, I2C_SLV2_NACK: {i2c_slv2_nack}, '
            description += f'I2C_SLV1_NACK: {i2c_slv1_nack}, I2C_SLV0_NACK: {i2c_slv0_nack}\n'
        elif register == 'INT Pin / Bypass Enable Configuration':
            int_level = (data[0] >> 7) & 0x01
            int_open = (data[0] >> 6) & 0x01
            latch_int_en = (data[0] >> 5) & 0x01
            int_rd_clear = (data[0] >> 4) & 0x01
            fsync_int_level = (data[0] >> 3) & 0x01
            fsync_int_en = (data[0] >> 2) & 0x01
            i2c_bypass_en = (data[0] >> 1) & 0x01
            description += f'\t INT_LEVEL: {int_level}, INT_OPEN: {int_open}, LATCH_INT_EN: {latch_int_en}, INT_RD_CLEAR: {int_rd_clear}, '
            description += f'FSYNC_INT_LEVEL: {fsync_int_level}, FSYNC_INT_EN: {fsync_int_en}, I2C_BYPASS_EN: {i2c_bypass_en}\n'
        elif register == 'Interrupt Enable':
            fifo_oflow_en = (data[0] >> 4) & 0x01
            i2c_mst_int_en = (data[0] >> 3) & 0x01
            data_rdy_en = data[0] & 0x01
            description += f'\t FIFO_OFLOW_EN: {fifo_oflow_en}, I2C_MST_INT_EN: {i2c_mst_int_en}, DATA_RDY_EN: {data_rdy_en}\n'
        elif register == 'Interrupt Status':
            fifo_oflow_int = (data[0] >> 4) & 0x01
            i2c_mst_int = (data[0] >> 3) & 0x01
            data_rdy_int = data[0] & 0x01
            description += f'\t FIFO_OFLOW_INT: {fifo_oflow_int}, I2C_MST_INT: {i2c_mst_int}, DATA_RDY_INT: {data_rdy_int}\n'
        elif register.startswith('Accelerometer and Gyroscope'):
            
            description += f"\t Ax: {ctypes.c_int16(((data[0] << 8) | (data[1]))).value}\n"
            description += f"\t Ay: {ctypes.c_int16(((data[2] << 8) | (data[3]))).value}\n"
            description += f"\t Az: {ctypes.c_int16(((data[4] << 8) | (data[5]))).value}\n"
            description += f"\t Gx: {ctypes.c_int16(((data[8] << 8) | (data[9]))).value}\n"
            description += f"\t Gy: {ctypes.c_int16(((data[10] << 8) | (data[11]))).value}\n"
            description += f"\t Gz: {ctypes.c_int16(((data[12] << 8) | (data[13]))).value}\n"

        elif register.startswith('Temperature Measurement'):
            description += f'\t Temperature Data: {data[0]}\n'
        elif register.startswith('Gyroscope Measurements - '):
            description += f'\t Gyroscope {register[-10:-8]} Axis Data: {data[0]}\n'
        elif register.startswith('External Sensor Data '):
            description += f'\t External Sensor Data: {data[0]}\n'
        elif register.startswith('I2C Slave ') and register.endswith(' Data Out'):
            description += f'\t I2C Slave Data Out: {data[0]}\n'
        elif register == 'I2C Master Delay Control':
            delay_es_shadow = (data[0] >> 7) & 0x01
            i2c_slv4_dly_en = (data[0] >> 4) & 0x01
            i2c_slv3_dly_en = (data[0] >> 3) & 0x01
            i2c_slv2_dly_en = (data[0] >> 2) & 0x01
            i2c_slv1_dly_en = (data[0] >> 1) & 0x01
            i2c_slv0_dly_en = data[0] & 0x01
            description += f'\t DELAY_ES_SHADOW: {delay_es_shadow}, I2C_SLV4_DLY_EN: {i2c_slv4_dly_en}, I2C_SLV3_DLY_EN: {i2c_slv3_dly_en}, '
            description += f'I2C_SLV2_DLY_EN: {i2c_slv2_dly_en}, I2C_SLV1_DLY_EN: {i2c_slv1_dly_en}, I2C_SLV0_DLY_EN: {i2c_slv0_dly_en}\n'
        elif register == 'Signal Path Reset':
            gyro_reset = (data[0] >> 2) & 0x01
            accel_reset = (data[0] >> 1) & 0x01
            temp_reset = data[0] & 0x01
            description += f'\t GYRO_RESET: {gyro_reset}, ACCEL_RESET: {accel_reset}, TEMP_RESET: {temp_reset}\n'
        elif register == 'User Control':
            fifo_en = (data[0] >> 6) & 0x01
            i2c_mst_en = (data[0] >> 5) & 0x01
            i2c_if_dis = (data[0] >> 4) & 0x01
            fifo_reset = (data[0] >> 2) & 0x01
            i2c_mst_reset = (data[0] >> 1) & 0x01
            sig_cond_reset = data[0] & 0x01
            description += f'\t FIFO_EN: {fifo_en}, I2C_MST_EN: {i2c_mst_en}, I2C_IF_DIS: {i2c_if_dis}, FIFO_RESET: {fifo_reset}, '
            description += f'I2C_MST_RESET: {i2c_mst_reset}, SIG_COND_RESET: {sig_cond_reset}\n'
        elif register == 'Power Management 1':
            device_reset = (data[0] >> 7) & 0x01
            sleep = (data[0] >> 6) & 0x01
            cycle = (data[0] >> 5) & 0x01
            temp_dis = (data[0] >> 3) & 0x01
            clksel = data[0] & 0x07
            description += f"\t DEVICE_RESET: {device_reset}, SLEEP: {sleep}, CYCLE: {cycle}, TEMP_DIS: {temp_dis}, "
            description += f"CLKSEL: {clksel} [{self.registers[reg_id]['fields']['CLKSEL'][clksel]}]\n"
        elif register == 'Power Management 2':
            lp_wake_ctrl = (data[0] >> 6) & 0x03
            stby_xa = (data[0] >> 5) & 0x01
            stby_ya = (data[0] >> 4) & 0x01
            stby_za = (data[0] >> 3) & 0x01
            stby_xg = (data[0] >> 2) & 0x01
            stby_yg = (data[0] >> 1) & 0x01
            stby_zg = data[0] & 0x01
            description += f"\t LP_WAKE_CTRL: {lp_wake_ctrl} [{self.registers[reg_id]['fields']['LP_WAKE_CTRL'][lp_wake_ctrl]}], "
            description += f'STBY_XA: {stby_xa}, STBY_YA: {stby_ya}, STBY_ZA: {stby_za}, '
            description += f'STBY_XG: {stby_xg}, STBY_YG: {stby_yg}, STBY_ZG: {stby_zg}\n'
        elif register.startswith('FIFO Count Registers'):
            description += f'\t FIFO Count: {data[0]}\n'
        elif register == 'FIFO Read Write':
            description += f'\t FIFO_DATA: {data[0]}\n'
        elif register == 'Who Am I':
            description += f'\t Device ID: {hex(data[0])}\n'

        return description.strip()  # Remove the trailing newline character