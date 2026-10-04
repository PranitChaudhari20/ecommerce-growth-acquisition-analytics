# Raw data — sources, licences and integrity

**Author of this project: Pranit Ajay Chaudhari.**
**I did not create either dataset.** Both are public datasets published by other people. They are
included here as the exact prepared inputs used by the project. Two Olist files are privacy-scrubbed
before publication as documented below; all credit and all rights remain with the original publishers.

---

## Part A — Brazilian E-Commerce Public Dataset by Olist

| | |
|---|---|
| **Publisher** | Olist Store (Brazil), released publicly via Kaggle |
| **Licence** | CC BY-NC-SA 4.0 |
| **Content** | ~100,000 real orders placed on the Olist marketplace, Sep 2016 – Oct 2018 |
| **Obtained from** | Public GitHub repository `dujiaying/olist`, folder `data/` |
| **Date obtained** | 1 October 2026 |
| **Anonymisation** | Olist anonymised the data before release: customer, seller and product identifiers are random hashes, and company names are replaced with Game of Thrones house names |

**Provenance check.** Five of the eight files were byte-compared against a second, unrelated public
repository (`xor9237/brazil_ecommerce`) and were **identical**, which is reasonable evidence these
are the genuine published files rather than someone's edited copy.

| File | Rows | SHA-256 |
|---|---|---|
| `olist_orders_dataset.csv` | 99,441 | `8df58ef3d2d7e9944010f7beecd9b75367f5588ec6e3c91cec19ae3345ef9ecf` |
| `olist_customers_dataset.csv` | 99,441 | `983a422239e1712ded753b3bf9ecf47dc73f144d306029dcfa99e70a226883d2` |
| `olist_order_items_dataset.csv` | 112,650 | `0bc4d068c4fe38cbb01bd90e8746e3c613fe7b4baef75fab7b0e329701c3e279` |
| `olist_order_payments_dataset.csv` | 103,886 | `4f713964f2815dbbaa40b9488268c55aac3627bfce5aa96cf58d1f3616de3cc0` |
| `olist_order_reviews_dataset.csv` | 100,000 | original `0dff69f6fed33a13648020198ea94d7ae12afbdd4904186c6cd904e27a3e1ccd` · **prepared `ab1fd08cccdb570097d25740982645269834c9c7b9472b3989c3e710d01f8128`** |
| `olist_products_dataset.csv` | 32,951 | `3e6569628a17fbc75fd206ee357b59e20364b9afa90f5b6cd5b4d624c58aa9cc` |
| `olist_sellers_dataset.csv` | 3,095 | original `1f643d2b950373b85735e7794b20986f528d7a000432e7c6f9bcbb44d0846a0e` · **prepared `bea554a0732e030a4c3d17b4d0123c00dd32d3286db4ba79c7b4d3e6a6432fef`** |
| `product_category_name_translation.csv` | 71 | `a81f0d1f27b27e7293f761bc79e3ce8f348ee39c4b3ed3e49bde38f478586278` |

## Two files are modified before publication, and here is exactly why

**The published Olist data contains real email addresses.** Olist anonymised its identifiers, but
free-text fields were never scrubbed, and customers typed contact details into them. A scan of the
raw download found **nine real email addresses** — several clearly personal accounts — eight inside
review comments and one in a seller's city field.

Republishing other people's personal data on a public repository would be wrong, and here it costs
nothing analytically, because **this project never uses the comment text**: it reads `review_score`
and nothing else. `review_comment_title` and `review_comment_message` are not referenced in a single
script, query or formula.

So `python/00_prepare_raw.py` removes those two columns from the committed reviews file and masks
the one affected `seller_city` value. The script re-scans every raw file afterwards and refuses to
pass if any address remains. Both the **original** and the **prepared** SHA-256 are listed above, so
anyone can download the original, verify it, run the same script and reproduce the committed file
byte for byte.

**A counting trap in the original reviews file.** As published it has **105,764 lines but 100,000
records**, because review comments contain embedded newlines — counting lines instead of parsing the
CSV overstates reviews by 5.8%. The prepared copy has no comment text, so it has 100001 lines
for the same 100,000 records. `01_clean_partA.py` parses the file properly either way.

**Files deliberately not included.** The dataset also ships `olist_geolocation_dataset.csv` (61 MB)
and two marketing-funnel tables. Geolocation is not used — state and city come from the customers
table — and the funnel tables describe **sellers** being recruited to the marketplace, not consumer
marketing, so they do not belong in a customer-analytics project. Committing 61 MB of unused data
would be noise, so they were left out rather than shipped unused.

---

## Part B — Marketing Campaign / Customer Personality dataset

| | |
|---|---|
| **Content** | 2,240 customers of a retailer, with two years of category spend, purchase counts by channel, demographics, and the outcome of five marketing campaigns plus a sixth most recent one |
| **Format** | Tab-separated despite the `.csv` extension |
| **Obtained from** | Public GitHub repository `arienugroho050396/Customer-Personality-Analysis` |
| **Date obtained** | 1 October 2026 |
| **Original publication** | Circulated widely on Kaggle as "Customer Personality Analysis" / "Marketing Campaign". The underlying company is not named in the file and I make no claim about who it is |

| File | Rows | SHA-256 |
|---|---|---|
| `marketing_campaign.csv` | 2,240 | `cd0affa36b1b981e80ba0e27767e9b3ab723f7a3dba948f722af81abc6b990ea` |

**Known quality problems**, all handled explicitly in `02_clean_partB.py` and logged:
182 duplicate customer records, 24 missing incomes, one income of 666,666, three birth years
implying ages over 100, and four records whose marital status reads `Absurd` or `YOLO`.

---

## Reproducing the download

```bash
git clone --depth 1 https://github.com/dujiaying/olist.git
cp olist/data/olist_{orders,customers,order_items,order_payments,order_reviews,products,sellers}_dataset.csv data/raw/
cp olist/data/product_category_name_translation.csv data/raw/

git clone --depth 1 https://github.com/arienugroho050396/Customer-Personality-Analysis.git
cp Customer-Personality-Analysis/marketing_campaign.csv data/raw/

python python/00_prepare_raw.py          # strip the personal data (see above) - do this before committing
sha256sum -c data/raw/SHA256SUMS.txt     # confirm you now have the same files this project was built on
```
