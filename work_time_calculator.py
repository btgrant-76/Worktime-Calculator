#!/usr/bin/env python3
import re
import sys
from functools import reduce
from typing import List, AnyStr

LEADERSHIP = "👨🏻‍🏫"
BUILDING = "👨🏻‍💻"
ETC = "😴"

ALL_TAGS = [LEADERSHIP, BUILDING, ETC]

TOTAL_WORK_HOURS = 40


def _main(input_file_name: str, available_hours: int):
    with open(input_file_name, encoding="utf8", mode="r") as f:
        lines = f.readlines()

        subtotals, total_line = _calculate_work_time(available_hours, lines)

        output_file_name = _generate_output_file_name(input_file_name)
        with open(output_file_name, "w") as output:
            for line in subtotals:
                output.write(line + "\n")

            output.write("\n")
            output.write(total_line)

        print(f'calculations written to "{output_file_name}"')


def _calculate_work_time(available_hours, lines):
    cleaned = _clean(lines)
    grouped = _group_events_by_date(cleaned)
    grouped_by_tag = _group_times_by_tag(grouped)
    grouped_by_valid_tag = _filter_unmatched_tags(grouped_by_tag)
    dates_with_totals = _total_times(grouped_by_valid_tag)
    subtotals = _generate_subtotal_output_lines(dates_with_totals)
    total_line = _generate_total_line(dates_with_totals, available_hours)
    return subtotals, total_line


def _generate_output_file_name(input_file_name: str):
    return f"{input_file_name.rstrip('.txt')}-calculated.txt"


def _clean(lines: List[str]):
    no_blank_lines = filter(lambda l: l != "\n", lines)
    lines_with_cleaned_tags = map(_clean_tag, no_blank_lines)
    cleaned_and_stripped = map(
        lambda l: l.rstrip("\n").lstrip("Scheduled: ").replace(r", \w{3}", ""),
        lines_with_cleaned_tags,
    )

    with_to_time_separator = map(
        # Copy/paste from Calendar.app uses "to"; output from iCalBuddy uses "-"
        lambda line: re.sub(r"-", "to", line),
        cleaned_and_stripped,
    )

    without_timezones = map(
        lambda cleaned: re.sub(r", \w{3}$", "", cleaned), with_to_time_separator
    )

    return list(without_timezones)


def _clean_tag(line: AnyStr) -> str:
    if line.startswith(ETC):
        return ETC
    elif line.startswith(LEADERSHIP):
        return LEADERSHIP
    elif line.startswith(BUILDING):
        return BUILDING
    else:
        return line


def _group_events_by_date(clean_lines: List[str]):
    def pair_tag_with_event(stuff, acc):
        if stuff:
            tag = stuff.pop(0)
            event = stuff.pop(0)
            acc.append((tag, event))
            return pair_tag_with_event(stuff, acc)

        return acc

    tags_and_events = pair_tag_with_event(clean_lines, [])
    # print(f"pair_tag_with_event output: \n{tags_and_events}")

    tags_and_split_events = list(
        map(lambda p: (p[0], p[1].split(" at ")), tags_and_events)
    )
    tag_and_time_by_date = list(
        map(lambda p: {p[1][0]: (p[0], p[1][1])}, tags_and_split_events)
    )

    def group_events(events_by_date):  # TODO could this be a reduce?
        acc = {}
        for e in events_by_date:
            date = list(e.keys())[0]
            events = acc.get(date)
            if events:
                events.append(e[date])
            else:
                current_event = e[date]
                new_events = [current_event]
                acc[date] = new_events

        return acc

    return group_events(tag_and_time_by_date)


def _group_times_by_tag(grouped_events):
    final = {}
    for k, v in grouped_events.items():
        times_by_tag = {}
        for tag_and_time in v:
            tag = tag_and_time[0]
            time = tag_and_time[1]
            times = times_by_tag.get(tag)

            if times:
                times.append(time)
            else:
                new_times = [time]
                times_by_tag[tag] = new_times
        final[k] = times_by_tag

    return final


def _filter_unmatched_tags(grouped_by_tag):
    filtered = {}

    for date, tagged in grouped_by_tag.items():
        valid_tags = {}

        for tag, events in tagged.items():
            if tag in ALL_TAGS:
                valid_tags[tag] = events

        filtered[date] = valid_tags

    return filtered


def _total_times(times_grouped_by_tag):
    dates_with_totaled_times = {}
    for date, tag_and_times in times_grouped_by_tag.items():
        tagged_totals = []
        dates_with_totaled_times[date] = tagged_totals
        for tag, times in tag_and_times.items():
            total_time = reduce(lambda x, y: x + y, map(_count_time, times))
            tagged_totals.append((tag, total_time))

    return dates_with_totaled_times


def _hour_to_minutes(hour):
    split_hour = hour.split()
    meridian = split_hour[1]
    hour_and_minutes = split_hour[0].split(":")
    if hour_and_minutes[0] == "12":
        hour_and_minutes[0] = "0"
    total_minutes = (
        (int(hour_and_minutes[0]) * 60)
        + (int(hour_and_minutes[1]))
        + (0 if meridian == "AM" else 720)
    )
    return total_minutes


def _count_time(time):  # TODO maybe total_times?
    start_and_end = time.split(" to ")
    total_minutes = reduce(lambda x, y: y - x, map(_hour_to_minutes, start_and_end))
    return total_minutes / 60


def _generate_subtotal_output_lines(totaled_times):
    lines = []

    for date, tags_and_hours_totals in totaled_times.items():
        line = f"{date}: "
        totals = {BUILDING: 0, LEADERSHIP: 0, ETC: 0}
        for pair in tags_and_hours_totals:
            tag = pair[0]
            hours = pair[1]

            # print(pair)

            running_total = totals[tag]
            totals[tag] = running_total + hours

        for tag, total in totals.items():
            line += f"{tag}: {total} "

        lines.append(line.rstrip(" "))
    return lines


def _generate_total_line(totaled_items, available_hours=40):
    starter = {BUILDING: 0, LEADERSHIP: 0, ETC: 0}
    target = _generate_targets(available_hours)

    for tagged_totals in totaled_items.values():
        for tag, total in tagged_totals:
            tag_total = starter[tag]
            starter[tag] = tag_total + total

    total_line = " ".join(
        [f'{k}: {v}/{str(target[k]).rstrip(".0")}' for k, v in starter.items()]
    )
    return f"{total_line} ({sum(starter.values())}/{available_hours})"


def _generate_targets(hours):
    target_percentages = {BUILDING: 0.4, LEADERSHIP: 0.4, ETC: 0.2}
    targets = {}

    for tag, percentage in target_percentages.items():
        targets[tag] = target_percentages[tag] * hours

    return targets


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("please provide an input file name")
        exit(-1)

    input_file: str = sys.argv[1].strip()
    print(f"input file name is '{input_file}'")

    hours_input: str = input("available hours (default = 40):  ")
    _main(input_file, 40 if hours_input.strip() == "" else int(hours_input))
