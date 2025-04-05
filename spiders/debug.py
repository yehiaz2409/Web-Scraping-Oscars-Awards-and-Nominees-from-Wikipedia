import scrapy

class DebugCastSpider(scrapy.Spider):
    name = "debug_cast"

    def start_requests(self):
        yield scrapy.Request(
            url="https://en.wikipedia.org/wiki/Oppenheimer_(film)",
            callback=self.parse
        )

    def parse(self, response):
        # Grab the "Starring" row from the infobox
        cast_list = response.xpath(
            '//table[contains(@class, "infobox")]//tr[th[contains(text(), "Starring")]]/td//li'
        )

        if not cast_list:
            self.logger.warning("No starring list found.")
            return

        for li in cast_list:
            actor = li.xpath('.//a/text()').get()
            actor_url = li.xpath('.//a/@href').get()
            self.logger.info(f"ACTOR: {actor} | URL: {response.urljoin(actor_url) if actor_url else None}")