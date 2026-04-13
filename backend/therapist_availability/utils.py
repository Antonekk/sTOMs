def overlaps(a_start, a_end, b_start, b_end):
    return a_start < b_end and a_end > b_start


def exclude_intervals(availability_blocks, exclusion_blocks):
    """Subtract exclusion intervals from availability intervals."""
    result = []
    ptr = 0
    exclusion_blocks = sorted(exclusion_blocks, key=lambda x: x["start_time"])

    for block in sorted(availability_blocks, key=lambda x: x["start_time"]):
        start_time, end_time = block["start_time"], block["end_time"]

        while (
            ptr < len(exclusion_blocks)
            and exclusion_blocks[ptr]["start_time"] <= start_time
        ):
            ptr += 1

        current_start_time = start_time

        while (
            ptr < len(exclusion_blocks)
            and exclusion_blocks[ptr]["start_time"] < end_time
        ):
            exclusion_block = exclusion_blocks[ptr]

            if exclusion_block["start_time"] > current_start_time:
                result.append(
                    {
                        "start_time": current_start_time,
                        "end_time": exclusion_block["start_time"],
                    }
                )
            current_start_time = max(start_time, exclusion_block["end_time"])
            if current_start_time >= end_time:
                break
            ptr += 1

        if current_start_time < end_time:
            result.append(
                {
                    "start_time": current_start_time,
                    "end_time": end_time,
                }
            )
    return result
