from flask import Blueprint,render_template, request, session
import src.utils.spis as spi_utils
import src.utils.db as db_utils
import src.utils.table as table_utils
from src.utils.graphs import interactive_plot
from datetime import datetime
import pandas as pd
### DATA ANALYSIS
import plotly.graph_objects as go

module1_OCC_ = Blueprint('module1_OCC_', __name__)

spis = {}
graph_map ={ 
    "tozeroy": "≥"
}

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
    
    session['all_data'] = all_data

    aircafts = []

    for spi in all_data:
        if spi['spi_name'].__contains__('I-MSC'):
            start_index = spi['spi_name'].index('I-MSC')
            end_index = start_index + 6
            aircafts.append(spi['spi_name'][start_index:end_index])

    table=table_utils.get_table(all_data, graph_map)

    return render_template('OCC.html', table=table, all_data=all_data, start_date_value=datetime.today().replace(month=1, day=1).strftime('%Y-%m-%d'), end_date_value=datetime.today().strftime('%Y-%m-%d'), aircrafts=aircafts)
