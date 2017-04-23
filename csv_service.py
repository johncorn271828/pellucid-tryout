import numpy as np
import pandas as pd
import dateparser
import tempfile
from flask import Flask, request, redirect, send_file



app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
def csv_service():
    "Flask REST service for transforming csvs as described in the exercise."
    
    if(request.method == 'POST' and
       'daily.csv' in request.files and
       'companies.csv' in request.files and
       'start_date' in request.form and
       'end_date' in request.form and
       'n' in request.form):
        
        #Needed request data in hand, generate the csv response to a tempfile.
        with tempfile.NamedTemporaryFile() as tf:
            make_csv_response(request, tf.name)

            #Send the response
            return send_file(tf.name, mimetype='text/csv', as_attachment=True,
                             attachment_filename='transformed.csv')

    #Somewhat curt response for malformed requests.
    return '''<!doctype html>
<title>CSV Service</title>
<h1>CSV Service</h1>
<form method=post enctype=multipart/form-data>
<p> daily.csv : <input type=file name=daily.csv> </p>
<p> companies.csv : <input type=file name=companies.csv> </p>
<p> start_date: <input type=date name=start_date> </p>
<p> end_date : <input type=date name=end_date> </p>
<p> n : <input type=number name=n min=1> </p>
<p> <input type=submit value=Submit> </p>
</form>'''


def make_csv_response(request, tf_path):
    "Use DataFrames to generate the csv file, writing to tf_path."

    #Read companies into a dataframe, dropping duplicates.
    companies = make_companies(request.files['companies.csv'])

    #Read daily into a dataframe, with some basic cleaning.
    daily = make_daily(request.files['daily.csv'])

    #Gather metadata from the request.
    start_date = dateparser.parse(request.form['start_date'])
    end_date = dateparser.parse(request.form['end_date'])
    try:
        n = max(1, int(request.form['n']))
    except:
        n = 1

    #Merge the data frames.
    merged = make_merged(daily, companies, start_date, end_date, n)

    #Write the csv to the temporary file before upload and return.
    merged.to_csv(tf_path,sep=',')
    return


def make_companies(csv_file):
    "Construct clean-ish dataframe from companies.csv"
    
    companies = pd.read_csv(csv_file)
    
    #Eliminate double associations.
    companies.drop_duplicates(subset='id', keep='last')
    
    #More cleaning?
    
    return companies


def make_daily(csv_file):
    "Construct a clean-ish DataFrame from daily.csv"
    
    # Instructions say to forward fill missing dates.
    daily = pd.read_csv(csv_file).ffill()
    
    #Use dateparser to turn date strings into date objects.
    daily['date'] = daily['date'].apply(dateparser.parse)
    
    #Use builtin float parser, dropping rows without value.
    def try_float(s):
        try:
            result = float(s)
        except:
            result = np.NAN
        return result
    daily['value'] = daily['value'].apply(try_float)
    daily = daily[~pd.isnull(daily['value'])]

    #moar?
    
    return daily
    

def make_merged(daily, companies, start_date, end_date, n):
    "Construct a merged DataFrame with everything needed for the output csv."
    
    merged = pd.merge(daily, companies, on='id')

    #Sort by id, then date.
    merged.sort_values(['id', 'date'], ascending=[True,True], inplace=True)

    #Select rows within desired date range,
    merged = merged[(merged['date'] >= start_date) & \
                      (merged['date'] <= end_date)]\

    #Compute difference column.
    merged['difference'] = merged['value'] -   \
                           merged.groupby(['id'])['value']\
                                 .transform(lambda x: x.shift(n))

    return merged



if __name__ == "__main__":
    app.run(debug=True)
