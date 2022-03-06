from mysql.connector import Error

from dao.tool import MysqlUtil
from entity import Attraction





class AttractionDao:
    """景點與資料庫互動工具"""
    def __init__(self):
        self.__util = MysqlUtil()
        self.__table = False

    def _create_table(self):
        try:
            self.__util.create_cursor()
            sql = """
            CREATE TABLE IF NOT EXISTS attractions(
                        id BIGINT PRIMARY KEY AUTO_INCREMENT,
                        `name` VARCHAR(255) NOT NULL UNIQUE,
                        category VARCHAR(255),
                        `description` TEXT,
                        address VARCHAR(255),
                        transport TEXT,
                        mrt VARCHAR(255),
                        latitude DOUBLE,
                        longitude DOUBLE,
                        `create_time` DATETIME NOT NULL DEFAULT NOW()
                    )
            """
            self.__util.create_cursor()
            self.__util.cursor.execute(sql)
            self.__util.conn.commit()

            sql = """
            CREATE TABLE IF NOT EXISTS attractions_images(
                        id BIGINT PRIMARY KEY AUTO_INCREMENT,
                        `attractions_name` VARCHAR(255) NOT NULL,
                        url VARCHAR(255),
                        `create_time` DATETIME NOT NULL DEFAULT NOW(),
                        FOREIGN KEY (attractions_name) references attractions(`name`) ON UPDATE CASCADE ON DELETE RESTRICT
                    )
            """
            self.__util.create_cursor()
            self.__util.cursor.execute(sql)
            self.__util.conn.commit()
        except Error as e:
            print(e)
            raise

        finally:
            self.__util.disconnect()
            self.__table = True

    def init_data(self, attractions: list[Attraction]):
        if not self.__table:
            self._create_table()
        for attraction in attractions:
            try:
                self.__util.create_cursor()
                sql = """INSERT INTO attractions(name, category, description, address, transport, mrt, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

                new_data = (attraction.name, attraction.category, attraction.description,
                            attraction.address, attraction.transport, attraction.mrt,
                            attraction.latitude, attraction.longitude)
                self.__util.cursor.execute(sql, new_data)
                self.__util.conn.commit()
                for image in attraction.images:
                    sql = """INSERT INTO attractions_images(attractions_name, url) values (%s, %s)"""
                    new_data = (attraction.name, image)
                    self.__util.cursor.execute(sql, new_data)
                    self.__util.conn.commit()
            except Error as e:
                print(e)
                raise

            finally:
                self.__util.disconnect()

    def get_attractions_info(self, page, keyword='') -> tuple[int, list]:
        """每頁12筆資料，多取一筆判斷是否還有下一頁"""
        next_page = page + 1
        attraction_lst = []

        with self.__util as cursor:
            if not keyword:
                sql = """
                select * from attractions
                limit %s, 13
                """
                cursor.execute(sql, (page*12,))

            else:
                sql = """
                select * from attractions
                where name REGEXP CONCAT(%s, '')
                limit %s, 13
                """

                cursor.execute(sql, (keyword, page*12))

            while True:
                res = cursor.fetchone()
                if not res:
                    break
                attraction = Attraction(_id=res['id'], name=res['name'], category=res['category'],
                                        description=res['description'], address=res['address'],
                                        transport=res['transport'], mrt=res['mrt'], latitude=res['latitude'],
                                        longitude=res['longitude'])
                attraction_lst.append(attraction)

            if len(attraction_lst) < 13:
                next_page = None
            return next_page, attraction_lst

    def get_attractions_info_with_images(self, page, keyword='') -> tuple[int, list]:
        """取得景點訊息，每頁12筆資料，多取一筆判斷是否還有下一頁"""
        next_page = page + 1
        attraction_lst = []

        with self.__util as cursor:
            if not keyword:
                sql = """
                        SELECT attr.*, images.url
                        FROM attractions_images AS images
                        JOIN (SELECT * FROM attractions LIMIT %s, 13) AS attr
                        ON images.`attractions_name` = attr.`name`;
                        """
                cursor.execute(sql, (page*12,))

            else:
                sql = """
                        SELECT attr.*, images.url
                        FROM attractions_images AS images
                        JOIN (SELECT * FROM attractions WHERE `name` 
                              REGEXP CONCAT(%s, '') LIMIT %s, 13) AS attr
                        ON images.`attractions_name` = attr.`name`;
                        """
                cursor.execute(sql, (keyword, page*12))

            while True:
                res = cursor.fetchone()

                if not res:
                    break
                attraction = Attraction(_id=res['id'], name=res['name'], category=res['category'],
                                        description=res['description'], address=res['address'],
                                        transport=res['transport'], mrt=res['mrt'], latitude=res['latitude'],
                                        longitude=res['longitude'], images=res['url'])
                attraction_lst.append(attraction)

            self.organize_attractions_list(attraction_lst)

            if len(attraction_lst) < 13:
                next_page = None
            return next_page, attraction_lst

    def organize_attractions_list(self, attraction_list: list[Attraction]) -> None:
        """整理數據，去除重複資訊"""
        # images_dict = {}
        # for attraction in attraction_list:
        #     name = attraction.name
        #     if images_dict.get(name, ''):
        #         images_dict[name].append(attraction.images)
        #     else:
        #         images_dict[name] = [attraction.images]
        #
        # name_list = []
        # for index in range(len(attraction_list)-1, -1, -1):
        #     # 去除重複的景點
        #     name = attraction_list[index].name
        #     if name not in name_list:
        #         name_list.append(name)
        #     else:
        #         del attraction_list[index]
        #
        # for attraction in attraction_list:
        #     name = attraction.name
        #     attraction.images = images_dict[name]

        images_dict = {}
        for index in range(len(attraction_list) - 1, -1, -1):
            # 小技巧: 一定要倒著循環列表，index才不會有問題
            name = attraction_list[index].name
            if images_dict.get(name, ''):
                # 添加每個景點列表的圖片url訊息
                images_dict[name].images.append(attraction_list[index].images)
                del attraction_list[index]
            else:
                # 初始化每個景點url列表，將找到 '第一個名稱為name' 的物件當作景點代表
                attraction_list[index].images = [attraction_list[index].images]
                # dict: (key, value) = (name, Attraction)
                images_dict[name] = attraction_list[index]

    def append_attractions_images(self, attractions_lst: list[Attraction]):
        """將景點列表附加圖片url訊息"""
        with self.__util as cursor:
            for attraction in attractions_lst:
                attraction.images = []
                attractions_name = attraction.name

                sql = """
                select url from attractions_images
                where attractions_name = %s
                """

                cursor.execute(sql, (attractions_name,))

                while True:
                    # 對每個attraction附加圖片資訊
                    res = cursor.fetchone()
                    if not res:
                        break
                    attraction.images.append(res['url'])

    def get_attraction_by_id(self, attractionId):
        attraction = None

        with self.__util as cursor:
            sql = """
                        select * from attractions
                        where id = %s
                        """
            cursor.execute(sql, (attractionId,))

            res = self.__util.cursor.fetchone()

            attraction = Attraction(_id=res['id'], name=res['name'], category=res['category'],
                                    description=res['description'], address=res['address'],
                                    transport=res['transport'], mrt=res['mrt'], latitude=res['latitude'],
                                    longitude=res['longitude'])
            # raise ValueError("create error")
            return attraction

    def get_attraction_by_id_with_images(self, attractionId):
        attraction_lst = []

        with self.__util as cursor:
            sql = """
                    SELECT attr.*, images.url
                    FROM attractions_images AS images
                    JOIN (SELECT * FROM attractions WHERE id = %s) AS attr
                    ON images.`attractions_name` = attr.`name`;
                    """
            cursor.execute(sql, (attractionId,))

            while True:
                res = cursor.fetchone()
                if not res:
                    break
                attraction = Attraction(_id=res['id'], name=res['name'], category=res['category'],
                                        description=res['description'], address=res['address'],
                                        transport=res['transport'], mrt=res['mrt'], latitude=res['latitude'],
                                        longitude=res['longitude'], images=res['url'])
                attraction_lst.append(attraction)

            self.organize_attractions_list(attraction_lst)
            attraction = attraction_lst.pop()
            # raise ValueError("create error")
            return attraction


def main():
    attractionDao = AttractionDao()
    # res = attractionDao.get_attractions_info(page=0, keyword='新北投溫泉區')
    # res = attractionDao.get_attractions_info(page=1)
    # res = attractionDao.get_attractions_info_with_images(page=0, keyword='新北投溫泉區')
    # res = attractionDao.get_attractions_info_with_images(page=0)
    # print(res)
    # print(res)
    # res = attractionDao.get_attractions_info(page=0, keyword='新北投溫泉區')
    # attractionDao.append_attractions_images(res[1])
    res = attractionDao.get_attraction_by_id_with_images(1)
    print(res.__dict__)


if __name__ == "__main__":
    main()

