import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Memuat dataset
df = pd.read_csv('final_dataset.csv')

# Input dan Target
X = df.drop('Sleep Disorder', axis=1)
y = df['Sleep Disorder']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

with mlflow.start_run():
    mlflow.autolog()

    # Inisialisasi dan training model
    rf = RandomForestClassifier(random_state=42)
    rf.fit(X_train, y_train)

    # Logging model
    input_example = X_train.iloc[:1]  # contoh input
    mlflow.sklearn.log_model(
        sk_model=rf,
        artifact_path="model",
        input_example=input_example
    )
