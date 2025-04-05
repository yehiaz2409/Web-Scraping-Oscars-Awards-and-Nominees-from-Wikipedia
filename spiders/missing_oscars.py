import scrapy
import re


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


class NominationsMissingSpider(scrapy.Spider):
    name = "nominations_missing"
    allowed_domains = ["en.wikipedia.org"]
    start_urls = [
        f"https://en.wikipedia.org/wiki/{i}{'th' if 10 <= i % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(i % 10, 'th')}_Academy_Awards"
        for i in range(18, 50)
    ]

    def parse(self, response):
        self.logger.info(f"Parsing page: {response.url}")

        match = re.search(r'(\d+)(?:st|nd|rd|th)_Academy_Awards', response.url)
        iteration = int(match.group(1)) if match else None

        tables = response.xpath('//table[contains(@class, "wikitable")]')

        for table in tables:
            rows = table.xpath('.//tr')
            current_categories = []

            for row in rows:
                headers = row.xpath('./th')
                if headers:
                    current_categories = []
                    for header in headers:
                        cat_text = header.xpath('.//a[not(contains(@class, "image"))]/text()').get()
                        if not cat_text:
                            cat_text = header.xpath('string(.)').get()
                        cat_text = cat_text.strip() if cat_text else None
                        if cat_text:
                            current_categories.append(cat_text)
                    continue

                cells = row.xpath('./td')
                if not cells or not current_categories:
                    continue

                for i, cell in enumerate(cells):
                    if i >= len(current_categories):
                        continue
                    category = current_categories[i]
                    nominee_kind = category_type(category)

                    for entry in cell.xpath('.//li | .//a[not(ancestor::li)]'):
                        is_winner = bool(entry.xpath('.//b | self::b'))

                        # MOVIE
                        movie_name = entry.xpath('.//i/a/text() | .//a[ancestor::i]/text()').get()
                        movie_url = entry.xpath('.//i/a/@href | .//a[ancestor::i]/@href').get()

                        if not movie_name:
                            movie_name = entry.xpath('.//i[not(a)]/text()').get()
                        if movie_url:
                            movie_url = response.urljoin(movie_url)

                        # PERSON
                        person_name = entry.xpath('.//a[not(ancestor::i)]/text()').get()
                        person_url = entry.xpath('.//a[not(ancestor::i)]/@href').get()
                        if person_url:
                            person_url = response.urljoin(person_url)

                        # fallback parsing from text
                        if not person_name:
                            full_text = entry.xpath('string(.)').get()
                            if full_text and '–' in full_text:
                                person_part = full_text.split('–', 1)[1]
                                person_name = person_part.split('(')[0].strip()

                        if "International Feature Film" in category:
                            if movie_name:
                                yield {
                                    "iteration": iteration,
                                    "category": category,
                                    "nominee": movie_name,
                                    "movies": [],
                                    "is_winner": is_winner,
                                    "person": False,
                                    "nominee_urls": [movie_url] if movie_url else [],
                                    "movies_urls": []
                                }
                            continue

                        if nominee_kind == "movie":
                            if movie_name:
                                yield {
                                    "iteration": iteration,
                                    "category": category,
                                    "nominee": movie_name,
                                    "movies": [],
                                    "is_winner": is_winner,
                                    "person": False,
                                    "nominee_urls": [movie_url] if movie_url else [],
                                    "movies_urls": []
                                }

                        elif nominee_kind in ("person", "direct"):
                            if person_name:
                                yield {
                                    "iteration": iteration,
                                    "category": category,
                                    "nominee": person_name,
                                    "movies": [movie_name] if movie_name else [],
                                    "is_winner": is_winner,
                                    "person": True,
                                    "nominee_urls": person_url if person_url else None,
                                    "movies_urls": [movie_url] if movie_url else []
                                }