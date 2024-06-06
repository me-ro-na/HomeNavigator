from flask import Blueprint, request, jsonify

search_service = Blueprint('search_service', __name__)

# 간단한 전역 변수로 검색 기록 저장 (예제용)
search_history = []

@search_service.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    if query:
        search_history.append(query)
        if len(search_history) > 10:  # 최근 검색 기록 10개로 제한
            search_history.pop(0)
    return jsonify({'status': 'success', 'search_history': search_history})
