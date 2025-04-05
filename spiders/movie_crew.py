import scrapy
import json
import datetime
import re

class MovieCrewSpider(scrapy.Spider):
    name = "movie_crew"

    def start_requests(self):
        with open("final_movies.json") as f:
            movies = json.load(f)

        for movie in movies:
            url = movie.get("movie_url")
            if url:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_cast,
                    meta={
                        "movie_name": movie["movie_name"],
                        "release_date": movie["release_date"],
                        "director_name": movie.get("director_name"),
                        "director_birth_date": movie.get("director_birth_date")
                    }
                )
    def extract_date(self, response, label):
        # date = response.xpath(
        #     f"//tr[th[contains(text(), '{label}')]]/td/span[@class='bday' or @class='dday']/text()"
        # ).get()

        # if not date:
        #     date_texts = response.xpath(
        #         f"//tr[th[contains(text(), '{label}')]]/td//text()[not(parent::sup)]"
        #     ).getall()
        #     date_texts = [text.strip() for text in date_texts if text.strip()]
        #     date_texts = [re.sub(r"\[\d+\]", "", text) for text in date_texts]
        #     date_texts = [text for text in date_texts if text not in ["(", ")", "[", "]"]]

        #     months = {
        #         "January", "February", "March", "April", "May", "June",
        #         "July", "August", "September", "October", "November", "December"
        #     }

        #     if date_texts:
        #         first_word = date_texts[0].split()[0]
        #         if first_word in months:
        #             date = date_texts[0]
        #         elif len(date_texts) > 1 and date_texts[1].split()[0] in months:
        #             date = date_texts[1]
        #         elif len(date_texts) >= 2:
        #             date = date_texts[2]
        date_of_birth = response.xpath('//span[@class="bday"]/text()').get()
        if not date_of_birth:
            # Fallback: look for a 4-digit year in the "Born" section
            born_text = response.xpath('//th[text()="Born"]/following-sibling::td[1]//text()').getall()
            born_text = " ".join(born_text)
            year_match = re.search(r'\b(1[89]\d{2}|20\d{2})\b', born_text)  # match 1800–2099
            if year_match:
                date_of_birth = f"{year_match.group(1)}-01-01"  # approximate as Jan 1date_of_birth = response.xpath('//span[@class="bday"]/text()').get()

        # return self.format_date_for_sql(date) if date else "N/A"
        return date_of_birth

    def format_date_for_sql(self, date_str):
        formats = ["%B %d, %Y", "%d %B %Y", "%Y-%m-%d"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
            except:
                continue
        return date_str  # fallback

    def parse_cast(self, response):
        # --- Extract Cast from Infobox ---
        cast_section = response.xpath('//table[contains(@class, "infobox")]//tr[th[contains(text(), "Starring")]]/td')

        for actor in cast_section.xpath('.//a'):
            actor_name = actor.xpath('text()').get()
            actor_url = actor.xpath('@href').get()
            if actor_name and actor_url:
                yield response.follow(
                    url=actor_url,
                    callback=self.parse_crew_dob,
                    meta={
                        "crew_name": actor_name,
                        "crew_role": "actor",
                        "movie_name": response.meta["movie_name"],
                        "movie_release_date": response.meta["release_date"],
                        "crew_url": actor_url
                    }
                )

        # --- Extract Producers from infobox ---
        producer_rows = response.xpath('//table[contains(@class, "infobox")]//tr[th[contains(text(), "Produced by")]]/td')

        for producer in producer_rows.xpath('.//a'):
            producer_name = producer.xpath('text()').get()
            producer_url = producer.xpath('@href').get()
            if producer_name and producer_url:
                yield response.follow(
                    url=producer_url,
                    callback=self.parse_crew_dob,
                    meta={
                        "crew_name": producer_name,
                        "crew_role": "producer",
                        "movie_name": response.meta["movie_name"],
                        "movie_release_date": response.meta["release_date"],
                        "crew_url": producer_url
                    }
                )

        # Director (from JSON)
        # --- Extract Director from Infobox ---
        director_row = response.xpath('//table[contains(@class, "infobox")]//tr[th[contains(text(), "Directed by")]]/td')
        director_link = director_row.xpath('.//a[1]')
        director_name = director_link.xpath('text()').get()
        director_url = director_link.xpath('@href').get()

        if director_name and director_url:
            yield response.follow(
                url=director_url,
                callback=self.parse_crew_dob,
                meta={
                    "crew_name": director_name,
                    "crew_role": "director",
                    "movie_name": response.meta["movie_name"],
                    "movie_release_date": response.meta["release_date"],
                    "crew_url": director_url
                }
            )

    def parse_crew_dob(self, response):
        dob = self.extract_date(response, "Born")
        # --- Date of Death ---
        death_date = response.xpath('//th[text()="Died"]/following-sibling::td//span[@class="dday"]/text()').get()
        if not death_date:
            died_text = response.xpath('//th[text()="Died"]/following-sibling::td[1]//text()').getall()
            died_text = " ".join(died_text)
            try:
                # Try parsing full date
                parsed = datetime.strptime(died_text.strip(), "%B %d, %Y")
                death_date = parsed.strftime("%Y-%m-%d")
            except:
                # Fallback: extract year only
                year_match = re.search(r'\b(1[89]\d{2}|20\d{2})\b', died_text)
                if year_match:
                    death_date = f"{year_match.group(1)}-01-01"
        # Try to get country from Nationality first
        # First try Nationality
        country = response.xpath('//th[text()="Nationality"]/following-sibling::td//text()').get()
        if country:
            country = country.strip()
        else:
            # Fallback to birthplace div
            birthplace_parts = response.xpath('//th[text()="Born"]/following-sibling::td//div[@class="birthplace"]//text()').getall()
            if birthplace_parts:
                country = birthplace_parts[-1].strip()
            else:
                country = None
        yield {
            "crew_name": response.meta["crew_name"],
            "crew_date_of_birth": dob,
            "crew_country": country,
            "crew_death_date": death_date.strip() if death_date else None,
            "crew_role": response.meta["crew_role"],
            "movie_name": response.meta["movie_name"],
            "movie_release_date": response.meta["movie_release_date"],
            "crew_url": response.meta["crew_url"]
        }
