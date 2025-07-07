from flask import Blueprint,render_template, request, redirect
import src.utils.spis as spi_utils
import src.utils.db as db_utils
from datetime import datetime
import pandas as pd

### DATA ANALYSIS
import plotly.graph_objects as go


module3_bp = Blueprint('module3', __name__)
#!!! IDS USED FOR IDENTIFICATION WITHIN THE TABLE NOT TO IDENTIFY SPI CLASS !!!
spis = [
    { "id": 1, "spi_name": "Nr. of Safety Review Board perfomed", "target_value": 2, "mode": "sum"},
    { "id": 2, "spi_name": "% of Recommendations implemented (YTD)", "target_value": 95, "mode": "avg"},
]
"""{ "id": 3, "spi_name": "Nr. of Emergency Response (ERP) drill performed" },
    { "id": 4, "spi_name": "Nr. of review of Safety Policy & Objectives" },
    { "id": 5, "spi_name": "Nr of Accident" },
    { "id": 6, "spi_name": "Nr of Serious Incident" },
    { "id": 7, "spi_name": "Nr of Operational Incidents (MOR)" },
    { "id": 8, "spi_name": "Nr of Technical Incidents (MOR)" },
    { "id": 9, "spi_name": "Nr of Safety Reports (Voluntary & confidential) per month" },
    { "id": 10, "spi_name": "Nr of Risk Assessments perfomed per month" },
    { "id": 11, "spi_name": "Nr of Hazards identified per month" },
    { "id": 12, "spi_name": "Nr of new Mitigations validated and implemented per month" },
    { "id": 13, "spi_name": "Nr. of Safety Bulletin published" },
    { "id": 14, "spi_name": "Nr. of Safety Flash published" },
    { "id": 15, "spi_name": "Nr. of Runway Incursions per month (Source: Safety report)" },
    { "id": 16, "spi_name": "Nr. of Wildlife Strike per month (Source: Safety report)" },
    { "id": 17, "spi_name": "Nr. of Level Bust per month (Source: Safety report)" },
    { "id": 18, "spi_name": "Nr. of High speed rejected take-off per month (Source: FDM)" },
    { "id": 19, "spi_name": "Nr. of Take-off with abnormal configuration per month (Source: Safety report)" },
    { "id": 20, "spi_name": "Nr of Insufficient take-off performance per month (Source: FDM)" },
    { "id": 21, "spi_name": "Nr of Unstable Approach per month (Source: FDM)" },
    { "id": 22, "spi_name": "Nr of Abnormal pitch at touchdown per month (Source: FDM)" },
    { "id": 23, "spi_name": "Nr. of Hard landing per month (Source: FDM)" },
    { "id": 24, "spi_name": "Nr of Aircraft lateral deviations at high speed on the ground (beginning of landing roll) per month (Source: FDM, LF010 heading change after nose down)" },
    { "id": 25, "spi_name": "Nr of Aircraft lateral deviations at high speed on the ground (till end of take-off roll) per month (Source: FDM, TF300 Takeoff heading range 100knt to rotation)" },
    { "id": 26, "spi_name": "Nr of Short rolling distance at landing per month (Source: FDM)" },
    { "id": 27, "spi_name": "Nr of (E)GPWS/TAWS Warning Trigger per month (Source: FDM)" },
    { "id": 28, "spi_name": "Nr of Pitch attitude high during take off per month (Source: FDM)" },
    { "id": 29, "spi_name": "Nr of Stall protection trigger per month (Source: FDM)" },
    { "id": 30, "spi_name": "Nr of Excessive speed per month (Source: FDM)" },
    { "id": 31, "spi_name": "Nr of Excessive vertical speed during climb per month (Source: FDM)" },
    { "id": 32, "spi_name": "Nr of Excessive vertical speed during descent per month (Source: FDM)" },
    { "id": 33, "spi_name": "Nr of Low go-around or rejected landing per month (Source: FDM)" },
    { "id": 34, "spi_name": "Nr of Reduced margin to manoeuvrability speed per month (Source: FDM)" },
    { "id": 35, "spi_name": "Nr of TCAS/ACAS Resolution Advisory per month (Source: FDM)" },
    { "id": 36, "spi_name": "Nr. of COM flights captured by FDM per month" },
    { "id": 37, "spi_name": "Nr of of fatigue report form received per month" }"""

graphs_spis = [ ### Note all the SPIs need to be in the spis list to be displayed in the graphs
    {"spi_name": "Nr. of Safety Review Board perfomed" },
    {"spi_name": "% of Recommendations implemented (YTD)" },
]

@module3_bp.route('/module/3', methods=['GET', 'POST'])
def module_3():#!!!!ID USATO PER INDIVISUARE ISTANZA DI SPI NON CLASSE DI SPI!!!!
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        new_data = [] #buffer for one commit

        # Ottieni i dati dal modulo
        reference_month = datetime.today().month  # Usa il mese corrente come riferimento
        reference_year = datetime.today().year  # Usa l'anno corrente come riferimento
        for spi in spis:
            spi_id = spi['id']
            spi_value = request.form.get(f'{spi_id}')
            if spi_value is not None:
                try:
                    spi_value = int(spi_value)
                    if spi_value < 0:
                        return f"Invalid value for SPI {spi_id}: Value cannot be negative", 400
                    
                    # Aggiungi i dati al buffer
                    new_data.append((spi['spi_name'], spi_value, reference_month, reference_year))
                    # perform commit
                except ValueError:
                    return f"Invalid value for SPI {spi_id}", 400 #TODO add a popup
            else:
                spi_value = None
        # Commit all data in one go
        # Commit the update to the database
        db_utils.commit_update_data(new_data, conn) 

        return redirect('/module/3')

    # Recupera i dati esistenti dal database
    if request.method == 'GET':
        # Use request.args for GET parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        # Requires formatting or default values
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = datetime.today().replace(month=1, day=1)
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = datetime.today().replace(day=1)

        

        all_data = []
        for spi in spis:
            try:
                spi_data = db_utils.retrieve_data_db(spi['spi_name'], datetime.date(start_date), datetime.date(end_date), cur)
                all_data.append({'id': spi['id'], 'spi_name': spi['spi_name'], 'values': spi_data})
                ###
                #id
                #spi_name
                #values
                #   | spi_data = ['value', 'entry_date']
                ###
            except Exception as e:
                print(f"Error fetching data for SPI {spi['spi_name']}: {e}")

        cur.close()
        conn.close()

        processed_data = []# buffer for processed data to be used in the template & graphs

        for spi in all_data:
            spi_values = spi['values']
            processed_spi = {
                'id': spi['id'],
                'spi_name': spi['spi_name'],
                'data': spi_utils.process_data(spi_values, spi['id']),
                'target_value': spi_utils.get_spi_by_id(spi['id'])['target_value']
            }
            
            processed_data.append(processed_spi)
                

            #graphs = interactive_plot(pd.DataFrame(processed_data[0]['data']['values']), processed_data[0]['spi_name'])
    
        return render_template('SAFETY.html', rows=processed_data, start_date_value=start_date.strftime('%Y-%m-%d'), end_date_value=end_date.strftime('%Y-%m-%d'))

def interactive_plot(df, spi_name, target_value=0):
    """ 
        Generate an interactive plot for the given DataFrame and SPI name.
    """

    fig = go.Figure()
    
    fig.update_layout(
        title= f'{spi_name} - over time',
        xaxis_title='Entry Date',
        yaxis_title='SPI Value',
        template='plotly_white'
    )

    df['entry_date'] = pd.to_datetime(df['entry_date'])  # Ensure entry_date is in datetime format

    min_date = df['entry_date'].min()
    max_date = df['entry_date'].max()
    # Set interval (e.g., every 1 month)
    fig.update_xaxes(
        range=[min_date, max_date],
        dtick="M1", 
        tickformat="%Y-%m"
    )
    # Graph
    fig.add_trace(
        go.Scatter(
            x=df['entry_date'],
            y=df['value'],
            mode='lines+markers',
            name='SPI Value',
            line=dict(color='blue', width=2),
            marker=dict(size=5)
        )
    )
    # target
    fig.add_trace(
        go.Scatter(
            x=[min_date, max_date],
            y=[target_value, target_value],
            mode='lines',
            name='Target Value',
            line=dict(color='red', dash='dash'),
            showlegend=True
        )
    )
    return fig.to_html(full_html=True, include_plotlyjs='cdn')

@module3_bp.route('/module/3/graphs')
def module_3_graphs():
    conn = db_utils.get_db_connection()
    cur = conn.cursor()
    # Use the same date range logic as in /module/3
    start_date = datetime.today().replace(month=1, day=1)
    end_date = datetime.today().replace(day=1)
    all_data = []
    for spi in spis:
        try:
            spi_data = db_utils.retrieve_data_db(spi['spi_name'], datetime.date(start_date), datetime.date(end_date), cur)
            all_data.append({'id': spi['id'], 'spi_name': spi['spi_name'], 'target_value': spi['target_value'],'values': spi_data})
        except Exception as e:
            print(f"Error fetching data for SPI {spi['spi_name']}: {e}")
    cur.close()
    conn.close()
    graphs = ""
    for spi in all_data:
        if spi['spi_name'] in [g['spi_name'] for g in graphs_spis]:
            spi_values = spi['values']
            processed_spi = {
                'id': spi['id'],
                'spi_name': spi['spi_name'],
                'data': spi_utils.process_data(spi_values, spi['id'])
            }
            graphs += f'<div class="graph-item">{interactive_plot(pd.DataFrame(processed_spi["data"]["values"]), processed_spi["spi_name"], spi["target_value"])}</div>'
    
    return graphs