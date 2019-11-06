import json
import logging
import sys
import requests
from lxml import html
from urllib import parse
import csv

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Doctoralia(object):
    def __init__(self):
        self.session = requests.Session()
        self.host = 'https://www.doctoralia.com.br/especializacoes-medicas'

    def parse_specialist(self, url):
        response = self.session.get(url)
        page = html.fromstring(response.text)
        name = page.xpath(
            'string(//div[@class="unified-doctor-header-info__name"]//span[@itemprop="name"]/text())'
        )
        specialties = page.xpath(
            '//h2[@class="h4 text-muted text-base-weight offset-bottom-0"]/a/@title'
        )
        specialties = ', '.join(specialties) if specialties else []
        region = page.xpath(
            'string(//span[@class="province region"]/@content)'
        ).split(' ')[-1]

        city = page.xpath(
            'string(//span[@class="city"]/@content)'
        )
        phones = page.xpath('//a[contains(@href, "tel:")]/@href')
        phones = ', '.join([x.replace('tel:', '').strip()
                            for x in phones]) if phones else []
        data = {
            'name': name,
            'specialties': specialties,
            'region': region,
            'city': city,
            'phones': phones
        }
        logging.info(data)
        return data

    def parse_specialists(self, url):
        url = parse.urljoin(self.host, url)
        response = self.session.get(url)
        page = html.fromstring(response.text)
        links = page.xpath('//a[@class="rank-element-name__link"]/@href')
        return links

    def get_specializations(self):

        response = self.session.get(url=self.host)
        page = html.fromstring(response.text)
        links = page.xpath('//h3[@class="panel-title"]//a[1]/@href')
        return links

    def stalk(self):
        logging.info('Iniciando crawler: Doctoralia')
        links_specializations = self.get_specializations()
        specialists = list()
        for link in links_specializations:
            links_specialists = self.parse_specialists(link)
            for link in links_specialists:
                specialist = self.parse_specialist(link)
                specialists.append(specialist)

        return specialists


if __name__ == '__main__':
    doc = Doctoralia()
    response = doc.stalk()
    with open('especialistas.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(list(response[0].keys()))

        for row in response:
            writer.writerow(list(row.values()))
    json.dump(response, open('especialistas.json', 'w'))
