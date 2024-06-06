from flask import Blueprint, request, jsonify, current_app
import requests
import json
import os
import urllib.parse
import time

fetch_service = Blueprint('fetch_service', __name__)

# 전역 변수 설정
pangyo = "127.11115550000015,37.395263800000095,placeid=20543619,name=7YyQ6rWQ7JetIOyLoOu2hOuLueyEoA"

@fetch_service.route('/api/search', methods=['GET'])
def proxy_search():
    query = urllib.parse.quote(request.args.get('query'))
    type_ = request.args.get('type')
    searchCoord = request.args.get('searchCoord')
    boundary = request.args.get('boundary')

    url = f"https://map.naver.com/p/api/search/allSearch?query={query}&type={type_}&searchCoord={searchCoord}&boundary={boundary}"

    time.sleep(5)
    response = requests.get(url)
    
    # 로그 추가: 상태 코드와 응답 본문 출력
    print(f"API URL: {url}")
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")

    # JSON 응답 파싱
    try:
        api_data = response.json()
    except requests.exceptions.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return jsonify({"error": "Failed to decode JSON response from API", "response_text": response.text}), 500

    # Check if correction is null
    if api_data.get('result', {}).get('metaInfo', {}).get('correction') is None:
        print("Correction is null, skipping to next query.")
        return None

    # Get the first result's id
    matching_ids = []
    first_result = api_data.get('result', {}).get('place', {}).get('list', [])
    if first_result:
        matching_ids.append(first_result[0].get('id'))

    summary_data = None
    directions_data = None
    summary_json = []
    if matching_ids:
        top_matching_id = matching_ids[0]
        summary_url = f"https://map.naver.com/p/api/place/summary/{top_matching_id}"
        time.sleep(5)
        summary_response = requests.get(summary_url)
        
        # 로그 추가: 상태 코드와 응답 본문 출력
        print(f"Summary API URL: {summary_url}")
        print(f"Summary Response Status Code: {summary_response.status_code}")
        print(f"Summary Response Text: {summary_response.text}")
        
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
                time.sleep(5)
                directions_response = requests.get(directions_url, params=directions_params)
                
                # 로그 추가: 상태 코드와 응답 본문 출력
                print(f"Directions API URL: {directions_url}")
                print(f"Directions Response Status Code: {directions_response.status_code}")
                print(f"Directions Response Text: {directions_response.text}")
                
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

    return jsonify({
        "matching_ids": matching_ids,
        "api_data": api_data,
        "summary_data": summary_data,
        "directions_data": directions_data,
        "summary_json": summary_json
    })

@fetch_service.route('/api/process_queries', methods=['GET'])
def process_queries():
    apartment_file_path = os.path.join(current_app.root_path, 'static', 'data', 'apartment.json')
    with open(apartment_file_path, 'r', encoding='utf-8') as file:
        apartment_data = json.load(file)

    limit = request.args.get('limit')
    if limit == 'all':
        queries = [apartment['address'] for apartment in apartment_data]
    else:
        limit = int(limit)
        queries = [apartment['address'] for apartment in apartment_data[:limit]]

    results = []
    errors = []

    for query in queries:
        try:
            encoded_query = urllib.parse.quote(query)
            api_url = f"{request.host_url}api/search?query={encoded_query}&type=all&searchCoord=&boundary="
            api_response = requests.get(api_url)
            
            # 로그 추가: 상태 코드와 응답 본문 출력
            print(f"Query API URL: {api_url}")
            print(f"Query Response Status Code: {api_response.status_code}")
            print(f"Query Response Text: {api_response.text}")
            
            if api_response.ok:
                api_result = api_response.json()
                if api_result is not None:
                    results.append(api_result)
                else:
                    print(f"Skipped query {query} due to null correction.")
            else:
                errors.append(query)
        except Exception as e:
            print(f"Exception occurred: {e}")
            errors.append(query)

        

    summary_json = [result['summary_json'] for result in results if 'summary_json' in result]

    return jsonify({
        "summary_json": summary_json,
        "errors": errors
    })
