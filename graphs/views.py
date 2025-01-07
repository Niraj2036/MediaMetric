from django.shortcuts import render
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from django.conf import settings
import pprint
import requests
from django.http import JsonResponse


pprint.pprint(settings.TEMPLATES)

# df = pd.read_csv("C:/Users/niraj/Downloads/levelsupermindataset.csv")
df = pd.read_csv("https://bookstoreapp1.s3.eu-north-1.amazonaws.com/levelsupermindataset.csv")

# Convert the 'Date' column to datetime format and extract the day of the week
df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
df['day'] = df['date'].dt.day_name()

# Convert the 'Time' column to datetime format for easier time-based grouping
df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S').dt.time




def plot_graphs(request):
    # Calculate average likes, shares, comments, and engagement rate
    avg_likes = int(df['likes'].mean())
    avg_shares = int(df['shares'].mean())
    avg_comments = int(df['comments'].mean())
    avg_engagement_rate = round(df['engagement rate'].mean(), 2)

    # 1. Line graph: Day vs Average Impressions
    avg_impressions_day = df.groupby('day')['impressions'].mean().reset_index()
    # Ensure 'day' is in the correct order
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['day'] = pd.Categorical(df['day'], categories=day_order, ordered=True)
    
    # 1. Line graph: Day vs Average Impressions
    avg_metrics_day = df.groupby('day').agg({
        'impressions': 'mean',
        'likes': 'mean',
        'shares': 'mean',
        'comments': 'mean',
        'engagement rate': 'mean'
    }).reset_index()

    # Convert impressions, likes, shares, and comments to integers
    avg_metrics_day[['impressions', 'likes', 'shares', 'comments']] = avg_metrics_day[['impressions', 'likes', 'shares', 'comments']].astype(int)

    fig1 = px.line(avg_metrics_day, x='day', y='impressions', title='Average Impressions by Day')

    # Customizing Graph 1
    fig1.update_layout(
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=False,
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=2,
            fixedrange=True,
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=2,
            fixedrange=True,
        ),
        hovermode='x',
    )
    fig1.update_traces(
        line=dict(color='#5e9693', width=2),
        mode='lines+markers',
        marker=dict(
            symbol='circle',
            color='white',
            size=10,
            line=dict(color='#5e9693', width=2)
        ),
        hovertemplate='Day: %{x}<br>Impressions: %{y}<br>' +
                      'Average Likes: %{customdata[0]}<br>' +
                      'Average Shares: %{customdata[1]}<br>' +
                      'Average Comments: %{customdata[2]}<br>' +
                      'Average Engagement Rate: %{customdata[3]:.2f}<extra></extra>'
    )
    fig1.update_traces(customdata=avg_metrics_day[['likes', 'shares', 'comments', 'engagement rate']].values)

    # Add a moving vertical dotted line
    fig1.add_shape(
        type='line',
        x0=0,
        x1=0,
        y0=0,
        y1=1,
        xref='x',
        yref='paper',
        line=dict(color='gray', width=1, dash='dot'),
    )

    # 2. Line graph: Time vs Average Impressions (Hourly)
    df['Hour'] = pd.to_datetime(df['time'], format='%H:%M:%S').dt.hour
    avg_metrics_hour = df.groupby('Hour').agg({
        'impressions': 'mean',
        'likes': 'mean',
        'shares': 'mean',
        'comments': 'mean',
        'engagement rate': 'mean'
    }).reset_index()

    # Convert impressions, likes, shares, and comments to integers
    avg_metrics_hour[['impressions', 'likes', 'shares', 'comments']] = avg_metrics_hour[['impressions', 'likes', 'shares', 'comments']].astype(int)

    fig2 = px.line(avg_metrics_hour, x='Hour', y='impressions', title='Average Impressions by Hour')

    # Customizing Graph 2
    fig2.update_layout(
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=False,
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=2,
            tickmode='array',
            tickvals=[x for x in range(0, 24)],
            ticktext=[f'{x}:00-{x+1}:00' for x in range(0, 23)] + ['23:00-00:00'],
            fixedrange=True,
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=2,
            fixedrange=True,
        ),
        hovermode='x',
    )
    fig2.update_traces(
        line=dict(color='#5e9693', width=2),
        mode='lines+markers',
        marker=dict(
            symbol='circle',
            color='white',
            size=10,
            line=dict(color='green', width=2)
        ),
        hovertemplate='Hour: %{x}<br>Impressions: %{y}<br>' +
                      'Average Likes: %{customdata[0]}<br>' +
                      'Average Shares: %{customdata[1]}<br>' +
                      'Average Comments: %{customdata[2]}<br>' +
                      'Average Engagement Rate: %{customdata[3]:.2f}<extra></extra>'
    )
    fig2.update_traces(customdata=avg_metrics_hour[['likes', 'shares', 'comments', 'engagement rate']].values)

    # Add a moving vertical dotted line
    fig2.add_shape(
        type='line',
        x0=0,
        x1=0,
        y0=0,
        y1=1,
        xref='x',
        yref='paper',
        line=dict(color='gray', width=1, dash='dot'),
    )
    # 3. Bar graph: Post Type vs Engagement Rate
    avg_engagement_rate = df.groupby('type')['engagement rate'].mean().reset_index()
    fig3 = px.bar(avg_engagement_rate, x='type', y='engagement rate', title='Engagement Rate by Post Type')

    # Customizing Graph 3
    fig3.update_layout(
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=False,
            zeroline=True,
            zerolinecolor='#5e9693',
            zerolinewidth=2,
            fixedrange=True,
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True,
            zerolinecolor='#5e9693',
            zerolinewidth=2,
            fixedrange=True,
        ),
        bargap=0.3,
    )
    fig3.update_traces(
        marker=dict(color='#5e9693', line=dict(color='#5e9693', width=1)),
        hovertemplate='Type: %{x}<br>Engagement Rate: %{y:.2f}<extra></extra>'
    )

    # 4. Scatter plot: Engagement Rate vs Impressions
    fig4 = px.scatter(df, x='impressions', y='engagement rate', title='Engagement Rate vs Impressions')

    # Customizing Graph 4
    fig4.update_layout(
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=2,
            fixedrange=True,
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=2,
            fixedrange=True,
        ),
        hovermode='closest',
    )
    fig4.update_traces(
        marker=dict(color='green', size=10, opacity=0.7),
        hovertemplate='Impressions: %{x}<br>Engagement Rate: %{y:.2f}<extra></extra>'
    )

   # 5. Heatmap: Engagement Rate by Hour and Day (Blended Colors)
    import numpy as np

    # Preparing data for contour plot (smooth blending)
    import plotly.graph_objects as go


    # Preparing data for the heatmap
    heatmap_data = df.groupby(['day', 'Hour'])['engagement rate'].mean().unstack()
    x = heatmap_data.columns  # Hours
    y = heatmap_data.index    # Days
    z = heatmap_data.values   # Engagement rate values

    # Generating the heatmap
    fig5 = go.Figure(
        data=go.Contour(
            z=z,
            x=x,
            y=y,
            colorscale='RdYlGn',  # Red to yellow gradient
            contours=dict(
                coloring='fill',  # Smooth blended coloring
                showlines=False   # Ensure no lines are visible
            ),
            colorbar=dict(title='Engagement Rate'),  # Colorbar for context
        )
    )

    # Customizing the layout
    fig5.update_layout(
        title='Blended Heatmap of Engagement Rate by Hour and Day',
        xaxis=dict(
            title='Hour',
            tickmode='array',
            tickvals=[x for x in range(24)],
            ticktext=[f'{x}:00' for x in range(24)],
        ),
        yaxis=dict(
            title='Day',
            tickmode='array',
            tickvals=np.arange(len(df['day'].unique())),
            ticktext=df['day'].unique(),
        ),
        plot_bgcolor='white',  # White background for clarity
    )
    post_type_counts = df['type'].value_counts().reset_index()
    post_type_counts.columns = ['type', 'count']

    fig6 = px.pie(
        post_type_counts,
        values='count',
        names='type',
        title='Distribution of Posts by Type',
        color_discrete_sequence=px.colors.sequential.Greens  # Adjust color palette as desired
    )

    # Customizing the Pie Chart
    fig6.update_traces(
        textinfo='percent+label',  # Show both percentage and label
        pull=[0.1 if i == post_type_counts['count'].idxmax() else 0 for i in range(len(post_type_counts))],  # Highlight the largest slice
        hoverinfo='label+value+percent'  # Add detailed hover information
    )

    fig6.update_layout(
        showlegend=True,
        legend=dict(
            title='Post Types',
            orientation='h',  # Horizontal legend
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        )
    )



    # Convert Plotly figures to HTML
    graph_html1 = fig1.to_html(full_html=False)
    graph_html2 = fig2.to_html(full_html=False)
    graph_html3 = fig3.to_html(full_html=False)
    graph_html4 = fig4.to_html(full_html=False)
    graph_html5 = fig5.to_html(full_html=False)
    graph_html6 = fig6.to_html(full_html=False)

    # Render the template with the graphs
    return render(request, 'index.html', {
        'graph_html1': graph_html1,
        'graph_html2': graph_html2,
        'graph_html3': graph_html3,
        'graph_html4': graph_html4,
        'graph_html5': graph_html5,
        'graph_html6': graph_html6,
    })




# Constants for LangFlow API
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "ecd8c8e2-9811-404a-8fe7-2557f8542feb"
FLOW_ID = "c70b9d7d-f753-45e2-b923-e6db9006778c"
APPLICATION_TOKEN = "AstraCS:xQcnsaCmlNAxKQxdEmDdqvwT:01fb6832fc24c087bbcb352094c74b2e0f14494a7052402ca661217771dadf34"

# Chatbot interaction view
def chatbot_interact(request):
    if request.method == "POST":
        input_message = request.POST.get("message")
        if not input_message:
            return JsonResponse({"error": "No message provided"}, status=400)

        url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{FLOW_ID}?stream=false"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {APPLICATION_TOKEN}"
        }

        payload = {
            "input_value": input_message,
            "output_type": "chat",
            "input_type": "chat",
            "tweaks": {}
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            message = response_data.get("outputs")[0]["outputs"][0]["results"]["message"]["data"]["text"]
            return JsonResponse({"response": message})
        else:
            return JsonResponse({"error": "Failed to connect to LangFlow API"}, status=response.status_code)

    return JsonResponse({"error": "Invalid request method"}, status=405)