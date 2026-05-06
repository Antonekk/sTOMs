def overlaps(a_start, a_end, b_start, b_end):
    return a_start < b_end and a_end > b_start


def merge_adjacent_blocks(blocks):
    """Merge adjacent intervals within the same day_of_week"""
    by_day: dict[int, list] = {}
    for block in blocks:
        by_day.setdefault(block["day_of_week"], []).append(block)

    merged = []
    for day_of_week in sorted(by_day):
        sorted_blocks = sorted(by_day[day_of_week], key=lambda item: item["start_time"])
        current = {
            "day_of_week": day_of_week,
            "start_time": sorted_blocks[0]["start_time"],
            "end_time": sorted_blocks[0]["end_time"],
        }
        for next_block in sorted_blocks[1:]:
            if current["end_time"] == next_block["start_time"]:
                current["end_time"] = next_block["end_time"]
            else:
                merged.append(current)
                current = {
                    "day_of_week": day_of_week,
                    "start_time": next_block["start_time"],
                    "end_time": next_block["end_time"],
                }
        merged.append(current)
    return merged


def exclude_intervals(availability_blocks, exclusion_blocks):
    """Subtract exclusion interval blocks from availability interval blocks"""
    result = []
    exclusion_blocks = sorted(exclusion_blocks, key=lambda x: x["start_time"])

    for block in sorted(availability_blocks, key=lambda x: x["start_time"]):
        start_time, end_time = block["start_time"], block["end_time"]
        current_start_time = start_time

        for exclusion in exclusion_blocks:
            if exclusion["end_time"] <= current_start_time:
                continue
            if exclusion["start_time"] >= end_time:
                break

            if exclusion["start_time"] > current_start_time:
                result.append(
                    {
                        "start_time": current_start_time,
                        "end_time": exclusion["start_time"],
                    }
                )

            current_start_time = max(current_start_time, exclusion["end_time"])
            if current_start_time >= end_time:
                break

        if current_start_time < end_time:
            result.append(
                {
                    "start_time": current_start_time,
                    "end_time": end_time,
                }
            )
    return result
