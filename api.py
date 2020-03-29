from flask import Flask, request, make_response, render_template, flash
import automl_model
import utils
from forms import InputForm, LongForm
from flask import Markup

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/start',methods=['GET','POST'])
def start():
    mlr_form = InputForm()
    automl_form = LongForm()

    #display predictions from automl model
    if automl_form.validate_on_submit():
        prediction = automl_model.predict([automl_form.volume.data,automl_form.rsi.data,automl_form.sma.data,automl_form.macd.data,automl_form.rmb.data, automl_form.rlb.data,automl_form.rub.data])
        print(prediction)
        flash(str(prediction))

    #display mlr model summary
    elif mlr_form.validate_on_submit():
        info = utils.get_model_summary(utils.get_clean_input_data(str(mlr_form.stock.data)))
        summary = info[0]
        results = info[1]
        R2 = results.rsquared
        SSR = results.ssr
        p = results.pvalues
        nobs = results.nobs
        flash(Markup("<h6>Model Summary: </h6>"))
        flash(Markup("<p><b>Number of observations:</b> "+ str(nobs) +"</p>"))
        flash(Markup("<p><b>R^2 value:</b> "+ str(R2)+ "</p>" ))
        flash(Markup("<p><b>Sum of the squared residuals:</b> " + str(SSR) + "</p>"))
        flash(Markup("<h6>Statistics for each independent variable: </h6>"))
        flash(Markup(str(summary.tables[1].as_html())))

    return render_template('home.html', mlr_form=mlr_form,automl_form=automl_form)

#api requests
@app.route('/api/automl_long_term/', methods=['POST'])

def automl_long_term():
    jsonfile = request.get_json(force=True)
    prediction = automl_model.predict(jsonfile['values'])
    return "\n" + prediction

@app.route('/api/mlr/', methods=['POST'])
def mlr():
    jsonfile = request.get_json(force=True)
    summary = utils.get_model_summary(utils.get_clean_input_data(jsonfile['stock']))
    return str(summary)

if __name__ == '__main__':
    app.run(debug=True)