def overlaps(a_start, a_end, b_start, b_end):
    return a_start < b_end and a_end > b_start
