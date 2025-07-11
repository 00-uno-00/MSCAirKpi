import pandas as pd
import plotly.graph_objects as go

def interactive_plot(df, spi_name, target_value=0, fill='tozeroy'):
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
            showlegend=True,
            fill=fill
        )
    )
    return fig.to_html(full_html=True, include_plotlyjs='cdn')