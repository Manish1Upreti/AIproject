import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use 'Agg' for non-interactive backends (necessary for server environments)
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import os
from django.shortcuts import render
from django.conf import settings
from transformers import pipeline
from .forms import UploadFileForm

# Load the sentiment analysis model (from HuggingFace)
analyzer = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

def generate_chart(sentiments, chart_type, palette):
    sentiment_counts = pd.Series(sentiments).value_counts()

    # Define the chart path to save images
    chart_path = os.path.join(settings.BASE_DIR, 'sentimentanalysis', 'static', 'charts', 'sentiment_chart.png')

    # Generate Bar Chart
    if chart_type == 'bar':
        plt.figure(figsize=(8, 5))
        ax = sns.barplot(x=sentiment_counts.index, y=sentiment_counts.values, hue=sentiment_counts.index, palette=palette, legend=False)

        # Add percentage annotations
        for i, count in enumerate(sentiment_counts.values):
            percentage = count / sentiment_counts.sum() * 100
            ax.text(i, count + 0.1, f'{percentage:.1f}%', ha='center', fontsize=10, weight='bold')

        plt.title("Sentiment Distribution")
        plt.xlabel("Sentiment")
        plt.ylabel("Count")
    else:  # Pie Chart
        colors = sns.color_palette(palette, n_colors=len(sentiment_counts)).as_hex()

        plt.figure(figsize=(8, 6))
        plt.pie(
            sentiment_counts,
            labels=sentiment_counts.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=140
        )
        plt.axis('equal')

    # Save the chart image to disk
    plt.savefig(chart_path)
    plt.close()

    return 'charts/sentiment_chart.png'


def process_file(file, chart_type, palette):
    try:
        # Read the Excel file
        df = pd.read_excel(file)

        # Ensure 'Review' column is present
        if 'Review' not in df.columns:
            raise ValueError("The uploaded file must contain a 'Review' column.")

        # Analyze sentiment using HuggingFace model
        sentiments = analyzer(df['Review'].tolist())
        df['Sentiment'] = [sent['label'] for sent in sentiments]

        # Generate chart
        chart_path = generate_chart(df['Sentiment'].tolist(), chart_type, palette)

        return df, chart_path

    except Exception as e:
        raise ValueError(f"Error processing file: {str(e)}")


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Process file and generate results
                df, chart_path = process_file(
                    request.FILES['file'],
                    form.cleaned_data['chart_type'],
                    form.cleaned_data['palette']
                )
                # Render table and chart results
                table_html = df.to_html(classes='table table-striped', index=False)
                return render(request, 'sentimentanalysis/result.html', {
                    'table_html': table_html,
                    'chart_path': chart_path
                })
            except Exception as e:
                # Handle errors during file processing
                return render(request, 'sentimentanalysis/upload.html', {
                    'form': form,
                    'error': str(e)
                })
    else:
        form = UploadFileForm()

    return render(request, 'sentimentanalysis/upload.html', {'form': form})
