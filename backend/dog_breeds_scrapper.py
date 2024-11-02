import json
import asyncio
import aiohttp

import requests
import re
import tqdm
from bs4 import BeautifulSoup
from lxml import html


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

def export_dog_breeds_links():
    response = requests.request("GET", "https://wamiz.com/chiens/race-chien")

    soup = BeautifulSoup(response.text, 'html.parser')
    races = soup.find_all(class_="listView-item-title--homepageBreed")

    breeds_links = [race.get('href') for race in races if race.get('href')]

    return "https://wamiz.com", breeds_links


async def parse_dog_breed_data(session, root, link):
    response_content = await fetch(session, root + link)
    tree = html.fromstring(response_content)

    lifetime = tree.xpath("//table/tr/td/p")[1].text.strip()
    character = [c.tail.strip() for c in tree.xpath("//table/tr/td/ul/li/a/img")]
    size = tree.xpath("//table/tr/td/a/div")[0].text

    female = {
        "adult_size": tree.xpath("//table/tr/td/div/span")[1].text.strip(),
        "adult_weight": tree.xpath("//table/tr/td/div/span")[5].text.strip()
    }

    male = {
        "adult_size": tree.xpath("//table/tr/td/div/span")[3].text.strip(),
        "adult_weight": tree.xpath("//table/tr/td/div/span")[7].text.strip()
    }

    coat_colors_block = tree.xpath("//table/tr/td")[11]
    coat_colors = [cc.text.strip() for cc in coat_colors_block.xpath("a/span")]

    coat_type_block = tree.xpath("//table/tr/td")[13]
    coat_type = [ct.text.strip() for ct in coat_type_block.xpath("a/span")]
    eyes_color = tree.xpath("//table/tr/td/a/span")[0].text
    price = tree.xpath("//table/tr/td/p")[-1].text.strip()

    dog_breed = re.match(r'/chiens/([\w+-]+)-\d+', link).groups()[0]
    return dog_breed, {
        "lifetime": lifetime,
        "character": character,
        "size": size,
        "female": female,
        "male": male,
        "coat_colors": coat_colors,
        "coat_type": coat_type,
        "eyes_color": eyes_color,
        "price": price
    }


async def export_dog_breeds_data(root, links):
    dog_breeds_data = {}

    async with aiohttp.ClientSession() as session:
        tasks = [parse_dog_breed_data(session, root, link)
        for link in links]
        for future in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            dog_breed, data = await future
            dog_breeds_data[dog_breed] = data

    return dog_breeds_data


if __name__ == '__main__':
    root, links = export_dog_breeds_links()
    data = asyncio.run(export_dog_breeds_data(root, links))

    with open('resources/dog_breeds_data.json', 'w') as f:
        json.dump(data, f, indent=4)