import requests

programs = [
    ('International Business', 'international-business'),
    ('Software Engineering', 'software-engineering'),
    ('Industrial Design', 'industrial-design'),
]

bases = [
    'https://ju.se/en/study-at-ju/masters/{}.html',
    'https://ju.se/en/study-at-ju/our-programmes/master-programmes/{}.html',
    'https://ju.se/en/study-at-ju/education/master-programmes/{}.html',
    'https://ju.se/en/education/master-programmes/{}.html',
    'https://ju.se/en/education/programmes/{}.html',
]

for name, slug in programs:
    print('---', name)
    for b in bases:
        url = b.format(slug)
        try:
            r = requests.head(url, allow_redirects=True, timeout=5)
            print(url, r.status_code, r.url)
        except Exception as e:
            print(url, 'error', e)
