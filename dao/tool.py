from mysql.connector import pooling

from mysql.connector import Error


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
                print('connect', e)
                raise

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
        try:
            conn = self.connect()
            self.__cursor = conn.cursor(dictionary=True)
        except Error as e:
            print('create_cursor', e)
            raise

        return self.__cursor

    def disconnect(self):
        if self.__cursor is not None:
            self.__cursor.close()
        if self.__conn.is_connected():
            self.__conn.close()

    def __enter__(self):
        return self.create_cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # clean up code ...
        self.disconnect()
        if exc_tb:
            print(exc_type, exc_val)
            return False
        return True