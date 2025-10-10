# Bengaluru House Price Prediction 🏠

![Python](https://img.shields.io/badge/Python-3.7%2B-blueviolet)
![Django](https://img.shields.io/badge/Django-3.2%2B-green)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-0.24%2B-orange)

A full-stack web application that predicts house prices in Bengaluru using a machine learning regression model. This project provides a user-friendly interface to get instant, data-driven property valuations.

## 🚀 Demo

Here's a look at the prediction interface. The first image shows the empty form, and the second demonstrates an example input with a predicted price.

### Prediction Form
![Empty Prediction Form](./Screenshot%20(425).png)

### Predicted Price Example
![Predicted Price Example](./Screenshot%20(426).png)


---

## ✨ Features

- **Accurate Price Prediction:** Utilizes a machine learning model to provide realistic property valuations.
- **Interactive UI:** A clean and modern user interface for easy input of property features.
- **Comprehensive Feature Set:** The model considers a wide range of factors including:
  - Location
  - Square Feet
  - Property Type & BHK
  - Age of Property & Condition
  - Floor Level, Amenities, and Connectivity
- **Real-time Results:** Get an instant price estimate upon entering the details.

---

## 💻 Tech Stack

- **Backend:** Python, Django
- **Machine Learning & Data Science:** Scikit-learn, Pandas, NumPy, Jupyter Notebook
- **Frontend:** HTML, CSS, JavaScript

---

## 🤖 Machine Learning Model

The core of this project is the regression model, which was built following the complete data science lifecycle.

1.  **Data Collection:** The model was trained on the "Bengaluru House Price Data" dataset from Kaggle.
2.  **Data Cleaning & Preprocessing:** Performed extensive data wrangling, handled missing values, and corrected inconsistent data types.
3.  **Feature Engineering & Outlier Removal:** Created new features like `price_per_sqft` for analysis and implemented a multi-step outlier removal process using both business logic (e.g., sqft per bedroom) and statistical methods (standard deviation).
4.  **Model Training & Selection:** Systematically evaluated multiple algorithms (Linear Regression, Lasso, etc.) using `GridSearchCV` and selected the best-performing model for deployment.
5.  **Export:** The final model was exported as a `pickle` file for integration into the Django backend.

---

## 🛠️ Installation & Setup

To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/SHANID/Real-Estate-Price-Prediction.git](https://github.com/SHANID/Real-Estate-Price-Prediction.git)
    cd Real-Estate-Price-Prediction
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Django development server:**
    ```bash
    python manage.py runserver
    ```

5.  **Open your browser** and navigate to `http://12.0.0.1:8000/`.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

SHANID – [Mailto](mailto:shanidpsha@gmail.com)

Project Link: [https://github.com/SHANID/Real-Estate-Price-Prediction](https://github.com/SHANID/Real-Estate-Price-Prediction)
