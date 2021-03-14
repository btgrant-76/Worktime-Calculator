from functools import reduce
from typing import List

LEADERSHIP = '👨🏻‍🏫'
BUILDING = '👨🏻‍💻'
ETC = '😴'

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


def _count_time(time):  # maybe total_times?
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
            # dates_with_totaled_times[date] = {tag: total_time}
            print(f'{times} is {total_time} hours')

    return dates_with_totaled_times


def _group_times_by_tag(grouped_events):
    final = {}
    for k, v in grouped_events.items():
        times_by_tag = {}
        # print(f'k: {k}, v: {v}')
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


def _group_events_by_date(clean_lines: List[str]):  # TODO mark private

    def pair_tag_with_event(stuff, acc):
        if stuff:
            tag = stuff.pop(0)
            event = stuff.pop(0)
            acc.append((tag, event))
            return pair_tag_with_event(stuff, acc)

        return acc

    tags_and_events = pair_tag_with_event(clean_lines, [])
    # print('\n')
    # [print(x) for x in tags_and_events]

    tags_and_split_events = list(map(lambda p: (p[0], p[1].split(' at ')), tags_and_events))
    # print('\ntags_and_split_events')
    # [print(x) for x in tags_and_split_events]

    tag_and_time_by_date = list(map(lambda p: {p[1][0]: (p[0], p[1][1])}, tags_and_split_events))

    # print('\ntag_and_time_by_date')
    # [print(x) for x in tag_and_time_by_date]

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

    grouped = group_events(tag_and_time_by_date)
    # print(f'\ngrouped\n{grouped}')

    return grouped


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


def _main():
    with open('this-week.txt', encoding='utf8', mode='r') as f:
        lines = f.readlines()
        cleaned = _clean(lines)
        grouped = _group_events_by_date(cleaned)
        grouped_even_more = _group_times_by_tag(grouped)
        dates_with_totals = _total_times(grouped_even_more)

        with open('output.txt', 'w') as output:
            totals = {
                LEADERSHIP: 0,
                ETC: 0,
                BUILDING: 0
            }

            for date, tags_and_hours_totals in dates_with_totals.items():
                output.write(f'{date}: ')
                for pair in tags_and_hours_totals:
                    tag = pair[0]
                    hours = pair[1]

                    weekly_total = totals[tag]
                    totals[tag] = weekly_total + hours

                    output.write(f'{tag}: {hours} ')
                output.write('\n')

            for tag, hours in totals.items():
                output.write(f'{tag}: {hours} ')


if __name__ == '__main__':
    print('hello world')
    _main()
