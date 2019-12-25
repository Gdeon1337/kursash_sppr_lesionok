from pandas import read_csv
from pandas import datetime
from datetime import timedelta
from matplotlib import pyplot
from statsmodels.tsa.arima_model import ARIMA
from pandas import DataFrame


def __getnewargs__(self):
    return (
        (self.endog),
        (self.k_lags, self.k_diff, self.k_ma)
    )


ARIMA.__getnewargs__ = __getnewargs__


def parser(x):
    return datetime.strptime('200' + x, '%Y-%m')


def get_plot(path, model_fit=None):
    series = read_csv(path, header=0, parse_dates=[0], index_col=0, squeeze=True, date_parser=parser)
    X = series.values
    size = int(len(X) * 0.66)
    train, test = X[0:size], X[size:len(X)]
    dates = series.index[size:len(X)]
    logger = [
        {
            'date': series.index[i],
            'value': series.values[i],
            'predict_value': ''
        }
        for i in range(len(train))
    ]
    history = [x for x in train]
    predictions, _logger, model_fit = fit_model(test, history, dates, model_fit)
    logger += _logger
    fig, ax = pyplot.subplots()
    ax.plot(test, label='Тестовые данные')
    ax.plot(predictions, color='red', label='Предикт ARIMA')
    ax.grid(True)
    ax.set_xlabel(u'Дата')
    ax.set_ylabel(u'Сумма в млн. руб.')
    ax.set_title(u'График суммы расходов на электроэнергию')
    ax.legend(loc='best', frameon=False)
    fig.savefig('image.png')
    image = load_file('image.png')
    image_error = load_file('image_error.png')
    return image, image_error, logger, model_fit


def load_file(path):
    file = open(path, 'rb')
    image = file.read()
    file.close()
    return image


def fit_model(test, history, dates, model):
    predictions = []
    logger = []
    model_fit = model
    for t in range(len(test)):
        if not model:
            model = ARIMA(history, order=(5, 1, 0))
            model_fit = model.fit(disp=0)
        output = model_fit.forecast()
        yhat = output[0]
        predictions.append(yhat)
        obs = test[t]
        history.append(obs)
        logger.append({
                'date': dates[t],
                'value': obs,
                'predict_value': round(yhat[0], 2)
            })
        model = None
    output = model_fit.forecast(steps=10)
    date = dates[-1]
    for yhat in output[0]:
        predictions.append(yhat)
        date = date + timedelta(days=31)
        logger.append({
            'date': date,
            'value': 'undefined',
            'predict_value': round(yhat, 2)
        })
    residuals = DataFrame(model_fit.resid)
    residuals.plot(kind='kde', label='График ошибки')
    pyplot.savefig('image_error.png')
    return predictions, logger, model_fit
