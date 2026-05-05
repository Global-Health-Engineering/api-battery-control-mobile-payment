from machine import ADC
import time

adc = ADC(26)          # GP26 = ADC0
ADC_MAX = 65535        # read_u16() gives 0..65535

# --- function to determine offset automatically -----------------------------------
# Important: no current during measurement
def measure_offset(samples=200, delay_ms=2):
    s = 0
    for _ in range(samples):
        s += adc.read_u16()
        time.sleep_ms(delay_ms)
    return s // samples

#offset = measure_offset()
#offset = 934 #from testing i got this value

# --- Umrechnung ADC-Counts -> Strom ------------------------------------------
#
# counts_per_amp:
#   185 mV/A is a good value for ACS712-05B:
#   (0.185 / 3.3) * 65535 ≈ 3674 counts per Ampere
COUNTS_PER_AMP = 3674

def Currentmeasure(offset, dt):
    raw = adc.read_u16()
    delta = raw - offset
    current_a = delta / COUNTS_PER_AMP
    print("ADC:", raw, "I[A]:", round(current_a, 3))
    time.sleep(dt)
    return current_a

