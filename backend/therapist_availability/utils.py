def overlaps(a_start, a_end, b_start, b_end):
    return a_start < b_end and a_end > b_start


def has_overlapping_intervals(intervals):
    sorted_intervals = sorted(intervals, key=lambda item: item["start_time"])
    for index in range(len(sorted_intervals) - 1):
        current = sorted_intervals[index]
        next_interval = sorted_intervals[index + 1]
        if overlaps(
            current["start_time"],
            current["end_time"],
            next_interval["start_time"],
            next_interval["end_time"],
        ):
            return True
    return False


def merge_overlapping_intervals(intervals):
    """Merge overlapping or adjacent intervals into a minimal set."""
    intervals = list(intervals)
    if not intervals:
        return []

    sorted_intervals = sorted(intervals, key=lambda item: item["start_time"])
    merged = [
        {
            "start_time": sorted_intervals[0]["start_time"],
            "end_time": sorted_intervals[0]["end_time"],
        }
    ]
    for interval in sorted_intervals[1:]:
        current = merged[-1]
        if interval["start_time"] <= current["end_time"]:
            current["end_time"] = max(current["end_time"], interval["end_time"])
        else:
            merged.append(
                {
                    "start_time": interval["start_time"],
                    "end_time": interval["end_time"],
                }
            )
    return merged


def merge_adjacent_blocks(blocks):
    """Merge adjacent intervals within the same day_of_week."""
    by_day = {}
    for block in blocks:
        by_day.setdefault(block["day_of_week"], []).append(block)

    merged = []
    for day_of_week in sorted(by_day):
        for interval in merge_overlapping_intervals(by_day[day_of_week]):
            merged.append({"day_of_week": day_of_week, **interval})
    return merged


def clip_interval_to_blocks(interval, blocks):
    """Return sub-intervals of interval that overlap with any block in blocks."""
    result = []
    for block in blocks:
        start = max(interval["start_time"], block["start_time"])
        end = min(interval["end_time"], block["end_time"])
        if start < end:
            result.append({"start_time": start, "end_time": end})
    return sorted(result, key=lambda item: item["start_time"])


def exclude_intervals(availability_blocks, exclusion_blocks):
    """Subtract exclusion intervals from availability intervals."""
    result = []
    exclusions = sorted(exclusion_blocks, key=lambda item: item["start_time"])

    for block in sorted(availability_blocks, key=lambda item: item["start_time"]):
        start = block["start_time"]
        end = block["end_time"]
        cursor = start

        for exclusion in exclusions:
            if exclusion["end_time"] <= cursor:
                continue
            if exclusion["start_time"] >= end:
                break
            if exclusion["start_time"] > cursor:
                result.append(
                    {"start_time": cursor, "end_time": exclusion["start_time"]}
                )
            cursor = max(cursor, exclusion["end_time"])
            if cursor >= end:
                break

        if cursor < end:
            result.append({"start_time": cursor, "end_time": end})
    return result
