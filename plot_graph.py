import plotly.graph_objects as go

def plot_sleep_metrics(df, select_keys): 
    fig = go.Figure()

    for column in select_keys: 
        if column != 'day': 
            fig.add_trace(go.Scatter(
                x=df['day'],
                y=df[column],
                mode='lines', 
                name=column,
                line_shape='spline'
                ))
            
    fig.update_layout(
        title='Sleep metrics', 
        xaxis_title='date', 
        yaxis_title='values', 
        template='plotly_white', 
        xaxis=dict(tickformat="%Y-%m-%d", showgrid=True), 
        yaxis=dict(showgrid=True), 
        legend=dict(title="Metrics")
    )

    fig.show()