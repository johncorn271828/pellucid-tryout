This has been tested with CPython 3.5.2. You might need to use pip or whatever to install dateparser, numpy, pandas, and/or flask. To start the service, say

$ python3 csv_service.py

Flask will print the IP address at which the service can be accessed.  You could try testing it with curl, on my machine I use

$ curl -i http://127.0.0.1:5000/ -F "start_date=1/1/2017" -F "end_date=1/9/2017" -F "n=2" -F "daily.csv=@/home/john/pellucid_tryout/daily.csv" -F "companies.csv=@/home/john/pellucid_tryout/companies.csv"

You could also just go to the url in your browser and use the submit forms.
