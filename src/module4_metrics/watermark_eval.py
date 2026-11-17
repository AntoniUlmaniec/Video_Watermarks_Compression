#BER = liczba błędnych bitów / liczba wszystkich bitów
#0 - odczyt bez błędów, a 0,5 - zgadywanie

import numpy as np


def compute_ber(bits, message):
    ber_mean = np.mean(bits != message)
    voted = np.mean(bits, axis=0) > 0.5
    ber_voted = np.mean(voted != message)

    return {"ber_mean": float(ber_mean), "ber_voted": float(ber_voted)}