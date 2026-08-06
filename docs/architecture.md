# Project Architecture

## Overview

This project is a Bag-of-Words + Logistic Regression sentiment classifier
(happiness vs. sadness) for tweets, wired into an MLOps pipeline:

```
raw data --> preprocessing --> feature engineering --> training --> evaluation --> registration --> promotion --> Flask serving
```

## Pipeline stages (DVC-orchestrated, see `dvc.yaml`)

| Stage | Module | Reads | Writes |
|---|---|---|---|
| Data ingestion | `src/data/data_ingestion.py` | remote CSV | `data/raw/{train,test}.csv` |
| Preprocessing | `src/data/data_preprocessing.py` | `data/raw` | `data/interim/{train,test}_processed.csv` |
| Feature engineering | `src/features/feature_engineering.py` | `data/interim` | `data/processed/{train,test}_bow.csv`, `models/vectorizer.pkl` |
| Model building | `src/model/model_building.py` | `data/processed` | `models/model.pkl` |
| Model evaluation | `src/model/model_evaluation.py` | `models/model.pkl`, `data/processed` | `reports/metrics.json`, `reports/experiment_info.json`, logs to MLflow |
| Model registration | `src/model/register_model.py` | `reports/experiment_info.json` | registers a model version in MLflow, stage=Staging |

`scripts/promote_model.py` runs after CI tests pass and promotes the latest
registered version to `Production` (archiving the prior production
version).

## Shared modules

- `src/config/config.py` — every path, constant, and environment-derived
  setting (MLflow tracking URI, DagsHub repo, random seed, registered
  model name, stage names, etc.) lives here.
- `src/logger.py` — one logger factory used by every stage; writes to
  `logs/<module>.log` plus the console.
- `src/exceptions.py` — one exception type per pipeline stage so failures
  are traceable to their source.
- `src/features/text_processing.py` — the single implementation of text
  normalization (lower-casing, stop-word removal, punctuation/URL/number
  stripping, lemmatization) used identically by the offline pipeline and
  the Flask app, preventing training/serving skew.
- `src/visualization/visualize.py` — confusion matrix and classification
  report generation, writing into `reports/`.

## Serving

`flask_app/app.py` loads the current highest-versioned model from the
MLflow Model Registry (`models:/<name>/<version>`) plus the fitted
vectorizer from `models/vectorizer.pkl`, and exposes a single form for
interactive predictions at `/predict`.

## Experiment tracking

MLflow tracking is hosted on DagsHub. Authentication uses the
`DAGSHUB_PAT` environment variable (loaded from `.env` locally, or from a
repository secret in CI) via `src.config.config.configure_mlflow_tracking()`.

## Data & model versioning

Datasets and pickled artifacts (`models/*.pkl`) are tracked with DVC, not
Git — see `.gitignore` and `dvc.yaml`. Only code, configuration, and DVC
metadata files (`.dvc`, `dvc.lock`) are committed to Git.
