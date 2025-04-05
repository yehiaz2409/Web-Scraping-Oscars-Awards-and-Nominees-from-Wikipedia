# Web-Scraping-Oscars-Awards-and-Nominees-from-Wikipedia

This project is a full data scraping, cleaning, and database integration pipeline built to analyze historical data from the Academy Awards (Oscars). It scrapes data from Wikipedia, processes and normalizes it, and stores it in a structured MySQL database for further analysis or application use.

---

## 📁 Project Structure

### 🔍 Web Scraping (Scrapy Spiders)

- `nominations`: Scrapes all 1st–96th Academy Awards nominees and winners, capturing:
  - Category
  - Iteration
  - Nominee name (person or movie)
  - Winner status
  - Movie/nominee URLs
- `movies`: Uses `movies_urls` to extract detailed movie info:
  - Movie name, release date, language, runtime, production company
  - Director name, director birthdate
- `movie_crew`: Extracts crew per movie (actors, producers, director), including:
  - Name, role, birthdate (from their own Wikipedia pages)
- `director_dob`: Optional spider for extracting director DOBs from URLs
- `missing_oscars`: Special spider for handling iterations 18–49 with a different layout

---

## 🧹 Data Cleaning and Normalization

After scraping:
- JSON files are transformed into normalized CSVs
- Non-ASCII characters are converted or removed
- Empty fields are replaced with `NULL`
- Dates are converted to SQL `DATE` format (`YYYY-MM-DD`)
- Deduplication and null filtering is performed

---

## 🗃️ Database Schema (MySQL)

```sql
Crew(name, date_of_birth, country, death_date)
Movie(movie_name, release_date, language, run_time, production_company)
movie_crew(name, date_of_birth, movie_name, release_date, role)
User(username, email, age, birth_date, gender, country)
Nomination(nom_id, cat_name, user_added, granted, num_of_votes)
nominated_for(nom_id, iteration, movie_name, release_date, name, date_of_birth)
user_nomination(username, nom_id)
```

### ✅ Notes:
- Composite keys used for relations (e.g. `Crew`, `Movie`)
- Foreign keys enforced to maintain referential integrity

---

## 🛠️ Technologies Used

- **Python**, **Scrapy** – for web scraping
- **Pandas**, **JSON**, **CSV** – for data transformation
- **MySQL** – relational database for structured storage
- **MySQL Workbench** – GUI for importing CSVs and running queries

---

## 📌 Importing to MySQL

Make sure:
- All CSVs are cleaned and ASCII-compatible
- Dates are in `YYYY-MM-DD` format
- Boolean fields like `granted`, `user_added` are converted to `0/1`
- Foreign key types (e.g. `nom_id`) match across all tables

Use MySQL Workbench → Table → Import CSV to insert into tables.

---

## 👤 Sample Users (for testing)

```sql
INSERT INTO User (username, email, age, birth_date, gender, country) VALUES
('alice', 'alice@example.com', 30, '1994-01-10', 'Female', 'USA'),
('bob', 'bob@example.com', 27, '1996-06-18', 'Male', 'Canada'),
('charlie', 'charlie@example.com', 22, '2002-03-30', 'Other', 'UK');
```

---

## 📂 Final CSV Files (Examples)

- `crew.csv`
- `movie_crew.csv`
- `Extracted_Movie_Info_Cleaned.csv`
- `nomination.csv`
- `nominated_for.csv`
- `user.csv`
- `user_nomination.csv`

---

## 🚀 Status

✅ Fully Scraped  
✅ Cleaned and Normalized  
✅ MySQL Database Ready  
🔜 Potential for Web App or Data Analytics Layer

---

## ❌ Limitations

- Not all people were scraped due to different date of birth formats
