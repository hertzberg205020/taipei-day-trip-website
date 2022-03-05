from flask import Blueprint, request, jsonify

from service import AttractionService

bp = Blueprint("api", __name__, url_prefix='/api')

attractionService = AttractionService()


@bp.route('/attractions')
def get_attractions():
    page = int(request.args.get('page', ''))
    keyword = request.args.get('keyword', '')
    try:
        res = attractionService.get_attractions(page, keyword)
    except Exception as e:
        print(e)
        res = {
            "error": True,
            "message": "自訂的錯誤訊息"
        }
    return res


@bp.route('/attraction/<int:attractionId>')
def get_attraction_by_id(attractionId):
    ret = None
    try:
        # ret = attractionService.get_attraction_by_id(attractionId)
        ret = attractionService.get_attraction_by_id_with_images(attractionId)
    except Exception as e:
        print(e)
        ret = {
            "error": True,
            "message": "自訂的錯誤訊息"
        }

    return ret
