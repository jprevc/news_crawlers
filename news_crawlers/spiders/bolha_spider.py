import os
import scrapy
import yaml
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class BolhaSpider(scrapy.Spider):
    name = "bolha"
    home_path = os.environ.get('NEWS_CRAWLERS_HOME', os.path.dirname(__file__))

    # get configuration data
    with open(os.path.join(home_path, 'bolha_configuration.yaml'), 'r') as f:
        config_data = yaml.safe_load(f)

    def start_requests(self):
        for query, url in self.config_data['urls'].items():
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs={'query': query})

    def parse(self, response, query):
        items = response.xpath('//*[text() = "Oglasi na bolha.com"]/following-sibling::ul/li[@data-href]')
        for item in items:
            yield {
                'query': query,
                'url': response.urljoin(item.attrib['data-href']),
                'price': item.xpath('.//li[@class="price-item"]/strong//text()').get().strip(),
            }

        next_page = response.xpath('//a[@class="Pagination-link"][text() = "Naslednja\xa0"]')
        if next_page:
            yield response.follow(next_page.attrib['href'], cb_kwargs={'query': query})


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())

    process.crawl('bolha')
    process.start()  # the script will block here until the crawling is finished
