from flask import Blueprint,render_template, request, session, make_response
import src.utils.spis as spi_utils
import src.utils.db as db_utils
import src.utils.table as table_utils
import src.utils.time_utils as time
from src.utils.graphs import interactive_plot, comparison_plot
from datetime import datetime
import calendar
import json
### DATA ANALYSIS
import plotly.graph_objects as go
import pandas as pd

module1_OCC_ = Blueprint('module1_OCC_', __name__)
SPIS = [
    { "id": 38, "spi_name": "Flight time -- block hours (HH:MM) - COM flights only", "target_value": 5000, "mode": "sum", "table": "occ_flight_data", "sign": "tozeroy"},
    { "id": 39, "spi_name": "Flight cycles -- COM flights only", "target_value": 475, "mode": "sum", "table": "occ_flight_data", "sign": "tozeroy"},
    { "id": 40, "spi_name": "Flight hours per cycle --", "target_value": 8, "mode": "avg", "table": "occ_flight_data", "sign": "tozeroy"},
    { "id": 41, "spi_name": "Regularity --", "target_value": 95, "mode": "avg", "table": "occ_flight_data", "sign": "tozeroy"},
    { "id": 42, "spi_name": "Departure Punctuality --","target_value": 75, "mode": "avg", "table": "occ_flight_data", "sign": "tozeroy"},
    { "id": 43, "spi_name": "Aircraft daily utilization per month --", "target_value": 12, "mode": "avg", "table": "occ_flight_data", "sign": "tozeroy"}
]

graph_map ={ 
    "tozeroy": "≥"
}

graphs_spis = [#uso id per corrispondneza anche se presente nome A/C mentre nome grafico custom, mantengo target indipendneti per table e grafico 
    {"id":38,"table_name": "Flight time - block hours", "target_value": 5000/12},
    {"id":39,"table_name": "Flight cycles", "target_value": 475/12},
    {"id":40,"table_name": "Flight hours per cycle", "target_value": [11, 10.50]},
    {"id":41,"table_name": "Regularity ", "target_value": 95},
    {"id":42,"table_name": "Departure Punctuality", "target_value": 75},
    {"id":43,"table_name": "Aircraft daily utilization per month", "target_value": 12}
]

@module1_OCC_.route('/module/1', methods=['GET', 'POST'])
def module_1_OCC():
    """
    Route for Operational Control Center (OCC) module, which handles the safety data.
    """
    
    cur = db_utils.get_db_connection().cursor()
    user_agent=request.headers.get('User-Agent')
    if (
        ('Firefox' in user_agent) or
        ('Safari' in user_agent and 'Chrome' not in user_agent and 'Edg/' not in user_agent)
    ):
        start_date = request.args.get('start_date', datetime.today().replace(month=1, day=1).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.today().strftime('%Y-%m-%d'))
    else:
        start_date = request.args.get('start_date', datetime.today().replace(month=1, day=1))
        end_date = request.args.get('end_date', datetime.today())
    
    all_data = db_utils.get_data_table('occ_flight_data', start_date=start_date, end_date=end_date, cur=cur)
    
    if not all_data:
        return render_template('OCC.html', table=None, all_data=None, start_date_value=datetime.today().replace(month=1, day=1).strftime('%Y-%m-%d'), end_date_value=datetime.today().strftime('%Y-%m-%d'), aircrafts=[])          

    session['all_data'] = all_data

    aircafts = []
    max_entries = 0

    for spi in all_data:
        if spi['spi_name'].__contains__('I-MSC'):
            start_index = spi['spi_name'].index('I-MSC')
            end_index = start_index + 6
            if spi['spi_name'][start_index:end_index] not in aircafts:
                aircafts.append(spi['spi_name'][start_index:end_index])
        if len(spi['data']) > max_entries:
            max_entries = len(spi['data'])

    table=table_utils.get_table(all_data, graph_map, 'occ_table.html', max_entries)

    resp = make_response()

    resp.set_cookie('spis', json.dumps(graphs_spis))  # Cookies are used for conditional formatting in the table

    for spi in graphs_spis:
        target_value = spi['target_value']
        if isinstance(target_value, list):
            resp.set_cookie(f"id_{spi['id']}", str(target_value))

    resp.set_data(render_template('OCC.html', table=table, all_data=all_data, start_date_value=datetime.today().replace(month=1, day=1).strftime('%Y-%m-%d'), end_date_value=datetime.today().strftime('%Y-%m-%d'), aircrafts=aircafts))
    
    return resp 

@module1_OCC_.route('/module/1/graphs')
def module_1_OCC_graphs():
    """Route for generating graphs for the OCC module.
    """

    processed_data = session.get('all_data', [])
    # convert the date from cookie to datetime
    if not processed_data:
        return "No data available", 404
    for spi in processed_data:
        for entry in spi['data']:
            if isinstance(entry['entry_date'], str):
                entry['entry_date'] = datetime.strptime(entry['entry_date'], '%a, %d %b %Y %H:%M:%S %Z')


    graphs = ""

    same_table_spis = []
    # group spis by their table name and pop them from the processed_data
    for graph_spi in graphs_spis:
        same_table_spis = [spi for spi in processed_data if spi['spi_name'].__contains__(f"{graph_spi['table_name'].split(' ')[0]} {graph_spi['table_name'].split(' ')[1] if graph_spi['table_name'].split(' ')[1] else ''}")]
        if len(same_table_spis)>0:
            for spi in same_table_spis:
                processed_data.remove(spi)
                for entry in spi['data']:# convert string values to float for the graph
                    if isinstance(entry['value'], str):
                        entry['value'] = float(entry['value']) if entry['value'] else 0.0
                    entry['entry_date'] = pd.to_datetime(entry['entry_date'])  # Ensure entry_date is in datetime format
                if spi['spi_name'].__contains__("hours") or spi['spi_name'].__contains__("month"):
                    for entry in spi['data']:
                        if isinstance(entry['value'], float) or isinstance(entry['value'], int):
                            entry['value'] = round(entry['value'] / 60, 2)

            graphs += f'<div class="graph-item">{comparison_plot(same_table_spis, graph_spi['table_name'], graph_spi['target_value'])}</div>'

    for processed_spi in processed_data:
        # values are string by default messing up the graphs
        for graph_spi in graphs_spis:
            if processed_spi['spi_name'].__contains__(f"{graph_spi['table_name'].split(' ')[0]} {graph_spi['table_name'].split(' ')[1] if graph_spi['table_name'].split(' ')[1] else ''}"):
                for entry in processed_spi['data']:
                    if isinstance(entry['value'], str):
                        entry['value'] = float(entry['value']) if entry['value'] else 0.0

                # convert minutes into hrs(float) for the graph
                if processed_spi['spi_name'].__contains__("hours") or processed_spi['spi_name'].__contains__("month"):
                    for entry in processed_spi['data']:
                        if isinstance(entry['value'], float) or isinstance(entry['value'], int):
                            entry['value'] = round(entry['value'] / 60, 2)

                graphs += f'<div class="graph-item">{interactive_plot(pd.DataFrame(processed_spi['data']), graph_spi['table_name'], graph_spi['target_value'], processed_spi['sign'])}</div>'
    
    return graphs

def auto_values(flight_cycles_data, flight_time_data):
    """
    Calculate the SPIS for the OCC module.
    """

    all_data = session.get('all_data', [])
    if not all_data:
        return "No data available for calculations."

    if len(all_data) < 2:
        return "Insufficient data for calculations."

    if flight_cycles_data is None or flight_time_data is None:
        return "Insufficient data for calculations."

    fhrc = spi_utils.get_spi_by_name("Flight hours per cycle")

    ac_daily_utilization = {}

    if flight_cycles_data is None or flight_cycles_data['value'] == 0:
        flight_hours_per_cycle = 0
    else:
        flight_hours_per_cycle = flight_time_data['value'] / flight_cycles_data['value']

    flight_hours_per_cycle = {
        'id': fhrc['id'],
        'spi_name': "Flight hours per cycle",
        'data': [{
            'value': round(flight_hours_per_cycle, 2),
            'entry_date': flight_cycles_data['entry_date']}],
        'target_value': fhrc['target_value'],
        'mode': fhrc['mode'],
        'table': fhrc['table'],
        'sign': fhrc['sign']
        }

    acd_m = spi_utils.get_spi_by_name("Aircraft daily utilization per month")

    if flight_time_data is not None and flight_time_data['value'] is not None:
        ac_daily_utilization = flight_time_data / calendar.monthrange(flight_time_data['entry_date'].year, flight_time_data['entry_date'].month)[1]
    else:
        ac_daily_utilization = 0

    ac_daily_utilization = {
        'id': acd_m['id'],
        'spi_name': "Aircraft daily utilization per month",
        'data': [{
            'value': round(ac_daily_utilization, 2),
            'entry_date': flight_time_data['entry_date']}],
        'target_value': acd_m['target_value'],
        'mode': acd_m['mode'],
        'table': acd_m['table'],
        'sign': acd_m['sign']
    }
    # Calculate daily utilization for each flight time entry based on the previous month days
    
    return [flight_hours_per_cycle, ac_daily_utilization]

@module1_OCC_.route('/module/1/save/<spi_name>', methods=['POST'])
def save_data(spi_name=None):
    """
    Save the data to the database.
    """

    conn = db_utils.get_db_connection()

    new_data = []
    reference_month = datetime.today().month  # Usa il mese corrente come riferimento
    reference_year = datetime.today().year  # Usa l'anno corrente come riferimento
    for spi in SPIS:
        spi_id = spi['id']
        spi_value = request.form.get(f'{spi_id}')
        if spi_value != '' and spi_value is not None:
            if spi_id == 41 or spi_id == 42:
                spi_value = float(spi_value)
            if spi_id == 40 or spi_id == 43 or spi_id == 38:  
                spi_value = time.time_to_minutes((spi_value).split(':')[0],(spi_value).split(':')[1])
            else:
                spi_value = int(spi_value)

            # Aggiungi i dati al buffer
            new_data.append((spi_name if spi_name else spi['spi_name'], spi_value, reference_month, reference_year))
            # perform commit
        else:
            spi_value = None


    db_utils.commit_update_data(new_data, conn, 'occ_flight_data')

    return "OK", 200

@module1_OCC_.route('/module/1/submit_spis', methods=['POST'])
def submit_spis():
    """
    Submit the SPIS data to the database.
    """
    data = request.get_json()

    print("Received data:", data)

    new_data = []
    reference_month = datetime.today().month
    reference_year = datetime.today().year

    if not data:
        return "No data provided", 400
    for aircraft_spis in data:
        for spi_name, value in aircraft_spis.items():
            if spi_name == 'aircraft':
                continue
            new_data.append((spi_name, value, reference_month, reference_year))

        # Save the data for each SPI
    
    db_utils.commit_update_data(new_data, db_utils.get_db_connection(), 'occ_flight_data')

    return "Data submitted successfully", 200

@module1_OCC_.route('/module/1/ac_data', methods=['GET'])
def get_ac_data():
    """
    Get the data for a specific aircraft.
    """
    aircraft = request.args.get('aircraft', None)

    ac_data = []
    max_entries = 0

    cur = db_utils.get_db_connection().cursor()

    if aircraft.__contains__('I-MSC'):
        for spi in SPIS:
            spi_copy = spi.copy()
            ac_index = spi_copy['spi_name'].index('--') + 1
            spi_copy['spi_name'] = spi_copy['spi_name'][:ac_index] +"("+ aircraft +")"+ spi_copy['spi_name'][ac_index:]
            data = db_utils.get_data_spi(spi_copy['spi_name'], datetime.today().replace(month=1, day=1), datetime.today(), cur, spi['table'])
            if data:
                ac_data.append({
                    'id': spi_copy['id'],
                    'spi_name': spi_copy['spi_name'],
                    'data': data,
                    'target_value': spi_copy['target_value'],
                    'mode': spi_copy['mode'],
                    'table': spi_copy['table'],
                    'sign': spi_copy['sign']
                })
            if len(data) > max_entries:
                max_entries = len(data)
    
        if not ac_data:
            return "No data found for the specified aircraft."

        return table_utils.get_table(ac_data, graph_map, 'occ_table.html', max_entries)
    
    else:
    
        cur = db_utils.get_db_connection().cursor()
        user_agent=request.headers.get('User-Agent')
        if (
            ('Firefox' in user_agent) or
            ('Safari' in user_agent and 'Chrome' not in user_agent and 'Edg/' not in user_agent)
        ):
            start_date = request.args.get('start_date', datetime.today().replace(month=1, day=1).strftime('%Y-%m-%d'))
            end_date = request.args.get('end_date', datetime.today().strftime('%Y-%m-%d'))
        else:
            start_date = request.args.get('start_date', datetime.today().replace(month=1, day=1))
            end_date = request.args.get('end_date', datetime.today())

        all_data = db_utils.get_data_table('occ_flight_data', start_date=start_date, end_date=end_date, cur=cur)

        if not all_data:
            return render_template('OCC.html', table=None, all_data=None, start_date_value=datetime.today().replace(month=1, day=1).strftime('%Y-%m-%d'), end_date_value=datetime.today().strftime('%Y-%m-%d'), aircrafts=[])          

        session['all_data'] = all_data

        aircafts = []
        max_entries = 0

        for spi in all_data:
            if spi['spi_name'].__contains__('I-MSC'):
                start_index = spi['spi_name'].index('I-MSC')
                end_index = start_index + 6
                if spi['spi_name'][start_index:end_index] not in aircafts:
                    aircafts.append(spi['spi_name'][start_index:end_index])
            if len(spi['data']) > max_entries:
                max_entries = len(spi['data'])

        table=table_utils.get_table(all_data, graph_map, 'occ_table.html', max_entries)

        resp = make_response()

        resp.set_cookie('spis', json.dumps(graphs_spis))  # Cookies are used for conditional formatting in the table

        for spi in graphs_spis:
            target_value = spi['target_value']
            if isinstance(target_value, list):
                resp.set_cookie(f"id_{spi['id']}", str(target_value))

        resp.set_data(table)

        return resp 

@module1_OCC_.route('/module/1/get_table', methods=['GET']) 
def get_table():
    """
    Endpoint to retrieve the table data for the module 3, also updates all_data.
    Returns:
        html for the table with the data for the module 3.
    """

    # Recupera i dati esistenti dal database
    cur = db_utils.get_db_connection().cursor()

    user_agent=request.headers.get('User-Agent')
    if (
        ('Firefox' in user_agent) or
        ('Safari' in user_agent and 'Chrome' not in user_agent and 'Edg/' not in user_agent)
    ):
        start_date = request.args.get('start_date', datetime.today().replace(month=1, day=1).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.today().strftime('%Y-%m-%d'))
    else:
        start_date = request.args.get('start_date', datetime.today().replace(month=1, day=1))
        end_date = request.args.get('end_date', datetime.today())

    all_data=db_utils.get_data_table('occ_flight_data', start_date, end_date, cur=cur)

    cur.close()
    db_utils.get_db_connection().close()

    return table_utils.get_table(all_data, graph_map, 'occ_table.html')