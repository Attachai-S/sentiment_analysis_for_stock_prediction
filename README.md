### This repository is for education purposes only!!!

### Project pipline or project implement

0. Project understanding
1. News collection (get news article data)
2. Text processing
3. Sentiment scoring
4. Stock price collection (get stock data)
5. Data preparation (feature enginering)
6. Machine Learning model
7. Evaluation

---

### 0. Project understanding
    
This project is developed for CP465 Text Mining at Srinakharinwirot University (SWU). The objective is to conduct sentiment analysis on news articles and their content to generate sentiment scores, which are subsequently integrated with stock market data for machine learning-based stock price prediction modeled as a classification problem.

---

### 1. New colletion

to get News article and their content we use 2 method as 
 
 - **1.1 API**    : use API from free source (NewsAPI etc.)
 
 - **1.2 Web scrapping** : develop source code for scapping content from authorize website (GoogleNews etc.) 

---

### 3. Sentiment Scoring

Pre-trained models are used to generate sentiment scores for each article, which are then stored for model training.

---

### 4. Stock price collection 

Retrieve historical stock price data from free sources such as Yahoo Finance to integrate with sentiment analysis results. All stock symbols used in this project are from the technology sector:

    - AAPL : Apple Corp.
    - CSCO : Cisco Systems, Inc. Common Stock. (DE)
    - INTC : Intel Corp.
    - MSFT : Microsoft Corp.
    - NVDA : Nvidia Corp.
    - ORCL : Oracle Corp.

---

### 5. Data preparation

Apply data science methodologies including feature engineering and normalization to prepare datasets for machine learning model training.

---

### 6. Machine learning model 

Train classification models using prepared features to predict stock price movements based on sentiment scores and historical data.

 ---

 ### 7. Evaluation 

Evaluate model performance using metrics such as accuracy, precision, recall, and F1-score. Validate results on test datasets and compare against baseline models to assess prediction effectiveness.

---

### library for import 
 - pip install requests
 - pip install pandas