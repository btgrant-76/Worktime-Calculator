from work_time_calculator import _group_events_by_date, _clean, _group_times_by_tag

FILE_LINES = [
    '😴 .5\n',
    'Scheduled: Mar 8, 2021 at 8:15 AM to 8:45 AM\n',
    '\n',
    '👨🏻‍🏫 1.75\n',
    'Scheduled: Mar 8, 2021 at 8:45 AM to 10:30 AM\n',
    '\n',
    '👨🏻‍💻 .75\n',
    'Scheduled: Mar 9, 2021 at 4:45 PM to 5:30 PM\n',
    '\n',
    '👨🏻‍🏫 (1)\n',
    'Scheduled: Mar 10, 2021 at 6:00 AM to 7:00 AM\n',
    '\n',
    '😴 1.25\n',
    'Scheduled: Mar 10, 2021 at 7:30 AM to 8:45 AM\n'
]

CLEANED_LINES = [
    '😴',
    'Mar 8, 2021 at 8:15 AM to 8:45 AM',
    '👨🏻‍🏫',
    'Mar 8, 2021 at 8:45 AM to 10:30 AM',
    '👨🏻‍💻',
    'Mar 9, 2021 at 4:45 PM to 5:30 PM',
    '👨🏻‍🏫',
    'Mar 10, 2021 at 6:00 AM to 7:00 AM',
    '😴',
    'Mar 10, 2021 at 7:30 AM to 8:45 AM',
]


def test_clean():
    cleaned = _clean(FILE_LINES)
    assert cleaned == CLEANED_LINES


def test_grouping():
    grouped_events = _group_events_by_date(CLEANED_LINES)
    assert grouped_events == {
        'Mar 8, 2021': [
            ('😴', '8:15 AM to 8:45 AM'),
            ('👨🏻‍🏫', '8:45 AM to 10:30 AM'),
        ],
        'Mar 9, 2021': [
            ('👨🏻‍💻', '4:45 PM to 5:30 PM'),
        ],
        'Mar 10, 2021': [
            ('👨🏻‍🏫', '6:00 AM to 7:00 AM'),
            ('😴', '7:30 AM to 8:45 AM')
        ]
    }


def test_tag_grouping():
    grouped_events = {
        'Mar 8, 2021': [
            ('😴', '8:15 AM to 8:45 AM'),
            ('👨🏻‍🏫', '8:45 AM to 10:30 AM'),
            ('👨🏻‍🏫', '1:00 PM to 3:30 PM'),
        ],
        'Mar 9, 2021': [
            ('👨🏻‍💻', '4:45 PM to 5:30 PM'),
        ],
        'Mar 10, 2021': [
            ('👨🏻‍🏫', '6:00 AM to 7:00 AM'),
            ('😴', '7:30 AM to 8:45 AM'),
            ('👨🏻‍🏫', '9:00 AM to 10:00 AM'),
            ('😴', '10:30 AM to 12:00 PM')
        ]
    }

    times_grouped_by_tag = _group_times_by_tag(grouped_events)
    assert times_grouped_by_tag == {
        'Mar 8, 2021': {
            '😴': ['8:15 AM to 8:45 AM'],
            '👨🏻‍🏫': ['8:45 AM to 10:30 AM', '1:00 PM to 3:30 PM']
        },
        'Mar 9, 2021': {
            '👨🏻‍💻': ['4:45 PM to 5:30 PM']
        },
        'Mar 10, 2021': {
            '👨🏻‍🏫': ['6:00 AM to 7:00 AM', '9:00 AM to 10:00 AM'],
            '😴': ['7:30 AM to 8:45 AM', '10:30 AM to 12:00 PM']
        }
    }




