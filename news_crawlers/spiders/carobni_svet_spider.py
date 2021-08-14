"""
Spider for carobni-svet.com
"""

import os
from typing import List

import yaml
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class CarobniSvetSpider(scrapy.Spider):
    """
    Spider for carobni-svet.com
    """

    # 'parse' method does not have to be overriden here
    # pylint: disable=abstract-method

    name = "carobni_svet"
    home_path = os.environ.get('NEWS_CRAWLERS_HOME', os.path.dirname(__file__))

    # get configuration data
    with open(os.path.join(home_path, 'carobni_svet_configuration.yaml'), 'r') as f:
        config_data = yaml.safe_load(f)

    def start_requests(self) -> List[scrapy.http.FormRequest]:
        """
        Starts requests for crawling. First request needs to enter the login page.

        :return: List of requests for further crawling.
        """
        return [scrapy.http.FormRequest(
            url=self.config_data['urls']['login'],
            formdata={
                'email': os.environ.get('EMAIL_USER'),
                'password': os.environ.get('CS_PASS')
            },
            callback=self.open_images
        )]

    def open_images(self, response) -> scrapy.Request:
        """
        Opens images page.

        :return: Request for further crawling.
        """
        # with login complete, access photo library
        return scrapy.Request(url=self.config_data['urls']['photos'], callback=self.get_images)

    def get_images(self, response):
        """
        Yields crawled data for images - URL for each image
        """
        # get all image items in 'galerija'
        image_items = response.xpath('//div[@id="galerija"]/a')

        for item in image_items:
            yield {
                'type': "image",
                'url': item.attrib['href']
            }

        yield scrapy.Request(url=self.config_data['urls']['blog'], callback=self.get_blog, dont_filter=True)

    @staticmethod
    def get_blog(response):
        """
        Yields crawled data for blog - ID (title) of each blog entry
        """
        # get all blog items
        blog_items = response.xpath('//div[@id="blogs"]/*')

        for item in blog_items:
            yield {
                'type': "blog",
                'url': item.attrib['id']
            }


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())

    process.crawl('carobni_svet')
    process.start()  # the script will block here until the crawling is finished
