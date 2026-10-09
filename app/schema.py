from pydantic import BaseModel, Field


class DiabetesInput(BaseModel):
    gender: str = Field(..., examples=["Female"])
    age: float = Field(..., examples=[54])
    hypertension: int = Field(..., ge=0, le=1, examples=[0])
    heart_disease: int = Field(..., ge=0, le=1, examples=[0])
    smoking_history: str = Field(..., examples=["never"])
    bmi: float = Field(..., examples=[27.32])
    HbA1c_level: float = Field(..., examples=[6.6])
    blood_glucose_level: float = Field(..., examples=[80])


class PredictionOutput(BaseModel):
    prediction: int
    probability: float