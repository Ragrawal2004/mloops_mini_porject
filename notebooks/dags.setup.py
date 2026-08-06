import mlflow
import dagshub

mlflow.set_tracking_uri("https://dagshub.com/Ragrawal2004/mloops_mini_porject.mlflow")


dagshub.init(repo_owner='Ragrawal2004', repo_name='mloops_mini_porject', mlflow=True)


with mlflow.start_run():
  mlflow.log_param('parameter name', 'value')
  mlflow.log_metric('metric name', 1)