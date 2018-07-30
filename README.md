# colormeshop-sales-predictor
A small web application which predicts the sales of your shop. :moneybag:

```bash
$ pipenv --three
$ pipenv install
$ FLASK_APP=app.py \
COLORME_ACCESS_TOKEN={YOUR_COLORME_ACCESS_TOKEN} \
DARKSKY_API_KEY={YOUR_DARKSKY_API_KEY} \
pipenv run flask run

 * Serving Flask app "app.py"
 * Environment: production
...
...
```

![image](https://user-images.githubusercontent.com/1885716/43401489-3f4ccac6-944b-11e8-9992-c373b08ed2a9.png)

- Model: Simple linear regression
- Learning algorithm: Least squares 
- Features: Temperatures (powered by [Dark Sky](https://darksky.net/poweredby/))
