"""parse json data"""
import json
from pathlib import Path

from dao import AttractionDao
from entity import Attraction


def get_data(path: str) -> list[dict]:
    """解析json格式的檔案"""
    path = Path(path)
    with open(path, 'r', encoding='utf-8') as jsonfile:
        raw_data = json.load(jsonfile)
        return raw_data['result']['results']


def get_images(images_str: str) -> list[str]:
    images_lst = images_str.split('https')
    ret = []
    ext = (".jpg", "png")
    for image in images_lst:
        if image.lower().endswith(ext):
            ret.append("https" + image)

    return ret


def parse_attractions(attractions: list[dict]) -> list[Attraction]:
    """解析景點資訊"""
    ret = []
    for attraction in attractions:
        _id = attraction.get('_id', '')
        name = attraction.get('stitle', '')
        # category = ' '.join([attraction.get('CAT1', ''), attraction.get('CAT2', '')])
        category = attraction.get('CAT2', '')
        description = attraction.get('xbody', '')
        address = attraction.get('address', '')
        transport = attraction.get('info', '')
        mrt = attraction.get('MRT', '')
        latitude = float(attraction.get('latitude', ''))
        longitude = float(attraction.get('longitude', ''))
        images = get_images(attraction.get('file', ''))
        attraction_obj = Attraction(_id=_id, name=name, category=category,
                                    description=description,
                                    address=address, transport=transport, mrt=mrt,
                                    latitude=latitude, longitude=longitude, images=images)

        ret.append(attraction_obj)

    return ret


def main():
    data = get_data('taipei-attractions.json')
    attraction_dao = AttractionDao()
    attractions = parse_attractions(data)
    attraction_dao.init_data(attractions)


if __name__ == "__main__":
    main()


