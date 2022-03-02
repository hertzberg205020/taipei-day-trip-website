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
            res = self.attractionDao.get_attractions_info(page, keyword)  # 返回tuple: (下一頁, 查詢結果列表: list[dict])
            self.attractionDao.append_attractions_images(res[1])  # 添加景點圖片url
        except Exception as e:
            raise

        # 能到這裡表示io沒有異常，表示數據可以拿到
        nextPage = res[0]
        # print(nextPage)
        data = []
        # 僅拿12筆資料
        i = 0
        for attraction in res[1]:
            if i == 12:
                break
            data.append(attraction.__dict__)
            i += 1
        # print({
        #     'nextPage': nextPage,
        #     'data': data
        # })
        return {
            'nextPage': nextPage,
            'data': data
        }

    # def get_attractions_info(self, page, keyword) -> tuple[int, list]:
    #     try:
    #         res = self.attractionDao.get_attractions_info(page, keyword)
    #     except Exception as e:
    #         raise
    #     return res

    # def append_attractions_images(self, attractions_lst) -> None:
    #     try:
    #         self.attractionDao.append_attractions_images(attractions_lst)
    #     except Exception as e:
    #         raise

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

