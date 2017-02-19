EDGAR Fund Holdings Scraper
==================================
This package implements a web scraper in Python that can parse and format mutual fund holdings pulled from EDGAR, the SEC's open-access repository for company financial reporting. Since the format of company's reports can vary, the goal of this project is to extract this information and present it in a single, consistent format for anyone to use.

## Table of Contents:
- [Quickstart](#quickstart)
- [Project Structure](#project-structure)
- [Tests and Coverage](#tests-and-coverage)
- [Assumptions and Notes](#assumptions-and-notes)
- [Final Thoughts](#final-thoughts)

## Quickstart
Running the scraper requires Python 3, pip, and optionally (but recommended) virtualenv.
```bash
$ virtualenv -p `which python3` holdings && source holdings/bin/activate
$ pip install -r requirements.txt
$ python -m holdings.main ticker_or_cik
```
As an example, lookup the holdings for the Vanguard Institutional Index Funds:
```bash
$ python -m holdings.main viiix
Reports successfully generated and can be found in:
reports/0000862084_S000002853_2016_11_30.txt
reports/0000862084_S000002855_2016_11_30.txt
```
Reports have the naming convention: CIK_SERIESID_FILING_DATE.txt

## Project Structure
- **holdings:** The source of the application
  - *main* Acts as the manager of the other modules, the entry point of the application.
  - *web* Contains all generic web scraping specific not coupled with a particular report.
  - **dto:** Data Transfer Objects, representations of the various SEC forms
    - *base* Base classes common to all reports
    - *report13fhr* Parsing and representation of 13F-HR forms
    - *reportnq* Parsing and representation of N-Q forms
- **tests:** All testing for the application
  - *test_functional* Functional tests, complete end-to-end flow of the application
  - *test_holdings_web* Testing for the web module
  - *test_13fhr_report* Testing for the report13fhr module
  - *test_nq_report* Testing for the reportnq module
- **resources:** Container for any resources needed for testing

## Tests and Coverage
All unit tests can be run with the following command:
```bash
$ python -m unittest
```
To test a specific module:
```bash
$ python -m unittest tests.test_functional
```

**Coverage:** Currently test coverage for the application is 85%. A detailed report can be found in htmlcov/index.html

## Assumptions and Notes
While the original scope of the project was broad and ambitious, as I learned more about the data the parser was working with I had to make some pragmatic tradeoffs on application complexity vs supported features. Below is a deatiled progression of the exploration process, but as a brief summary:
- **Supported:**
  - Searching for a ticker or CIK through the EDGAR search page
  - Parsing and generating tab-delimited holdings reports for 13F-HR forms
  - Parsing and generating tab-delimited holdings reports for N-Q reports whose holdings are reported on single rows
  - Graceful error handling as exceptions arise
- **Unsupported:**
  - Parsing of N-Q reports whose holdings span multiple lines, or whose holdings are reported as a series of images rather than text
  - Searching for holding reports later than the most recent copy
  
### Stage 1: Data Exploration

The first challenge was to figure out the types of filings the application had to interpret. Having no detailed knowledge of mutual fund filings, I needed to discover:
- What types of forms does the app need to parse for holdings information?
- What format are these forms in?
- What happens when the app can't find any of the forms it's looking for?

After a little research, it seems that holdings information is mostly contained in these filings:
- 13F-HR and 13F-HR/A (ammendment to an existing 13F-HR)
- N-Q 
- N-CSR(S)

Since N-CSR forms can also contain non-financial information to shareholders, I decided to stick with 13F-HR and N-Q filings to start. 

### Stage 2: Data Modeling
While the format of the reports can vary from company to company, there was a core model that was shared among all:

- **Holding:** All holdings have the following properties at a minimum:
  - *entity* The name of the security
  - *shares* The number of shares
  - *value* The value of those shares at the time of filing
  
- **SECForm:** All SEC forms have the following metadata:
  - *cik* The Central Index Key, a unique identifier for institutions
  - *accepted_date* The date the report was accepted
  - *submission_type* Whether the form is an N-Q, 13F-HR, etc.
  
With these core classes defined, they can serve as a common base and extend them to support specific reports while keeping a consistent format.

### Stage 3: Implementation

Starting with 13F-HR filings, these reports were fairly straightforward. While there was some minor namespacing differences between submissions, most reports seemed to follow a standard format, which made parsing holding information as easy as running the filings through an XML parser and extracting the relevant values.

With those out of the way, the parsing of N-Q filings were next. The first few funds I searched weren't too bad: they were giant HTML blobs rather than following a standard XML format, but then I tried searching the TRMCX ticker and came across one of worst things a web crawler can see: images. Instead of text, TRMCX had submitted their holdings as a series of JPG files, which left the following options for parsing them:

- *Install a local OCR like tesseract*, train the model on several samples
  - Pros: open source, anyone can install
  - Cons: requires several hours of manual work to annotate images for training, have to validate the training was successful and possibly repeat several times
- *Use a cloud offering like Google Vision API*
  - Pros: easy to use, highly abstract and portable
  - Cons: users need to pay for access, have to setup API keys
- *Find another data source*
  - Pros: if another text source can be found, much more reliable than reading text from images
  - Cons: if other sources also use images, could lead down a rabbit hole
  
Since finding another data source was the most pragmatic choice of the three, I set about looking for other sources. Unfortunately, the search was mostly unsuccessful. I tried searching for freely available sources such as Morningstar, Yahoo! Finance, and the funds own websites, but these only listed the Top 10 or Top 25 holdings, and didn't have any historical information on holdings, which makes them very lacking compared to the EDGAR database. While some sources did have APIs for fund holdings, these required hefty licensing fees, and if I'm going to be paying then I may as well use a cloud vision API and keep EDGAR as the single, consistent source.

As I progressed through the parsing of N-Q documents in text form, I quickly ran into several problems. While I initially thought them to be in a somewhat consistent format, the following issues arose as I started to flesh out the implementation and look at more examples:
- *Securities can span multiple lines*
  - As an example, one security group could be US Treasury Bonds, but with many different rates. Since the rates are listed in rows like "25,000  2.875%,05/15/43,  26,309", the parser can't just look at the individual rows and know which holding the security corresponds to.
- *Some insitutions report shares, while others report principal*
- *Inconsistent column ordering*
  - Some institutions report "Security Name|Shares|Value", while another may report "Principal|Security Name|Value"
  - Parser would have to have a very robust way to try and guess which columns correspond to which fields
- *Value amounts are not consistent*
  - Sometimes value is reported in thousands of US Dollars, sometimes not. Additionally, these disclaimers are on separate rows, so the parser would need a lot of extra edge-case checking to detect this.
 
Since the application complexity would increase exponentially if these issues were addressed, I decided to not support them at this time. Instead, I focused on an intial data model for N-Q reports that would be consistent across them all, and could address these issues in future iterations if time allows.

## Final Thoughts
This project was a great exploration both in financial domain knowledge as well as the techical side of web scraping. It does an excellent job of demonstrating that complexity in a web scraper can quickly climb, and that the developer needs to build their applications with robustness from the start to handle these challenges as they arise.
