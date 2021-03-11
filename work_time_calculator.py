from typing import List

LEADERSHIP = '👨🏻‍🏫'
BUILDING = '👨🏻‍💻'
ETC = '😴'


def blank_lines(line: str):
    return False if line == '\n' else True


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
    with open('input.txt', encoding='utf8', mode='r') as f:
        lines = f.readlines()
        cleaned = _clean(lines)
        grouped = _group_events_by_date(cleaned)
        # group_events_by_date(lines)
        # tags_and_schedules = list(filter(blank_lines, lines))
        # cleaned = list(map(lambda l: l.rstrip('\n').lstrip('Scheduled: '), tags_and_schedules))
        # assert len(cleaned) % 2 == 0, f'{len(cleaned)}, {cleaned}'
        #
        # events = []
        # for i in range(1, int(len(cleaned) / 2)):
        #     tag = cleaned.pop(0)
        #     schedule = cleaned.pop(0)
        #     events.append((tag, schedule.split(' at ')))
        #
        # mapped_events = list(map(lambda e: {e[1][0]: (e[0], e[1][1])}, events))
        # print(grouped)
        for k, v in grouped.items():
            print(f'{k}:  {v}')


if __name__ == '__main__':
    print('hello world')
    _main()
