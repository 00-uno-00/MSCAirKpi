from flask import Blueprint,render_template
import src.utils.spis as spi_utils
from datetime import datetime
### DATA ANALYSIS
import plotly.graph_objects as go


def get_table(all_data, graph_map, table, max_entries=0): 
    """
    Endpoint to retrieve the table data for the selected module.
    Args:
        all_data (list): List of dictionaries containing SPI data. CHECK all_data structure.
        graph_map (dict): Mapping of SPI signs to their graphical representations.
        table (str): The name of the template to render the table.

    Returns:
        html for the table with the data for the selected module.
    """

    processed_data = []# buffer for processed data to be used in the template & graphs

    for spi in all_data:
        spi_values = spi['data']
        target_value = spi['target_value']
        if isinstance(target_value, list):
            target_value = sorted(target_value)[0] if target_value else None
        processed_spi = {
            'id': spi['id'],
            'spi_name': spi['spi_name'],
            'data': spi_utils.process_data(spi_values, spi['id'], spi['spi_name'], max_entries),# align data if missing
            'target_value': spi['target_value'],
            'sign': graph_map.get(spi['sign'], spi['sign'])  
        }
        processed_data.append(processed_spi)

    return render_template(table, rows=processed_data, this_month=datetime.today().replace(month=datetime.today().month-1).strftime('%Y-%m'))

def fill_max(rows):
    """
    Fills missing months in the data entries.
    Args:
        rows (list): List of dictionaries containing SPI data entries.

    """
    max_length = find_max(rows)
    for entry in rows:
        data = entry.get('data', {})
        values = data.get('values', [])
        # Fill in empty months
        while len(values) < max_length:
            values.append({'value': 0})
        data['values'] = values
    return max(len(entry.get('data', [])) for entry in rows)

def find_max(rows):
    """
    Finds the maximum length of the 'values' list in the data entries.
    """
    max_length = 0
    for entry in rows:
        values = entry.get('data', {}).get('values', [])
        if len(values) > max_length:
            max_length = len(values)
    return max_length
