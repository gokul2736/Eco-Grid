import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import pickle

def train_model():
    print("Training AI Model...")
    try:
        df = pd.read_csv("eco_grid_data.csv")
    except FileNotFoundError:
        print("❌ Error: Run data_generator.py first!")
        return

    # Feature Engineering: Calculate 'Power Change'
    df['Power_Change'] = df['Total_Power_W'].diff().fillna(0)

    X = df[['Power_Change']]
    y = df['True_Label']

    # Train Decision Tree
    model = DecisionTreeClassifier()
    model.fit(X, y)

    # Save Model
    with open('nilm_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("✅ Model Trained & Saved: nilm_model.pkl")

if __name__ == "__main__":
    train_model()