import math
from datetime import datetime

def parse_time(block_time):
    return datetime.strptime(block_time, '%Y-%m-%dT%H:%M:%S')

def reputation(raw_reputation):
    rep = int(raw_reputation)
    if rep == 0:
        return 25
    score = max([math.log10(abs(rep)) - 9, 0]) * 9 + 25
    if rep < 0:
        score = 50 - score
    return score

def get_var_log_bins(nbins, minval, maxval):
    logmin = math.log10(minval)
    logmax = math.log10(maxval)
    binwidth = (logmax - logmin) / nbins
    return [float(math.pow(10, logmin + i * binwidth)) for i in range(0, nbins+1)]
