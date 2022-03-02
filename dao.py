from mysql.connector import pooling

from mysql.connector import Error

from entity import Attraction


class MysqlUtil:
    __conn_pool = None

    def __init__(self):
        self.__conn = None
        self.__cursor = None

    def connect(self):
        if not self.__conn_pool:
            try:
                self.__conn_pool = pooling.MySQLConnectionPool(
                    pool_name="pynative_pool",
                    pool_size=5,
                    pool_reset_session=True,
                    host='localhost',
                    database='website',
                    user='root',
                    password='abc123'
                )
            except Error as e:
                print(e)

        self.__conn = self.__conn_pool.get_connection()
        if self.__conn.is_connected():
            return self.__conn

    @property
    def conn(self):
        return self.__conn

    @property
    def cursor(self):
        return self.__cursor

    def create_cursor(self):
        conn = self.connect()
        try:
            self.__cursor = conn.cursor(dictionary=True)
        except Error as e:
            print(e)

        return self.__cursor

    def disconnect(self):
        if self.__cursor is not None:
            self.__cursor.close()
        if self.__conn.is_connected():
            self.__conn.close()


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
            finally:
                self.__util.disconnect()

    def get_attractions_info(self, page, keyword='') -> tuple[int, list]:
        """每頁12筆資料，多取一筆判斷是否還有下一頁"""
        next_page = page + 1
        attraction_lst = []
        try:
            self.__util.create_cursor()
            if not keyword:
                sql = """
                select * from attractions
                limit %s, 13
                """
                self.__util.cursor.execute(sql, (page*12,))
                print('step1')
            else:
                sql = """
                select * from attractions
                where name REGEXP CONCAT(%s, '')
                limit %s, 13
                """
                self.__util.cursor.execute(sql, (keyword, page*12))

            while True:
                res = self.__util.cursor.fetchone()
                if not res:
                    break
                attraction = Attraction(_id=res['id'], name=res['name'], category=res['category'],
                                        description=res['description'], address=res['address'],
                                        transport=res['transport'], mrt=res['mrt'], latitude=res['latitude'],
                                        longitude=res['longitude'])
                attraction_lst.append(attraction)

        except Error as e:
            print(e)
            raise

        finally:
            self.__util.disconnect()
            if len(attraction_lst) < 13:
                next_page = None
            return next_page, attraction_lst

    def append_attractions_images(self, attractions_lst: list[Attraction]):
        """將景點列表附加圖片url訊息"""
        try:
            self.__util.create_cursor()
            for attraction in attractions_lst:
                attraction.images = []
                attractions_name = attraction.name

                sql = """
                select url from attractions_images
                where attractions_name = %s
                """

                self.__util.cursor.execute(sql, (attractions_name,))

                while True:
                    # 對每個attraction附加圖片資訊
                    res = self.__util.cursor.fetchone()
                    if not res:
                        break
                    attraction.images.append(res['url'])

        except Error as e:
            print(e)
            raise

        finally:
            self.__util.disconnect()

    def get_attraction_by_id(self, attractionId):
        attraction = None
        try:
            self.__util.create_cursor()

            sql = """
            select * from attractions
            where id = %s
            """
            self.__util.cursor.execute(sql, (attractionId,))

            res = self.__util.cursor.fetchone()

            attraction = Attraction(_id=res['id'], name=res['name'], category=res['category'],
                                    description=res['description'], address=res['address'],
                                    transport=res['transport'], mrt=res['mrt'], latitude=res['latitude'],
                                    longitude=res['longitude'])

        except Error as e:
            print(e)
            raise

        finally:
            self.__util.disconnect()
            # print(attraction.name)
            return attraction



def main():
    attractionDao = AttractionDao()
    # res = attractionDao.get_attractions_info(page=0, keyword='新北投溫泉區')
    # res = attractionDao.get_attractions_info(page=1)
    # print(res)
    # res = attractionDao.get_attractions_info(page=0, keyword='新北投溫泉區')
    # attractionDao.append_attractions_images(res[1])
    attractionDao.get_attraction_by_id(5)


if __name__ == "__main__":
    main()

