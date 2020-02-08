# Account Book
This repository provides a simple application on the account book, which is can easily build on your local machine like the raspberry pi. Comparing to other applications of account book, with full customize functionality you can have your data and make some statistics by using this application.

## Functionality
This application surrounds three elements: user, category, and bill.yo

### User
After register and login into the application,  you can set your limitation on the day, week and month budget in the user profile which will show on the home page.

### Category
After adding a new category on the add bill page, the profile for the category will appear on the sidebar menu. You can see the statistic on each category and set whether it counts into your day, week and month budget.

### Bill
You can add your bill on the add bill page and search the bill by date or category on the search bill page.

## Requirement

- Python3.5 or upper version
- Install requirement by `pip install -r requirements.txt`
- Setting the configuration by edditing the config.py file, and the content should include the `SECRET_KEY` and `SQLALCHEMY_DATABASE_URI`.
An simple example:

```python
{
    "SECRET_KEY": "secret_key",
    "SQLALCHEMY_DATABASE_URI": "mysql+pymysql://user:password@localhost/DataBase"
{
```
- Apache or Nginx is highly recommended to deploy the application