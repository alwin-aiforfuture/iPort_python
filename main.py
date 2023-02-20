import iPort as ip
import sys
import time


def map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) +
               out_min)


mcu = ip.iPort(sys.argv[1])
address = 10

while True:

    # mcu.seven_segment_all_on(address)
    # time.sleep(0.1)
    # mcu.seven_segment_clear(address)
    # time.sleep(0.1)

    for i in range(0, 9999):
        mcu.seven_segment_set_signed_num(10, i)
        mcu.seven_segment_set_signed_num(11, i + 100)
        mcu.seven_segment_set_signed_num(12, i + 200)
        # time.sleep(1)
        # exit()

    # adc = mcu.analog_read(address, mcu.ADC_PIN_POTENTIOMETER)
    # print(adc)
    # mcu.seven_segment_set_signed_num(address, adc)
    # print(mcu.ultrasonic_get_distance(11))

exit()