from dao import AttractionDao
from entity import Attraction


class AttractionService:
    """景點相關的業務邏輯層"""
    def __init__(self):
        self.attractionDao = AttractionDao()

    def get_attractions(self, page, keyword):
        """每頁12筆資料"""
        res = None
        try:
            # res = self.attractionDao.get_attractions_info(page, keyword)  # 返回tuple: (下一頁, 查詢結果列表: list[dict])
            # self.attractionDao.append_attractions_images(res[1])  # 添加景點圖片url
            res = self.attractionDao.get_attractions_info_with_images(page, keyword)
        except Exception as e:
            raise

        # 能到這裡表示io沒有異常，表示數據可以拿到
        nextPage = res[0]
        attraction_list = res[1]
        data = []

        # 僅拿12筆資料
        # i = 0
        # for attraction in res[1]:
        #     if i == 12:
        #         break
        #     data.append(attraction.__dict__)
        #     i += 1

        for index in range(min(12, len(attraction_list))):
            data.append(attraction_list[index].__dict__)  # 將Attraction列表轉成dict列表

        return {
            'nextPage': nextPage,
            'data': data
        }

    def get_attraction_by_id(self, attractionId):
        """依景點編號搜尋景點訊息，若為空則回傳錯誤訊息"""
        try:
            res = [self.attractionDao.get_attraction_by_id(attractionId)]
            self.attractionDao.append_attractions_images(res)
        except Exception as e:
            raise

        ret = {
            "error": True,
            "message": "自訂的錯誤訊息"
        }

        if res[0]:  # 有找到景點訊息
            data = res[0].__dict__
            ret = {
                'data': data
            }

        return ret

    def get_attraction_by_id_with_images(self, attractionId):
        """依景點編號搜尋景點訊息，若為空則回傳錯誤訊息"""
        try:
            res = self.attractionDao.get_attraction_by_id_with_images(attractionId)
        except Exception as e:
            raise

        ret = {
            "error": True,
            "message": "自訂的錯誤訊息"
        }

        if res:  # 有找到景點訊息
            data = res.__dict__
            ret = {
                'data': data
            }

        return ret

