import re

import settings
import requests
import PythonApi.scraperApi.webscraper as webscraper
from tokens import DEBUG
login_url = 'http://www.jotihunt.net/groep/loginform.php'


def get_opdrachten():
    try:
        with requests.Session() as session:
            session.cookies.set('PHPSESSID', settings.Settings().phpsessid)
            r = session.get('http://www.jotihunt.net/groep/opdrachten.php')
            scraper = webscraper.TableHTMLParser()
            scraper.feed(r.text)
            scraper.fix_tables()
            # scraper.print_tables()
            with open('opdracht.log', 'w') as f:
                f.write(r.text)
            scraper.tables[0] = fix_opdrachten(scraper.tables[0])
            return (scraper.tables[0],
                   ['inzendtijd', 'title', 'punten'],
                   'title')
    except Exception as e:
        import Updates
        Updates.get_updates().error(e, 'get_opdrachten')
        return [], ['inzendtijd', 'title', 'punten'], 'title'


def get_hunts():
    try:
        with requests.Session() as session:
            session.cookies.set('PHPSESSID', settings.Settings().phpsessid)
            r = session.get('http://www.jotihunt.net/groep/hunts.php')
            scraper = webscraper.TableHTMLParser()
            scraper.feed(r.text)
            with open('hunts.log', 'w') as f:
                f.write(r.text)
            scraper.fix_tables()
            # scraper.print_tables()
            return scraper.tables[0], ['hunttijd', 'meldtijd', 'code',
                                       'status', 'toelichting',
                                       'punten'], 'code'
    except Exception as e:
        import Updates
        Updates.get_updates().error(e, 'get_hunts')
        return [], ['hunttijd', 'meldtijd', 'code', 'status', 'toelichting',
                    'punten'], 'code'


def fix_opdrachten(table):
    for i, row in enumerate(table):
        table.remove(row)
        row[1] = row[1].split('\n')[1]
        p = re.compile('\t')
        row[1] = p.sub('', row[1])
        table.insert(i, row)
    return table


if __name__ == '__main__':
    webscraper.print_table(get_opdrachten()[0])
    webscraper.print_table(get_hunts()[0])
