# Stock Portfolio Tracker

Stock Portfolio Tracker is a web application designed to simulate a stock trading platform. Originating from the finance problem set of CS50x, this project is continuously evolving with regular improvements and feature additions.

## Features

- **User Registration**: New users can register with a unique username and password.
- **Stock Price Lookup**: Users can check the current price of stocks using their symbols.
- **Buy Stocks**: Users can buy stocks using virtual cash.
- **Sell Stocks**: Users can sell stocks they own.
- **Transaction History**: Users can view a history of all their transactions.
- **User Dashboard**: Displays a summary of stocks owned, their current values, and the user's cash balance.

## Setup and Installation

1. **Clone the repository**:

    ```bash
    git clone [repository_link]
    cd finance
    ```

2. **Install the required packages**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up the Flask application**:

    ```bash
    export FLASK_APP=app.py
    ```

4. **Run the application**:

    ```bash
    flask run
    ```

5. Visit the provided link to access the web application.

## Usage

- **Register**: For new users, register with a unique username and password.
- **Login**: If already registered, log in with your credentials.
- **Quote**: Enter a stock symbol to check its current price.
- **Buy**: Purchase stocks by entering the stock symbol and the number of shares.
- **Sell**: Sell stocks you own by selecting the stock and specifying the number of shares.
- **History**: View a list of all your transactions.
- **Deposit Cash**: Add more virtual cash to your account.

## Technologies Used

- Flask
- SQLite
- IEX Cloud API (for stock price lookup)

## Continuous Improvement

This project is a living entity, with plans for consistent updates, feature additions, and improvements as I progress in my programming journey. Feedback and suggestions are always welcome.