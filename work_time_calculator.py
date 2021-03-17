from functools import reduce
from typing import List

LEADERSHIP = '👨🏻‍🏫'
BUILDING = '👨🏻‍💻'
ETC = '😴'

TOTAL_WORK_HOURS = 40


# TODO re-order functions based on use


def blank_lines(line: str):
    return False if line == '\n' else True


def _hour_to_minutes(hour):
    split_hour = hour.split()
    meridian = split_hour[1]
    hour_and_minutes = split_hour[0].split(':')
    if hour_and_minutes[0] == '12':
        hour_and_minutes[0] = '0'
    total_minutes = (int(hour_and_minutes[0]) * 60) + (int(hour_and_minutes[1])) + (0 if meridian == 'AM' else 720)
    return total_minutes


def _count_time(time):  # TODO maybe total_times?
    start_and_end = time.split(' to ')
    total_minutes = reduce(lambda x, y: y - x, map(_hour_to_minutes, start_and_end))
    return total_minutes / 60


def _total_times(times_grouped_by_tag):
    dates_with_totaled_times = {}
    for date, tag_and_times in times_grouped_by_tag.items():
        tagged_totals = []
        dates_with_totaled_times[date] = tagged_totals
        for tag, times in tag_and_times.items():
            total_time = reduce(lambda x, y: x + y, map(_count_time, times))
            tagged_totals.append((tag, total_time))

    return dates_with_totaled_times


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


def _group_events_by_date(clean_lines: List[str]):
    def pair_tag_with_event(stuff, acc):
        if stuff:
            tag = stuff.pop(0)
            event = stuff.pop(0)
            acc.append((tag, event))
            return pair_tag_with_event(stuff, acc)

        return acc

    tags_and_events = pair_tag_with_event(clean_lines, [])
    tags_and_split_events = list(map(lambda p: (p[0], p[1].split(' at ')), tags_and_events))
    tag_and_time_by_date = list(map(lambda p: {p[1][0]: (p[0], p[1][1])}, tags_and_split_events))

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


def clean_tag(line):
    if line.startswith(ETC):
        return ETC
    elif line.startswith(LEADERSHIP):
        return LEADERSHIP
    elif line.startswith(BUILDING):
        return BUILDING
    else:
        return line


# TODO try simplifying this following
#  https://stackoverflow.com/questions/24831476/what-is-the-python-way-of-chaining-maps-and-filters
def _clean(lines: List[str]):
    return list(map(lambda l: l.rstrip('\n').lstrip('Scheduled: '),
                    map(clean_tag,
                        filter(lambda l: l != '\n', lines)
                        )
                    ))


def _generate_subtotal_output_lines(totaled_times):
    lines = []

    for date, tags_and_hours_totals in totaled_times.items():
        line = f'{date}: '
        totals = {
            BUILDING: 0,
            LEADERSHIP: 0,
            ETC: 0
        }
        for pair in tags_and_hours_totals:
            tag = pair[0]
            hours = pair[1]

            running_total = totals[tag]
            totals[tag] = running_total + hours

        for tag, total in totals.items():
            line += f'{tag}: {total} '

        lines.append(line.rstrip(' '))
    return lines


def _generate_targets(hours):
    target_percentages = {BUILDING: .4, LEADERSHIP: .4, ETC: .2}
    targets = {}

    for tag, percentage in target_percentages.items():
        targets[tag] = target_percentages[tag] * hours

    return targets


def _generate_total_line(totaled_items):
    starter = {BUILDING: 0, LEADERSHIP: 0, ETC: 0}
    target = _generate_targets(TOTAL_WORK_HOURS)

    for tagged_totals in totaled_items.values():
        for tag, total in tagged_totals:
            tag_total = starter[tag]
            starter[tag] = tag_total + total

    line = ''
    for k, v in starter.items():
        line += f'{k}: {v}/{str(target[k]).rstrip(".0")} '

    return line.rstrip(' ')


def _main():
    with open('this-week.txt', encoding='utf8', mode='r') as f:
        lines = f.readlines()
        cleaned = _clean(lines)
        grouped = _group_events_by_date(cleaned)
        grouped_even_more = _group_times_by_tag(grouped)
        dates_with_totals = _total_times(grouped_even_more)

        with open('output.txt', 'w') as output:
            for line in _generate_subtotal_output_lines(dates_with_totals):
                output.write(line + '\n')

            output.write('\n')
            output.write(_generate_total_line(dates_with_totals))


if __name__ == '__main__':
    _main()
