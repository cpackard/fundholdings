Progression

Stage 1: Data Exploration

The first challenge was to figure out the types of filings we were dealing with. Having no detailed knowledge of mutual fund filings, we needed to discover:
- What types of forms do we need to parse for holdings information?
- What format are these forms in?
- What happens when we can't find any of the forms we're looking for?

After a little research, it seems that holdings information is mostly contained in these filings:
- 13F-HR and 13F-HR/A (ammendment to an existing 13F-HR)
- N-Q 
- N-CSR(S)

Since N-CSR forms can also contain non-financial information to shareholders, I decided to stick with 13F-HR and N-Q filings to start. 

Starting with 13F-HR filings, these reports were fairly straightforward. While there was some minor namespacing differences between submissions, most reports seemed to follow a standard format, which made parsing holding information as easy as running the filings through an XML parser and extracting the relevant values.

With those out of the way, the parsing of N-Q filings were next. The first few funds I searched weren't too bad: they were giant HTML blobs rather than following a standard XML format, but then I tried searching the TRMCX ticker and came across one of worst things a web crawler can see: images. Instead of text, TRMCX had submitted their holdings as a series of JPG files, which left the following options for parsing them:

- Install a local OCR like tesseract, train the model on several samples
  - Pros: open source, anyone can install
  - Cons: requires several hours of manual work to annotate images for training, have to validate the training was successful and possibly repeat several times
- Use a cloud offering like Google Vision API
  - Pros: easy to use, highly abstract and portable
  - Cons: users need to pay for access, have to setup API keys
- Find another data source 
  - Pros: if another text source can be found, much more reliable than reading text from images
  - Cons: if other sources also use images, could lead down a rabbit hole
  
Since finding another data source was the most pragmatic choice of the three, I set about looking for other sources. Unfortunately, the search was mostly unsuccessful. I tried searching for freely available sources such as Morningstar, Yahoo! Finance, and the funds own websites, but these only listed the Top 10 or Top 25 holdings, and didn't have any historical information on holdings, which makes them very lacking compared to the EDGAR database. While some sources did have APIs for fund holdings, these required hefty licensing fees, and if we're going to be paying then we may as well use a cloud vision API and keep EDGAR as the single, consistent source.


As we progressed through the parsing of N-Q documents in text form, we quickly ran into several problems. While we initially thought them to be in a somewhat consistent format, the following issues arose as we started to flesh out the implementation and look at more examples:
- Securities can span multiple lines
  - As an example, one security group could be US Treasury Bonds, but with many different rates. Since the rates are listed in rows like "25,000  2.875%,05/15/43,  26,309", the parser can't just look at the individual rows and know which holding the security corresponds to.
- Some insitutions report shares, while others report principal
- Inconsistent column ordering
  - Some institutions report "Security Name|Shares|Value", while another may report "Principal|Security Name|Value"
  - Parser would have to have a very robust way to try and guess which columns correspond to which fields
- Value amounts are not consistent
  - Sometimes value is reported in thousands of US Dollars, sometimes not. Additionally, these disclaimers are on separate rows, so the parser would need a lot of extra edge-case checking to detect this.
  
