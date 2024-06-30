# Expense generator from Deutsche Bank pdf reports

Deutsche Bank's mobile apps don't provide a good way to sort
expenses by category. Yes, there is some basic functionality - but
this functionality doesn't work very well. Perhaps this happens
in my case, but no less.

Fortunately, every month Deutsche Bank sends a **Kontoauszug**
(statement of account) which contains all transactions for
the previous month.

I created a small service that generates the expense report by
categories in excel format based on Kontoauszug PDF files sent
by Deutsche Bank.

![report](./img/report.png)
