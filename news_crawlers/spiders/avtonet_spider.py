"""
Spider for avto.net
"""

import os

import scrapy
import yaml
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class AvtoNetSpider(scrapy.Spider):
    """
    Spider for avto.net
    """

    name = "avtonet"
    home_path = os.environ.get("NEWS_CRAWLERS_HOME", os.path.dirname(__file__))

    # get configuration data
    with open(os.path.join(home_path, "avtonet_configuration.yaml")) as f:
        config_data = yaml.safe_load(f)

    def start_requests(self):
        for query, url in self.config_data["urls"].items():
            yield scrapy.Request(
                url=url, callback=self.parse, cb_kwargs={"query": query}
            )

    def parse(self, response, **kwargs):
        items = response.xpath('//form[@name="results"]/div[a]')
        for item in items:
            yield {
                "query": kwargs["query"],
                "url": response.urljoin(item.xpath("./a").attrib["href"]),
                "title": item.xpath(
                    './div[contains(@class, "GO-Results-Naziv")]/span/text()'
                ).get(),
                "data": self._get_car_data_from_table_rows(
                    item.xpath(
                        './/div[contains(@class, "GO-Results-Data")]'
                        '/div[@class="GO-Results-Data-Top"]'
                        "/table/tbody/tr"
                    )
                ),
                "price": item.xpath(
                    '(.//div[@class="GO-Results-Price-TXT-Regular"] | '
                    './/div[@class="GO-Results-Price-TXT-Akcija"])/text()'
                ).get(),
            }

        next_page = response.xpath('//a[@class="page-link"][span[text()="Naprej"]]')
        if next_page:
            yield response.follow(
                next_page.attrib["href"], cb_kwargs={"query": kwargs["query"]}
            )

    @staticmethod
    def _get_car_data_from_table_rows(tr_selectors) -> str:
        """
        Returns car data from crawled table.

        :return: Car data as a string, where each line is in a form "key: value".
        """
        out_data = dict()
        for tr_selector in tr_selectors:
            td_key, td_value = tr_selector.xpath(".//td/text()").getall()
            out_data[td_key] = td_value.strip()

        return "\n".join([f"{key}: {value}" for key, value in out_data.items()])


if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())

    process.crawl("avtonet")
    process.start()  # the script will block here until the crawling is finished
