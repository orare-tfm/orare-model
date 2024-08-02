from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
import re

class CrawlingSpider1(CrawlSpider):
    name = "mycrawler" # Name of the spider
    allowed_domains = ["esglesia.barcelona"] # Allowed domains
    start_urls = ["https://esglesia.barcelona/es/parroquia/",
                  "https://esglesia.barcelona/es/parroquies/catedral-basilica-de-barcelona/"] # Starting URL

    rules = (
        Rule(LinkExtractor(allow="es/parroquies"), callback="parse_item", follow=True),
    )

    def parse_item(self, response):
        parroquia = response.css(".parish__title::text").get().strip()
        address1 = response.xpath("//dt[text()='Dirección']/following-sibling::dd[1]/text()").getall()
        address2 = response.xpath("//dt[text()='Dirección']/following-sibling::dd[2]/text()").getall()
        address = address1 + [","] + address2
        address = ' '.join([i.strip() for i in address])
        telephone = response.xpath("//dt[text()='Teléfono']/following-sibling::dd[1]/text()").get()
        email = response.xpath("//dt[text()='Correo electrónico']/following-sibling::dd[1]/a/text()").get()
        website = response.xpath("//dt[text()='Web']/following-sibling::dd[1]/a/@href").get()
        # Use regex to find the postal code
        postal_code = None
        match = re.search(r'\b\d{5}\b', address)
        if match:
            postal_code = match.group()
        
        js = {
            'parroquia': parroquia,
            'address': address,
            'postal_code': postal_code,
            'telephone': telephone,
            'email': email,
            'website': website
        }

        # Horarios de misas, descripción, actividades...
        items2 = response.css(".accordion-item").getall() 
        for item in items2:
            sel = Selector(text=item)
            t = sel.css(".accordion-title span::text").get() # Title
            vec = sel.css(".accordion-inner::text, .accordion-inner br::text").getall() # Content
            js[t] = vec
        yield js

class CrawlingSpider2(CrawlSpider):
    name = "mycrawler_events" # Name of the spider
    allowed_domains = ["catalunyareligio.cat"] # Allowed domains
    start_urls = ["https://www.catalunyareligio.cat/ca/agenda?page=0",
                  "https://www.catalunyareligio.cat/ca/agenda?page=1",
                  "https://www.catalunyareligio.cat/ca/agenda?page=2",
                  "https://www.catalunyareligio.cat/ca/agenda?page=3",
                  "https://www.catalunyareligio.cat/ca/agenda?page=4",
                  "https://www.catalunyareligio.cat/ca/agenda?page=5",
                  "https://www.catalunyareligio.cat/ca/agenda?page=6",
                  "https://www.catalunyareligio.cat/ca/agenda?page=7",
                  "https://www.catalunyareligio.cat/ca/agenda?page=8",
                  "https://www.catalunyareligio.cat/ca/agenda?page=9",
                  "https://www.catalunyareligio.cat/ca/agenda?page=10",
                  "https://www.catalunyareligio.cat/ca/agenda?page=11",
                  "https://www.catalunyareligio.cat/ca/agenda?page=12",
                  "https://www.catalunyareligio.cat/ca/agenda?page=13",
                  "https://www.catalunyareligio.cat/ca/agenda?page=14"]

    rules = (
        Rule(LinkExtractor(allow="ca/agenda"), callback="parse_item", follow=True),
    )

    def parse_item(self, response):
        title = response.css(".col.my-3.in-node-body span::text").get() # Title event
        date = response.xpath(".//div[contains(@class, 'field--name-field-event-date')]//time/@datetime").get()
        location = response.xpath(".//div[contains(@class, 'field--name-field-nom-del-lloc')]//div[@class='field__item']/text()").get()
        address = response.xpath(".//div[contains(@class, 'field--name-field-direccio')]//div[@class='field__item']/text()").get()
        municipality =  response.xpath(".//div[contains(@class, 'field--name-field-municipi')]//div[@class='field__item']/text()").get()
        organizer = response.xpath(".//div[contains(@class, 'field--name-field-nom-de-l-organitzador')]//div[@class='field__item']/text()").get()
        diocesis = response.css('.field--name-field-territori a::text').get()
        tematica = response.css('.field--name-field-seccio .field__items a::text').getall() # Temática value
        combined_text = ' '.join([item.strip() for item in tematica])

        title_description = response.css('div.field--name-field-tipus-esdeveniment div.field__item a::text').get()

        summary = response.xpath(".//div[contains(@class, 'field--name-field-resum-esdeveniment')]//text()").getall()
        summary_text = ' '.join([text.strip() for text in summary if text.strip()])

        # Extract the body text, including links
        body = response.xpath(".//div[contains(@class, 'field--name-body')]//p//text() | .//div[contains(@class, 'field--name-body')]//p//a/text()").getall()
        body_text = ' '.join([text.strip() for text in body if text.strip()])
        # Combine the text from summary and body
        combined_text_2 = f"{summary_text} {body_text}"

        yield {
                'title': title,
                'date': date,
                'location': location,
                'address': address,
                'municipality': municipality,
                'organizer': organizer,
                'diocesis': diocesis,
                'theme': combined_text,
                'title_description': title_description,
                'description': combined_text_2,
                'url': response.url
            }

class CrawlingSpider3(CrawlSpider):
    name = "mycrawler_events_2" # Name of the spider
    allowed_domains = ["catalunyacristiana.cat"] # Allowed domains
    start_urls = ["https://www.catalunyacristiana.cat/agenda"]

    rules = (
        Rule(LinkExtractor(allow="agenda"), callback="parse_item", follow=True),
    )

    def parse_item(self, response):
        title = response.css("div.col-md-4 h3::text").get()
        date = response.xpath(".//b[text()='Data:']/following-sibling::text()[1]").get(default='').strip()
        hour = response.xpath(".//b[text()='Hora:']/following-sibling::text()[1]").get(default='').strip()
        location = response.xpath(".//b[text()='Lloc:']/following-sibling::text()[1]").get(default='').strip()
        municipality = response.xpath(".//b[text()='Municipi:']/following-sibling::text()[1]").get(default='').strip()
        theme = response.xpath(".//b[text()='Temàtica:']/following-sibling::text()[1]").get(default='').strip()
        text_nodes = response.xpath("//div[contains(@class, 'entry-content')]/p//text()").getall()
        description = ' '.join([text.strip() for text in text_nodes if text.strip()])

        yield {
                'title': title.strip(),
                'date': date,
                'hour': hour,
                'location': location,
                'address': location,
                'municipality': municipality,
                'organizer': location,
                'diocesis': "",
                'theme': theme,
                'description': description,
                'url': response.url
            }

class CrawlingSpider4(CrawlSpider):
    name = "mycrawler_postal_code" # Name of the spider
    allowed_domains = ["idescat.cat"] # Allowed domains
    start_urls = ["https://www.idescat.cat/codis/?id=50&n=9&lang=es"]

    rules = (
        Rule(LinkExtractor(allow=r'codis/\?id=50&n=9&c=\d+&lang=es'), callback="parse_item", follow=True),
    )

    def parse_item(self, response):
        postal_codes = response.xpath('//div[h2[text()="Divisió territorial postal"]]//ul/li/text()').getall()
        yield {
                "url": response.url,
                "postal_codes": postal_codes
            }
        