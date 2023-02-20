import time
import serial
import struct

from ctypes import c_short

# print_CMD = False
print_CMD = True

CMD_MAX_LENGTH = 15


class iPort:

    START_BYTE_SEND = 0xAB
    START_BYTE_RECEIVE = 0xCD

    CMD_DIGITAL_WRITE = 0x01
    GPIO_PIN_ACTIVE_BUZZER = 11
    GPIO_PIN_RELAY = 12

    CMD_DIGITAL_READ = 0x02
    GPIO_PIN_JOYSTICK_SW = 21
    GPIO_PIN_LINE_FOLLOWER = 22
    GPIO_PIN_PHOTO_INTERRUPT = 23
    GPIO_PIN_LIMIT_SWITCH = 24
    GPIO_PIN_VIBRATION = 25
    GPIO_PIN_TOUCH = 26
    GPIO_PIN_TILT_SWITCH = 27
    GPIO_PIN_BUTTON = 28

    CMD_ANALOG_READ = 0x04
    ADC_PIN_JOYSTICK_X = 41
    ADC_PIN_JOYSTICK_Y = 42
    ADC_PIN_WATER_LEVEL = 43
    ADC_PIN_FLAME = 44
    ADC_PIN_HALL_EFFECT = 45
    ADC_PIN_SOIL_HUMIDTY = 46
    ADC_PIN_ANALOG_TEMP = 47
    ADC_PIN_MIC = 48
    ADC_PIN_PHOTORESISTOR = 49
    ADC_PIN_POTENTIOMETER = 10
    ADC_PIN_HEART_RATE = 11

    CMD_SERVO = 0x05
    SERVO_ANGLE = 0x50
    SERVO_TARGET_US = 0x051

    CMD_SEVEN_SEGMENT = 0x06
    SEVEN_SEG_CLEAR = 0x60
    SEVEN_SEG_SET_DEC_NUM = 0x61
    SEVEN_SEG_SET_BRIGHTNESS = 0x62
    SEVEN_SEG_ALL_ON = 0x63
    SEVEN_SEG_SET_SIGNED_NUM = 0x64

    CMD_DHT11 = 0x07
    DHT11_UPDATE = 0x70
    DHT11_TEMPERATURE = 0x71
    DHT11_HUMIDITY = 0x72

    CMD_DS18B20 = 0x08
    DS18B20_UPDATE = 0x80
    DS18B20_TEMPERATURE = 0x81

    CMD_PCA9635 = 0x09
    PCA9635_SET_RGB = 0x90
    PCA9635_SET_PWM = 0x91
    PCA9635_LED_SMD_1 = 0x01
    PCA9635_LED_SMD_2 = 0x02
    PCA9635_LED_1 = 0x03
    PCA9635_LED_2 = 0x04
    PCA9635_LED_SMD_1_R = 0
    PCA9635_LED_SMD_1_G = 1
    PCA9635_LED_SMD_1_B = 2
    PCA9635_LED_SMD_2_R = 3
    PCA9635_LED_SMD_2_G = 4
    PCA9635_LED_SMD_2_B = 5
    PCA9635_LED_THT_1_R = 6
    PCA9635_LED_THT_1_G = 7
    PCA9635_LED_THT_1_B = 8
    PCA9635_LED_THT_2_R = 9
    PCA9635_LED_THT_2_G = 10
    PCA9635_LED_THT_2_B = 11
    PCA9635_COLOR_LED_1 = 12
    PCA9635_COLOR_LED_2 = 13
    PCA9635_LASER_1 = 14
    PCA9635_LASER_2 = 15

    CMD_BUZZER = 0x0A
    BUZZER_SET_HZ = 0xA0,

    CMD_ROTARY_ENCODER = 0x0B
    ROTARY_ENCODER_GET_COUNT = 0xB0
    ROTARY_ENCODER_GET_SW = 0xB1

    CMD_E_PLATFORM = 0x0C
    E_PLATFORM_GET_ALL_DIGITAL_SENSOR = 0xC0
    E_PLATFORM_GET_ALL_ANALOG_SENSOR = 0xC1
    E_PLATFORM_GET_ALL_SENSOR = 0xC2

    CMD_ULTRASONIC = 0x0D
    ULTRASONIC_UPDATE = 0xD0
    ULTRASONIC_GET_DISTANCE = 0xD1

    REC_LEN_0_BYTE = 4
    REC_LEN_1_BYTE = 5
    REC_LEN_2_BYTE = 6
    REC_LEN_4_BYTE = 8

    def __init__(self, com):
        self.__com = com
        self.__mcu = serial.Serial(port=self.__com,
                                   baudrate=1000000,
                                   timeout=0.2)

    def __standard_array_len(self, array):
        for _ in range(CMD_MAX_LENGTH - len(array)):
            array.append(0)
        return array

    def __xor_checksum(self, array):
        checksum = array[0]
        for i in range(1, len(array)):
            checksum ^= array[i]
        return checksum

    def __send_cmd(self, cmd, function_name):
        checksum = self.__xor_checksum(cmd)
        cmd.append(checksum)
        cmd = self.__standard_array_len(cmd)
        if print_CMD:
            print(function_name)
            print('->', [hex(i) for i in cmd])
        self.__mcu.write(bytearray(cmd))
        return checksum

    def __receive_0_byte(self, checksum, error_code):
        rec_cmd_len = self.REC_LEN_0_BYTE
        rec_cmd_array = self.__mcu.read(rec_cmd_len)
        if print_CMD:
            print('<-', [hex(i) for i in rec_cmd_array])
            print()

        rec_checksum = self.__xor_checksum(rec_cmd_array[:-1])
        # print(rec_checksum)

        if rec_cmd_array[0] != self.START_BYTE_RECEIVE or rec_cmd_array[
                1] != rec_cmd_len or rec_cmd_array[
                    2] != checksum or rec_cmd_array[3] != rec_checksum:
            print(error_code)
            exit()

    def __receive_1_byte(self, checksum, error_code):
        rec_cmd_len = self.REC_LEN_1_BYTE
        rec_cmd_array = self.__mcu.read(rec_cmd_len)
        if print_CMD:
            print('<-', [hex(i) for i in rec_cmd_array])
            print()

        rec_checksum = self.__xor_checksum(rec_cmd_array[:-1])
        # print(rec_checksum)

        if rec_cmd_array[0] != self.START_BYTE_RECEIVE or rec_cmd_array[
                1] != rec_cmd_len or rec_cmd_array[
                    2] != checksum or rec_cmd_array[4] != rec_checksum:
            print(error_code)
            exit()
        value = rec_cmd_array[3]
        return value

    def __receive_2_byte(self, checksum, error_code):
        rec_cmd_len = self.REC_LEN_2_BYTE
        rec_cmd_array = self.__mcu.read(rec_cmd_len)
        if print_CMD:
            print('<-', [hex(i) for i in rec_cmd_array])
            print()

        rec_checksum = self.__xor_checksum(rec_cmd_array[:-1])
        # print(rec_checksum)

        if rec_cmd_array[0] != self.START_BYTE_RECEIVE or rec_cmd_array[
                1] != rec_cmd_len or rec_cmd_array[
                    2] != checksum or rec_cmd_array[5] != rec_checksum:
            print(error_code)
            exit()
        value = rec_cmd_array[3] << 8 | rec_cmd_array[4]
        return value

    def __receive_4_byte(self, checksum, error_code):
        rec_cmd_len = self.REC_LEN_4_BYTE
        rec_cmd_array = self.__mcu.read(rec_cmd_len)
        if print_CMD:
            print('<-', [hex(i) for i in rec_cmd_array])
            print()

        rec_checksum = self.__xor_checksum(rec_cmd_array[:-1])
        # print(rec_checksum)

        if rec_cmd_array[0] != self.START_BYTE_RECEIVE or rec_cmd_array[
                1] != rec_cmd_len or rec_cmd_array[
                    2] != checksum or rec_cmd_array[7] != rec_checksum:
            print(error_code)
            exit()
        value = rec_cmd_array[3] << 24 | rec_cmd_array[
            4] << 16 | rec_cmd_array[5] << 8 | rec_cmd_array[6]
        return value

    def __receive_n_byte(self, checksum, rec_cmd_len, error_code):
        rec_cmd_len = 3 + rec_cmd_len + 1
        rec_cmd_array = self.__mcu.read(rec_cmd_len)
        if print_CMD:
            print('<-', [hex(i) for i in rec_cmd_array])
            print()

        rec_checksum = self.__xor_checksum(rec_cmd_array[:-1])
        # print(rec_checksum)

        if rec_cmd_array[0] != self.START_BYTE_RECEIVE or rec_cmd_array[
                1] != rec_cmd_len or rec_cmd_array[
                    2] != checksum or rec_cmd_array[-1] != rec_checksum:
            print(error_code)
            exit()

        data = []
        for i in range(3, rec_cmd_len - 1):
            data.append(rec_cmd_array[i])
        return data

    def digital_write(self, address, pin, state):
        cmd = [
            self.START_BYTE_SEND, 0x7, address, self.CMD_DIGITAL_WRITE, pin,
            state
        ]
        checksum = self.__send_cmd(cmd, 'digital_write')
        self.__receive_0_byte(checksum, self.CMD_DIGITAL_WRITE)

    def digital_read(self, address, pin):
        cmd = [self.START_BYTE_SEND, 0x6, address, self.CMD_DIGITAL_READ, pin]
        checksum = self.__send_cmd(cmd, 'digital_read')
        return self.__receive_1_byte(checksum, self.CMD_DIGITAL_READ)

    def analog_read(self, address, pin):
        cmd = [self.START_BYTE_SEND, 0x6, address, self.CMD_ANALOG_READ, pin]
        checksum = self.__send_cmd(cmd, 'analog_read')
        return self.__receive_2_byte(checksum, self.CMD_ANALOG_READ)

    def servo_angle(self, address, servo_num, angle):
        cmd = [
            self.START_BYTE_SEND, 0x8, address, self.CMD_SERVO,
            self.SERVO_ANGLE, servo_num, angle
        ]
        checksum = self.__send_cmd(cmd, 'servo_angle')
        self.__receive_0_byte(checksum, self.CMD_DIGITAL_WRITE)

    def servo_target_us(self, address, servo_num, target_us):
        target_us_MSB = (target_us & 0b1111111100000000) >> 8
        target_us_LSB = (target_us & 0b0000000011111111)
        cmd = [
            self.START_BYTE_SEND, 0x09, address, self.CMD_SERVO,
            self.SERVO_TARGET_US, servo_num, target_us_MSB, target_us_LSB
        ]
        checksum = self.__send_cmd(cmd, 'servo_target_us')
        self.__receive_0_byte(checksum, self.CMD_DIGITAL_WRITE)

    def seven_segment_clear(self, address):
        cmd = [
            self.START_BYTE_SEND, 0x06, address, self.CMD_SEVEN_SEGMENT,
            self.SEVEN_SEG_CLEAR
        ]
        checksum = self.__send_cmd(cmd, 'seven_segment_clear')
        self.__receive_0_byte(checksum, 0)

    def seven_segment_set_brightness(self, address, brightness):
        cmd = [
            self.START_BYTE_SEND, 0x07, address, self.CMD_SEVEN_SEGMENT,
            self.SEVEN_SEG_SET_BRIGHTNESS, brightness
        ]
        checksum = self.__send_cmd(cmd, 'seven_segment_set_brightness')
        self.__receive_0_byte(checksum, 0)

    def seven_segment_all_on(self, address):
        cmd = [
            self.START_BYTE_SEND, 0x06, address, self.CMD_SEVEN_SEGMENT,
            self.SEVEN_SEG_ALL_ON
        ]
        checksum = self.__send_cmd(cmd, 'seven_segment_all_on')
        self.__receive_0_byte(checksum, 0)

    def seven_segment_set_signed_num(self, address, num):
        num_MSB = (num & 0b1111111100000000) >> 8
        num_LSB = (num & 0b0000000011111111)
        cmd = [
            self.START_BYTE_SEND, 0x8, address, self.CMD_SEVEN_SEGMENT,
            self.SEVEN_SEG_SET_SIGNED_NUM, num_MSB, num_LSB
        ]
        checksum = self.__send_cmd(cmd,
                                   'seven_segment_set_signed_num ' + str(num))
        self.__receive_0_byte(checksum, 0)

    def DHT11_update(self, address):
        cmd = [
            self.START_BYTE_SEND, 0x6, address, self.CMD_DHT11,
            self.DHT11_UPDATE
        ]
        checksum = self.__send_cmd(cmd, 'DHT11_update ')
        self.__receive_0_byte(checksum, 0)
        time.sleep(0.255)

    def DHT11_get_temp(self, address):
        self.DHT11_update(address)
        cmd = [
            self.START_BYTE_SEND, 0x6, address, self.CMD_DHT11,
            self.DHT11_TEMPERATURE
        ]
        checksum = self.__send_cmd(cmd, 'DHT11_get_temp ')
        return self.__receive_1_byte(checksum, 0)

    def DHT11_get_hum(self, address):
        cmd = [
            self.START_BYTE_SEND, 0x6, address, self.CMD_DHT11,
            self.DHT11_HUMIDITY
        ]
        checksum = self.__send_cmd(cmd, 'DHT11_get_hum ')
        return self.__receive_1_byte(checksum, 0)

    def DS18B20_get_temp(self, address):
        cmd = [
            self.START_BYTE_SEND, 0x6, address, self.CMD_DS18B20,
            self.DS18B20_TEMPERATURE
        ]
        checksum = self.__send_cmd(cmd, 'DS18B20_get_temp ')
        # return self.__receive_4_byte(checksum, 0)
        val = hex(self.__receive_4_byte(checksum, 0))
        # print(val)
        q = int(val, 16)
        b8 = struct.pack('i', q)
        time.sleep(0.255)
        return struct.unpack('f', b8)[0]

    def PCA9635_set_rgb(self, address, pin, r, g, b):
        cmd = [
            self.START_BYTE_SEND, 0x0A, address, self.CMD_PCA9635,
            self.PCA9635_SET_RGB, pin, r, g, b
        ]
        checksum = self.__send_cmd(cmd, 'PCA9635_set_rgb ')
        self.__receive_0_byte(checksum, 0)

    def PCA9635_set_pwm(self, address, pin, value):
        cmd = [
            self.START_BYTE_SEND, 0x8, address, self.CMD_PCA9635,
            self.PCA9635_SET_PWM, pin, value
        ]
        checksum = self.__send_cmd(cmd, 'PCA9635_set_pwm ')
        self.__receive_0_byte(checksum, 0)

    def rotary_encoder_get_count(self, address):
        cmd = [
            self.START_BYTE_SEND, 0x06, address, self.CMD_ROTARY_ENCODER,
            self.ROTARY_ENCODER_GET_COUNT
        ]
        checksum = self.__send_cmd(cmd, 'rotary_encoder_get_count ')
        val = self.__receive_4_byte(checksum, 0)
        return c_short(val << 6).value >> 6

    def rotary_encoder_get_sw(self, address):
        cmd = [
            self.START_BYTE_SEND, 0x06, address, self.CMD_ROTARY_ENCODER,
            self.ROTARY_ENCODER_GET_SW
        ]
        checksum = self.__send_cmd(cmd, 'rotary_encoder_get_sw ')
        return self.__receive_1_byte(checksum, 0)

    def e_platform_get_all_digital_sensor(self, address):
        cmd = [
            self.START_BYTE_SEND, 0x06, address, self.CMD_E_PLATFORM,
            self.E_PLATFORM_GET_ALL_DIGITAL_SENSOR
        ]
        checksum = self.__send_cmd(cmd, 'e_platform_get_all_sensor ')
        return self.__receive_n_byte(checksum, 7, self.CMD_E_PLATFORM)

    def e_platform_get_all_analog_sensor(self, address):
        cmd = [
            self.START_BYTE_SEND, 0x06, address, self.CMD_E_PLATFORM,
            self.E_PLATFORM_GET_ALL_ANALOG_SENSOR
        ]
        checksum = self.__send_cmd(cmd, 'e_platform_get_all_analog_sensor ')
        return_array = self.__receive_n_byte(checksum, 11 * 2,
                                             self.CMD_E_PLATFORM)
        adc = []
        for i in range(0, len(return_array), 2):
            adc.append(return_array[i + 1] << 8 | return_array[i])
        return adc

    def e_platform_get_all_sensor(self, address):

        cmd = [
            self.START_BYTE_SEND, 0x06, address, self.CMD_E_PLATFORM,
            self.E_PLATFORM_GET_ALL_SENSOR
        ]
        checksum = self.__send_cmd(cmd, 'e_platform_get_all_sensor ')

        return_array = self.__receive_n_byte(checksum, 29, self.CMD_E_PLATFORM)

        if return_array != -9999:
            gpio = return_array[0:7]
            print('gpio\t', gpio)
            adc = []
            for i in range(7, 28, 2):
                adc.append(return_array[i] << 8 | return_array[i + 1])
            print('adc\t', adc)

        # return_array = self.__receive_n_byte(checksum, 4, self.CMD_E_PLATFORM)
        # print(return_array)
        # print()
        # time.sleep(0.01)

        return

    def ultrasonic_update(self, address):
        cmd = [
            self.START_BYTE_SEND, 0x6, address, self.CMD_ULTRASONIC,
            self.ULTRASONIC_UPDATE
        ]
        checksum = self.__send_cmd(cmd, 'ultrasonic_update ')
        self.__receive_0_byte(checksum, 0)
        time.sleep(0.25)

    def ultrasonic_get_distance(self, address):
        self.ultrasonic_update(address)

        cmd = [
            self.START_BYTE_SEND, 0x6, address, self.CMD_ULTRASONIC,
            self.ULTRASONIC_GET_DISTANCE
        ]
        checksum = self.__send_cmd(cmd, 'ultrasonic_get_distance ')
        # return self.__receive_4_byte(checksum, 0)
        return self.__receive_2_byte(checksum, 0)
