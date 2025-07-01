import pandas as pd
import plotly.graph_objects as go

def normalize_values(df, columns): 
    df_normalized = df.copy()
    for column in columns: 
        if column != 'day':
            col_min = df[column].min()
            col_max = df[column].max()
            df_normalized[column] = ((df[column] - col_min) / (col_max - col_min))
    
    return df_normalized
        
    

    