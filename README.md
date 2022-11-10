# minvar-portfolio-dashbord

A [dashboard](https://coindataschool-minvar-portfolio-dashbord-main-w2wjqa.streamlit.app/) for calculating the efficient frontier and min-variance portfolio of 
**GMX** and GNS based on historical daily prices.

![screen](https://github.com/coindataschool/minvar-portfolio-dashbord/blob/main/screenshot.png)

Manually run the following command to update data and calculation every month:

`$ python 01-download-data.py`

`$ python 02-calc-minvar-portfolios.py`

Re-deploy app after each update.