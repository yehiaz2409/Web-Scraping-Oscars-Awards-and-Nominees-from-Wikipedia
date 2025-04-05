import scrapy
import re
# from scrapy.linkextractors import LinkExtractor
# from ..items import MovieItem, CrewItem, NominationItem, NominatedForItem

def category_type(category: str) -> str:
    category = category.lower()

    if "picture" in category:
        return "movie"
    elif "actor" in category or "actress" in category:
        return "person"
    elif "director" in category or "directing" in category:
        return "direct"
    elif "writing" in category or "screenplay" in category or "story" in category:
        return "person"
    elif "cinematography" in category or "art direction" in category:
        return "person"
    elif "effects" in category or "sound" in category:
        return "person"
    else:
        return "direct"

class CrawlingSpider(scrapy.Spider):
    name = "nominations"
    allow_domains = ["en.wikipedia.org"]
    start_urls = [
    f"https://en.wikipedia.org/wiki/{i}{'th' if 10 <= i % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(i % 10, 'th')}_Academy_Awards"
    for i in range(1, 97)
]

    def parse(self, response):
        self.logger.info("Parsing started...")
        
        # Extract the iteration number (e.g., 1st, 2nd, ..., 96th)
        match = re.search(r'(\d+)(?:st|nd|rd|th)_Academy_Awards', response.url)
        if match:
            iteration = int(match.group(1))
        else:
            iteration = None  # fallback
        # Go through each category block
        for category_td in response.css('table.wikitable td'):
            # Extract category name
            category = category_td.css('div b a::text').get()
            self.logger.info(f"Processing category: {category}")
            self.logger.info(f"HTML snippet: {category_td.get()[:500]}")
            if not category:
                category = category_td.css('div b::text').get()
            if not category:
                continue

            nominee_kind = category_type(category)

            # Only get top-level nominees (winners)
            nominee_blocks = category_td.css('ul > li')

            # We only want to process the first <li> (the one containing winner + nested nominees)
            if not nominee_blocks:
                continue

            # 1. Winner block
            winner_block = nominee_blocks[0]

            # Winner
            # Special case for Best International Feature Film
            if "International Feature Film" in category:
                # Winner
                movie_name = winner_block.css('b i a::text').get()
                movie_url = winner_block.css('b i a::attr(href)').get()
                if movie_name:
                    yield {
                        "iteration": iteration,
                        "category": category,
                        "nominee": movie_name.strip(),
                        "movies": [],
                        "is_winner": True,
                        "person": False,
                        "nominee_urls": [response.urljoin(movie_url)] if movie_url else [],
                        "movies_urls": []
                    }

                # Other nominees
                for other in winner_block.css('ul > li'):
                    movie_name = other.css('i a::text').get()
                    movie_url = other.css('i a::attr(href)').get()
                    if movie_name:
                        yield {
                            "iteration": iteration,
                            "category": category,
                            "nominee": movie_name.strip(),
                            "movies": [],
                            "is_winner": False,
                            "person": False,
                            "nominee_urls": [response.urljoin(movie_url)] if movie_url else [],
                            "movies_urls": []
                        }
                continue  # Skip to next category
            if nominee_kind == "movie":
                winner_block = nominee_blocks[0]

                # Try getting movie from <b><i><a>
                movie_name = winner_block.css('b i a::text').get()
                movie_url = winner_block.css('b i a::attr(href)').get() or winner_block.css('i a::attr(href)').get()
                if not movie_name:
                    # Fallback to simpler <i><a>
                    movie_name = winner_block.css('i a::text').get()

                if movie_name:
                    yield {
                        "iteration": iteration,
                        "category": category,
                        "nominee": movie_name.strip(),
                        "movies": [],
                        "is_winner": True,
                        "person": False,
                        "nominee_urls": [response.urljoin(movie_url)] if movie_url else [],
                        "movies_urls": []
                    }

                # Other nominees
                for other in winner_block.css('ul > li'):
                    movie_name = other.css('i a::text').get()
                    movie_url = other.css('i a::attr(href)').get()
                    if movie_name:
                        yield {
                            "iteration": iteration,
                            "category": category,
                            "nominee": movie_name.strip(),
                            "movies": [],
                            "is_winner": False,
                            "person": False,
                            "nominee_urls": [response.urljoin(movie_url)] if movie_url else [],
                            "movies_urls": []
                        }

                continue
            if nominee_kind in ("person", "direct"):
                # Winner
                winner_name = winner_block.xpath('./b[1]/a[1]/text() | ./a[1]/text()').get()
                winner_href = winner_block.xpath('./b[1]/a[1]/@href | ./a[1]/@href').get()

                movie_name = winner_block.xpath('(./b/i/a | ./i/b/a | ./i/a)[1]/text()').get()
                movie_link = winner_block.xpath('(./b/i/a | ./i/b/a | ./i/a)[1]/@href').get()
                # # Fallback: if no movie names found, look for deeper patterns (e.g., Best Actress multiple films)
                # if not movie_names:
                #     movie_names = winner_block.xpath('./b/i/a/text()').getall()
                # if not movie_names:
                #     movie_names = winner_block.xpath('./i/a/text()').getall()
                if winner_name:
                    yield {
                        "iteration": iteration,
                        "category": category,
                        "nominee": winner_name.strip(),
                        "movies":  [movie_name.strip()] if movie_name else [],
                        "is_winner": True,
                        "person": True,
                        "nominee_urls": response.urljoin(winner_href) if winner_href else None,
                        "movies_urls": [response.urljoin(movie_link)] if movie_link else []
                    }

                # Nominees
                for other in winner_block.xpath('./ul/li'):
                    other_name = other.xpath('./a[1]/text()').get()
                    other_href = other.xpath('./a[1]/@href').get()
                    movie_name = other.xpath('(./i/a | ./i/b/a)[1]/text()').get()
                    movie_link = other.xpath('(./i/a | ./i/b/a)[1]/@href').get()
                    if other_name:
                        yield {
                            "iteration": iteration,
                            "category": category,
                            "nominee": other_name.strip(),
                            "movies": [movie_name.strip()] if movie_name else [],
                            "is_winner": False,
                            "person": True,
                            "nominee_urls": response.urljoin(other_href) if other_href else None,
                            "movies_urls": [response.urljoin(movie_link)] if movie_link else [],
                        }