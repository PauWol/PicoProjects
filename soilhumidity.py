from machine import ADC, Pin
import time

class Plant:
    def __init__(self, adc_pin: int):
        self.sensor = ADC(adc_pin)
        self.average_level = []
        self.offset = 30
        self.AVERAGE_MAX = 10
        self.threshold_count = 0
        self.threshold_count_start_time = 0
        self.threshold_timer_time_plus_count = 4
        self.over_threshold_timer = 0

    @property
    def get_sensor_data(self):
        analog_value = self.sensor.read_u16()
        data = round((analog_value / 10) - self.offset, 2)
        self.update_average(data)
        return data

    def update_average(self, value):
        if len(self.average_level) >= self.AVERAGE_MAX:
            self.average_level.pop(0)
        self.average_level.append(value)

    @property
    def get_average(self):
        if len(self.average_level) == 0:
            return 0  # Prevent division by zero
        return round(sum(self.average_level) / len(self.average_level), 2)

    def set_threshold_timer(self):
        if self.threshold_count_start_time == 0:
            self.threshold_count_start_time = time.time()
            print("Timer set")
        elif (time.time() - self.threshold_count_start_time) >= self.threshold_timer_time_plus_count:
            self.threshold_count_start_time = 0
            print("Timer erased")

    def under_threshold(self, threshold: int):
        if self.get_average <= threshold:
            self.threshold_count += 1
            #print("Count:", self.threshold_count)
            if self.threshold_count_start_time == 0:
                self.threshold_count_start_time = time.time()
                #print("Threshold timer started")
            if (time.time() - self.threshold_count_start_time) >= self.threshold_timer_time_plus_count:
                if self.threshold_count >= self.threshold_timer_time_plus_count:
                    self.threshold_count_start_time = 0
                    self.threshold_count = 0
                    return True
            return False
        else:
            self.threshold_count = 0
            self.threshold_count_start_time = 0
            return False

    def over_threshold(self):
        if self.threshold_count <= 0:
            if self.over_threshold_timer == 0:
                self.over_threshold_timer = time.time()
                #print("Over threshold timer started")
            if (time.time() - self.over_threshold_timer) >= self.threshold_timer_time_plus_count:
                self.over_threshold_timer = 0
                return True
            return False
        else:
            self.over_threshold_timer = 0
            return False

