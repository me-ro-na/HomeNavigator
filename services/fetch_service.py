from flask import Blueprint, request, jsonify, current_app
import requests
import json
import os

fetch_service = Blueprint('fetch_service', __name__)

# 전역 변수 설정
pangyo = "127.11115550000015,37.395263800000095,placeid=20543619,name=7YyQ6rWQ7JetIOyLoOu2hOuLueyEoA"

@fetch_service.route('/api/search', methods=['GET'])
def proxy_search():
    # Load local JSON file
    apartment_file_path = os.path.join(current_app.root_path, 'static', 'data', 'apartment.json')
    
    limit = request.args.get('limit')
    with open(apartment_file_path, 'r', encoding='utf-8') as file:
        apartment_data = json.load(file)
    if limit == 'all':
        queries = [apartment['address'] for apartment in apartment_data]
    else:
        limit = int(limit)
        queries = [apartment['address'] for apartment in apartment_data[:limit]]

    
    results = []
    for query in queries:
    # query = request.args.get('query')
        type_ = request.args.get('type')
        searchCoord = request.args.get('searchCoord')
        boundary = request.args.get('boundary')

        url = f"https://map.naver.com/p/api/search/allSearch?query={query}&type={type_}&searchCoord={searchCoord}&boundary={boundary}"
        response = requests.get(url)
        api_data = response.json()
        
        
        # Compare addresses and find matching id
        matching_ids = []
        
        print(f"api_data: {api_data}");
        first_result = api_data.get('result', {}).get('place', {}).get('list', [])
        if first_result:
            matching_ids.append(first_result[0].get('id'))
            
        # for api_place in api_data.get('result', {}).get('place', {}).get('list', []):
        #     api_address = api_place.get('address')
        #     for apartment in apartment_data:
        #         if api_address == apartment.get('address'):
        #             matching_ids.append(api_place.get('id'))

        summary_data = None
        directions_data = None
        summary_json = []
        if matching_ids:
            top_matching_id = matching_ids[0]
            summary_url = f"https://map.naver.com/p/api/place/summary/{top_matching_id}"
            summary_response = requests.get(summary_url)
            if summary_response.ok:
                summary_data = summary_response.json()
                route_url = summary_data.get('buttons', {}).get('route', '')
                if route_url:
                    # Extract parameters from route URL
                    params = {param.split('=')[0]: param.split('=')[1] for param in route_url.split('?')[1].split('&')}
                    ename = params.get('ename', '')
                    ex = params.get('ex', '')
                    ey = params.get('ey', '')
                    edid = params.get('edid', '')

                    # Create new variable a
                    a = f"{ex},{ey},placeid={edid},name={ename}"

                    # Create parameters for new API request
                    departure_time = "2024-05-29T07:00:00"
                    directions_params = {
                        "start": a,
                        "goal": pangyo,
                        "crs": "EPSG:4326",
                        "includeDetailOperation": True,
                        "lang": "ko",
                        "mode": "TIME",
                        "departureTime": departure_time
                    }

                    # Send new API request
                    directions_url = "https://map.naver.com/p/api/directions/pubtrans"
                    directions_response = requests.get(directions_url, params=directions_params)
                    if directions_response.ok:
                        directions_data = directions_response.json()
                        # Filter directions data where idx <= 5
                        for path in directions_data.get('paths', []):
                            if 1 <= path.get('idx') <= 5:
                                path_summary = {
                                    "idx": path.get("idx"),
                                    "total_duration": path.get("duration"),
                                    "legs": []
                                }
                                for leg in path.get("legs", []):
                                    steps = []
                                    for step in leg.get("steps", []):
                                        if step.get("type") == "WALKING":
                                            steps.append({
                                                "type": "WALKING",
                                                "duration": step.get("duration"),
                                                "distance": step.get("distance")
                                            })
                                        elif step.get("type") == "SUBWAY":
                                            routes = step.get("routes", [])[0] if step.get("routes", []) else {}
                                            stations = step.get("stations", [])
                                            steps.append({
                                                "type": "SUBWAY",
                                                "line": routes.get("name"),
                                                "departure_station": stations[0].get("displayName") if stations else "",
                                                "duration": step.get("duration"),
                                                "express": routes.get("operation", {}).get("name"),
                                                "station_count": len(stations) - 1,
                                                "arrival_station": stations[-1].get("displayName") if stations else ""
                                            })
                                        elif step.get("type") == "BUS":
                                            routes = step.get("routes", [])
                                            stations = step.get("stations", [])
                                            steps.append({
                                                "type": "BUS",
                                                "departure_station": stations[0].get("displayName") if stations else "",
                                                "bus_numbers": [route.get("longName") for route in routes],
                                                "arrival_station": stations[-1].get("displayName") if stations else "",
                                                "station_count": len(stations) - 1,
                                                "duration": step.get("duration"),
                                                "bus_types": [route.get("type", {}).get("name") for route in routes]
                                            })
                                    path_summary["legs"].append({"steps": steps})
                                summary_json.append(path_summary)
            results.append(summary_json)

    return jsonify({
        # "matching_ids": matching_ids,
        # "api_data": api_data,
        # "summary_data": summary_data,
        # "directions_data": directions_data,
        # "summary_json": summary_json
        "summary_json": results
    })
