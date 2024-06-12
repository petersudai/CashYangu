# CashYangu

Welcome to CashYangu, a comprehensive financial tracking web application designed to help you manage your expenses, budget, and savings efficiently. This README provides detailed instructions on how to get started, contribute, and understand the project's scope and functionality.

## Introduction

CashYangu is a web-based application aimed at simplifying personal financial management. With features to log your earnings, expenses, savings, and budget goals, CashYangu provides a user-friendly interface to keep your finances in check. The app also offers insightful financial reports and charts to help you visualize your financial health.

### Links

- **Deployed Site**: [CashYangu](https://cash-yangu-r3t1h6r11-petersudais-projects.vercel.app/)
- **Final Project Blog Article**: [CashYangu Project Blog](https://medium.com/@psudai/building-cashyangu-your-personal-finance-tracker-6477c9e11933)
- **Author LinkedIn**: [Peter Sudai](https://www.linkedin.com/in/peter-sudai-3b467313b/)

## Installation

Follow these steps to set up the CashYangu project on your local machine:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/petersudai/CashYangu.git
   cd CashYangu
2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt

4. **Set Up Environment Variables**:
    ```bash
    create a '.env' file in the root directory and add the following variables:
        SECRET_KEY=your_secret_key
        DATABASE_URL=your_database_url

5. **Run Database Migrations**:
    ```bash
    flask db upgrade

6. **Run the Appliccation**:
    ```bash
    flask run


## Usage

Once the application is up and running, you can start using CashYangu by following these steps:

1.Register an Account:

    Navigate to the registration page and create a new account.
2.Log In:

    Use your credentials to log in.
3.Dashboard:

    Access your dashboard to view your financial overview.
4.Log Financial Data:

    Add your earnings, expenses, savings, and budget goals.
5.Generate Reports: 

    Navigate to the Reports section to view detailed financial reports and download CSV Files.

## Contributing

Contributions are welcome! If you have any suggestions or improvements. Just fork the repository, create a new branch, make your changes and commit them. Then push to your fork.
After this open a pull request from your forked repository's feature branch to the main repository's 'main' branch.

## Related Projects

    https://github.com/DennisBauer/RecurringExpenseTracker

    https://github.com/floranguyen0/mmas-money-tracker

    https://github.com/look-after-the-pennies/look-after-the-pennies

## Licensing

CashYangu is under the MIT License.


