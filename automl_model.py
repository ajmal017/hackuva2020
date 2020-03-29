from google.cloud import automl_v1beta1 as automl
from google.oauth2 import service_account
#values = array w 7 elements

def predict(values):
    client = automl.TablesClient(credentials=service_account.Credentials.from_service_account_file('key.json'),project='hackuva2020', region='us-central1')
    response = client.predict(
        model_display_name='dow_20200328092950', inputs=values)
    prediction = ""
    for result in response.payload:
        cl = float(result.tables.value.string_value)
        if cl > 0.0:
            if result.tables.score >= .50:
                prediction = "Buy! Confidence: {:.2f}".format(result.tables.score)
        else:
            if result.tables.score > .50:
                prediction = "Sell! Confidence: {:.2f}".format(result.tables.score)
    return prediction