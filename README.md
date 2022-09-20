# social-insecurity

## Important information
This project uses '''https''' through the inclusion of '''FLASK_RUN_CERT = adhoc''' in the ''' .flaskenv ''' file. That means you need to have '''python-dotenv''' in order to execute this file. This dependency can be installed by using the following command:

```
pip install -r requirements.txt
```

Be adviced that most modern browsers will display a warning regarding insecure certificate. You can safely ignore this, or remove '''FLASK_RUN_CERT''' from '''.flaskenv''' to run normal http.