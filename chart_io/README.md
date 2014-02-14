# Chart.io Dashboard Retriever
## Motivation
As much as [Chart.io](http://chart.io) rocks, there is always room for improvement. At Ginger.io, we wanted to distribute a weekly sales report with one page per account. In Chart.io, I had set up a dashboard with a global filter for selecting an account. The report could have been created manually: select an account, wait for dashboard to refresh, save the PDF, and rinse and repeat for each account. Instead, I decided to automate the process using Python, WebDriver, and PhantomJS.

## Example
Once you've added the `chartio.py` file to your project, here's an example of how easy it is to use:
````
from .chartio import ChartioDashboardRetriever

chartio = ChartioDashboardRetriever(CHARTIO_USERNAME, CHARTIO_PASSWORD)
pdf = chartio.get_pdf_for_dashboard(CHARTIO_DASHBOARD_URL, ["Account 1", "Account 2"])
````
You can then save the PDF as a file or attach it to an email.

## Requirements
You'll need to have the following installed on your machine for this to work:
* Unix packages `libicu48`, `libjpeg-dev`, and `fontconfig`
* Python packages `Pillow`, `PyPDF2`, and `selenium`
* PhantomJS binary

Here's the code I used to install these on a 32-bit Ubuntu machine:
````
sudo apt-get install libicu48 libjpeg-dev fontconfig

curl -s https://phantomjs.googlecode.com/files/phantomjs-1.9.2-linux-i686.tar.bz2 | sudo tar xfj - --strip-components 2 -C /usr/bin phantomjs-1.9.2-linux-i686/bin/phantomjs

pip install Pillow==2.3.0 PyPDF2==1.19 selenium==2.31.0
````
Note that the long `curl` command simply places a copy of the `phantomjs` binary into `/usr/bin`.
