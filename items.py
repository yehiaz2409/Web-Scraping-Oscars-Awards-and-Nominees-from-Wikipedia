# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Milestone2Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class MovieItem(scrapy.Item):
    movie_name = scrapy.Field()
    release_date = scrapy.Field()
    language = scrapy.Field()
    run_time = scrapy.Field()
    production_company = scrapy.Field()
    director_name = scrapy.Field()
    director_birthdate = scrapy.Field()

class CrewItem(scrapy.Item):
    name = scrapy.Field()
    date_of_birth = scrapy.Field()
    country = scrapy.Field()
    death_date = scrapy.Field()

class NominationItem(scrapy.Item):
    nom_id = scrapy.Field()
    iteration = scrapy.Field()
    cat_name = scrapy.Field()
    user_added = scrapy.Field()
    granted = scrapy.Field()
    num_of_votes = scrapy.Field()

class NominatedForItem(scrapy.Item):
    nom_id = scrapy.Field()
    iteration = scrapy.Field()
    movie_name = scrapy.Field()
    release_date = scrapy.Field()
    name = scrapy.Field()
    date_of_birth = scrapy.Field()