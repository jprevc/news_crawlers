import os
import scrapy
import yaml
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class BolhaSpider(scrapy.Spider):
    name = "bolha"
    home_path = os.environ.get('PAGINATOR_CRAWLER_HOME', os.path.dirname(__file__))

    # get configuration data
    with open(os.path.join(home_path, 'bolha_configuration.yaml'), 'r') as f:
        config_data = yaml.load(f)

    start_urls = config_data['urls']

    def parse(self, response):
        items = response.xpath('//*[text() = "Oglasi na bolha.com"]/following-sibling::ul/li[@data-href]')
        for item in items:
            yield {
                'url': response.urljoin(item.attrib['data-href']),
                'price': item.xpath('.//li[@class="price-item"]/strong//text()').get().strip(),
            }

        next_page = response.xpath('//a[@class="Pagination-link"][text() = "Naslednja\xa0"]')
        if next_page:
            yield response.follow(next_page.attrib['href'], callback=self.parse)


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())

    process.crawl('bolha')
    process.start()  # the script will block here until the crawling is finished
