# Runbook: Diabetes Prediction API

This runbook provides operational guidance for maintaining, troubleshooting, and updating the Diabetes Prediction API.

## 🚀 Quick Start
### Local Execution
1. Activate environment: `.\.venv\Scripts\Activate.ps1`
2. Start server: `uvicorn app.main:app --reload`
3. Health check: `curl http://127.0.0.1:8000/health`

### Deployment
1. Build image: `docker build --platform linux/amd64 -t diabetes-api .`
2. Push to ECR (see README.md for full commands).
3. Update Lambda function to use the latest image.

## 🛠 Maintenance
### Updating the Model
To retrain the model with new data:
1. Update the dataset in `train/`.
2. Run training script: `python train/train.py`.
3. Verify model accuracy in the output.
4. Commit the new `.pkl` and `.json` artifacts (if not gitignored) or ensure they are bundled into the Docker image during the next build.
5. Redeploy the container to AWS Lambda.

### Monitoring & Logs
- **AWS CloudWatch**: Check `/aws/lambda/<function-name>` for application logs and error traces.
- **Health Endpoint**: Periodically check `GET /health` to ensure the service is responsive.

## 🚨 Troubleshooting
| Symptom | Likely Cause | Resolution |
| :--- | :--- | :--- |
| `502 Bad Gateway` | Lambda Web Adapter failure or app crash | Check CloudWatch logs for Python tracebacks. |
| `422 Unprocessable Entity` | Invalid request body | Verify request JSON matches the Pydantic schema in `app/schema.py`. |
| Slow Inference | Cold start or resource constraints | Increase Lambda memory allocation or use Provisioned Concurrency. |
| Inaccurate Predictions | Data drift or outdated model | Retrain the model using `train/train.py` with recent data. |

## 📁 Key Files Reference
- `app/main.py`: API entry point and routes.
- `app/schema.py`: Request/Response data models.
- `train/train.py`: Model training and artifact generation logic.
- `Dockerfile`: Container configuration for AWS Lambda.
