import scrapy
import json
from datetime import datetime
import csv
import re

class MovieSpider(scrapy.Spider):
    name = "movies"

    def start_requests(self):
        with open("movies_with_urls_new.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            seen = set()
            for row in reader:
                movie = row["movie_name"]
                url = row["movie_url"]
                if url not in seen:
                    seen.add(url)
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_movie,
                        meta={
                            "movie_name": movie,
                            "movie_url": url
                        }
                    )

    def parse_movie(self, response):
        def extract_with_label(label_text):
            return response.xpath(f"//tr[th[contains(normalize-space(), '{label_text}')]]/td")

        movie_name = response.meta['movie_name']

        # --- Release Date ---
        release_date = response.css(
            "table.infobox.vevent th:contains('Release date') + td div.plainlist ul li::text"
        ).get()
        if not release_date:
            release_date = response.css(
                "table.infobox.vevent th:contains('Release date') + td::text"
            ).get()

        formatted_release_date = None
        if release_date:
            try:
                formatted_release_date = datetime.strptime(release_date.replace("\xa0", " ").strip(), "%B %d, %Y").strftime("%Y-%m-%d")
            except:
                try:
                    formatted_release_date = datetime.strptime(release_date.strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
                except:
                    formatted_release_date = None

        # --- Runtime ---
        run_time_text = extract_with_label("Running time").xpath("string(.)").get()
        run_time = None
        if run_time_text:
            match = re.search(r'\d+', run_time_text)
            if match:
                run_time = int(match.group(0))

        # --- Production Company ---
        production_companies = response.xpath(
            "//table[contains(@class, 'infobox vevent')]//tr[th/div[contains(text(), 'Production')]]/td//a/text()"
        ).getall()
        if not production_companies:
            production_companies = ["Unknown"]
        production_company = ', '.join(production_companies)

        # --- Language ---
        languages = response.xpath(
            "//table[contains(@class, 'infobox vevent')]//th[contains(text(), 'Language')]/following-sibling::td//text()"
        ).getall()
        languages = [lang.strip() for lang in languages if lang.strip()]
        language_text = ', '.join(languages) if languages else None

        # --- Director ---
        director = extract_with_label("Directed by")
        director_name = director.css("a::text").get()
        director_url = response.urljoin(director.css("a::attr(href)").get()) if director_name else None

        # if director_url:
        #     yield scrapy.Request(
        #         url=director_url,
        #         callback=self.parse_director_dob,
        #         meta={
        #             "movie_name": movie_name,
        #             "release_date": formatted_release_date,
        #             "language": language_text,
        #             "run_time": run_time,
        #             "production_company": production_company,
        #             "director_name": director_name,
        #             "director_url": director_url,
        #             "movie_url": response.meta["movie_url"]
        #         }
        #     )
        # else:
        yield {
            "movie_name": movie_name,
            "release_date": formatted_release_date,
            "language": language_text,
            "run_time": run_time,
            "production_company": production_company,
            "movie_url": response.meta["movie_url"]
        }

    def parse_director_dob(self, response):
        dob = response.xpath('//span[contains(@class, "bday")]/text()').get()

        if not dob:
            # Fallback 1: from "Born" row in infobox
            born_row = response.xpath('//th[contains(text(), "Born")]/following-sibling::td[1]')
            raw_texts = born_row.xpath(".//text()").getall()
            for text in raw_texts:
                text = text.strip()
                try:
                    parsed = datetime.strptime(text, "%B %d, %Y")
                    dob = parsed.strftime("%Y-%m-%d")
                    break
                except:
                    continue

        if not dob:
            # Fallback 2: from first paragraph
            para_texts = response.xpath('//p[1]//text()').getall()
            for text in para_texts:
                text = text.strip()
                try:
                    parsed = datetime.strptime(text, "%d %B %Y")
                    dob = parsed.strftime("%Y-%m-%d")
                    break
                except:
                    continue

        yield {
            "movie_name": response.meta['movie_name'],
            "release_date": response.meta['release_date'],
            "language": response.meta['language'],
            "run_time": response.meta['run_time'],
            "production_company": response.meta['production_company'],
            "movie_url": response.meta['movie_url']
        }