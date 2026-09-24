# Data Source & Provenance

## Official Dataset Provenance

- **Repository**: UCI Machine Learning Repository
- **Dataset Title**: Online Retail II
- **DOI**: [10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D)
- **Direct Archive URL**: `https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip`
- **Citation**:
  ```bibtex
  @misc{online_retail_ii_502,
    author       = {Chen, Daqing},
    title        = {{Online Retail II}},
    year         = {2019},
    howpublished = {UCI Machine Learning Repository},
    doi          = {10.24432/C5CG6D}
  }
  ```
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Local Storage Path**: `data/raw/online_retail_II.xlsx`
- **File Size**: ~45.6 MB (43.51 MB compressed)
- **Total Records**: 1,067,371 rows across two sheets:
  - `Year 2009-2010`: 525,461 rows
  - `Year 2010-2011`: 541,910 rows

---

## Domain Interpretation & Scope

The dataset documents all transaction records occurring between **December 1, 2009 and December 9, 2011** for a UK-based registered non-store online retail merchant. The company primarily sells unique all-occasion giftware. Many of the customers are commercial wholesalers, corporate gift buyers, and international retailers.

### Official Field Definitions:
1. **`Invoice` (`invoice_no`)**: A 6-digit integral number uniquely assigned to each transaction. If the code begins with the letter 'C', it denotes an explicit cancellation.
2. **`StockCode` (`stock_code`)**: A 5-digit integral or alphanumeric code uniquely assigned to each distinct product or item line.
3. **`Description` (`description`)**: Nominal product/item specification name.
4. **`Quantity` (`quantity`)**: The quantities of each product (item) per transaction. Numeric. Negative values indicate cancellations, returns, or inventory damage adjustments.
5. **`InvoiceDate` (`invoice_date`)**: The day and minute when each transaction was generated.
6. **`Price` (`unit_price`)**: Unit product price in Sterling (£). Numeric.
7. **`Customer ID` (`customer_id`)**: A 5-digit integral number uniquely assigned to each registered customer account.
8. **`Country` (`country`)**: Nominal name of the sovereign territory where the billing customer resides.
