import requests
import pandas as pd
from datetime import datetime, timedelta
from models import db, Graph, DataPoint

def fetch_oura_data(token, start_date_str, end_date_str):
    url = 'https://api.ouraring.com/v2/usercollection/sleep'
    headers = {'Authorization': f'Bearer {token}'}

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    all_data = []
    chunk_start = start_date

    while chunk_start <= end_date:
        chunk_end = min(chunk_start + timedelta(days=29), end_date)
        params = {
            'start_date': chunk_start.isoformat(),
            'end_date': chunk_end.isoformat()
        }
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            all_data.append(response.json())
        elif response.status_code == 401:
            raise Exception("Invalid Oura API token. Please check your API token and try again.")
        else:
            raise Exception(f"Oura API request failed with status {response.status_code}: {response.text}")

        chunk_start = chunk_end + timedelta(days=1)

    return all_data

def flatten_oura_chunks(list_of_chunks):
    """
    Takes a list of chunk dicts, each like:
      { "data": [ {sleep_record_1}, {sleep_record_2}, ...] }
    Returns a single list of all sleep records.
    """
    all_records = []
    for chunk in list_of_chunks:
        # chunk might look like {"data": [ ... ], "next_token": "..."}
        data_list = chunk.get("data", [])
        # extend our master list with this chunk's data
        if isinstance(data_list, list):
            all_records.extend(data_list)
    return all_records

def clean_data(records):
    keys_in_minutes = [
        "awake_time",
        "deep_sleep_duration",
        "rem_sleep_duration",
        "total_sleep_duration"
    ]

    select_keys = [
        "day",
        "awake_time",
        "average_hrv",
        "average_heart_rate",
        "average_breath",
        "deep_sleep_duration",
        "rem_sleep_duration",
        "total_sleep_duration"
    ]

    #remove naps
    min_sleep_duration = 3 * 3600  # 3 hours in seconds
    filtered_data = [
        item for item in records
        if item.get('total_sleep_duration', 0) >= min_sleep_duration
    ]

    #select only relevant keys & convert to minutes
    final_data = []
    for item in filtered_data:
        row = {}
        for key in select_keys:
            value = item.get(key)
            if key in keys_in_minutes and value is not None:
                row[key] = value / 60  # convert seconds to minutes
            else:
                row[key] = value
        final_data.append(row)

    return final_data

def store_oura_data (cleaned_records): #list of dictionaries
    oura_graph = Graph.query.filter_by(name="Oura Data").first()
    if not oura_graph: 
        oura_graph = Graph(name="Oura Data", description="data from Oura API")
        db.session.add(oura_graph)
        db.session.commit()

    new_data_points = []

    for record in cleaned_records:
        day_str = record.get("day")
        if not day_str: 
            continue

        day_date = pd.to_datetime(day_str).date()

        for metric, value in record.items(): 
            if metric == "day" or value is None:
                continue
        
            existing_dp = DataPoint.query.filter_by(
                date=day_date,
                metric_name=metric,
                graph_id=oura_graph.id
            ).first()

            if not existing_dp:
                new_data_points.append(
                    DataPoint(
                        date=day_date,
                        metric_name=metric,
                        value=float(value),
                        graph_id=oura_graph.id
                    )  
                )
        
    db.session.bulk_save_objects(new_data_points)
    db.session.commit()
    rows_inserted = len(new_data_points)
            # Data inserted successfully
    return rows_inserted

# (Optional) A quick test call:
if __name__ == '__main__':
    token = '***REMOVED***'
    data = fetch_oura_data(token, '2025-01-01', '2025-02-10')
    flattened = flatten_oura_chunks(data)
    cleaned=clean_data(flattened)
    # Data cleaned successfully







