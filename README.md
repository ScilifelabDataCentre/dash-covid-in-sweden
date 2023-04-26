# COVID-19 in Sweden dashboard: Cases, ICU Admissions, Deaths

Plotly Dash dashboard containing graphs displaying the number of confirmed COVID-19 cases, admissions to intensive care units, and deaths due to COVID-19 in Sweden. The dashboard is based on open data shared by the Swedish Public Health Agency (Folkhälsomyndigheten) between February 2020 and March 2023. There are two filtering options: by date and by county (region).

The live dashboard can be found here: [c19-sweden.serve.scilifelab.se](https://c19-sweden.serve.scilifelab.se/).

## How the dashboard is built

The dashboard is built using [plotly.py](https://github.com/plotly/plotly.py), [Plotly Dash](https://github.com/plotly/dash), [Dash Bootstrap Components](https://github.com/facultyai/dash-bootstrap-components), [pandas](https://github.com/pandas-dev/pandas).

The underlying data is in an Excel file, fetched by the app using an URL. This Excel file is available in the */assets/* folder of this repository.

## Contributing

We welcome suggestions and contributions. If you found a mistake or would like to make a suggestion, please create an issue in this repository. Those who wish are also welcome to submit pull requests.

## Contact

This dashboard was built by [SciLifeLab Data Centre](https://github.com/ScilifelabDataCentre) team members. Primary contributors:

- [@LianeHughes](http://github.com/LianeHughes/)
- [@akochari](http://github.com/akochari/)
