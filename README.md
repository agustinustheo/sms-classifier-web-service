# A Web Service for Classifying SMS

A web service containing an Indonesian SMS classifier model. It classifies SMS into 3 categories:
normal message, promotional message and spam message. Built with Django.

The model comes from [sms-classifier-model](https://github.com/agustinustheo/sms-classifier-model), the code for
*SMS Spam Filtering using Machine Learning in Bahasa Indonesia* (EIConCIT 2021,
doi:[10.1109/EIConCIT50028.2021.9431859](https://doi.org/10.1109/EIConCIT50028.2021.9431859)).

## Branches

- **`master`**: modernised (Python 3.12, Django 6, uv, gunicorn).
- **[`original`](../../tree/original)**: the service as it was in 2019 (Django 2.1, commit `6ab9b8f`).

## Run

```bash
uv sync
uv run python manage.py runserver          # development
uv run python manage.py test smsclassifiermodel
```

```bash
curl "http://127.0.0.1:8000/classify/?string=Diskon%2050%25%20semua%20produk%20hari%20ini"
# promo
```

| Endpoint | Response |
|---|---|
| `GET /classify/?string=<text>` | `normal`, `promo` or `spam` (plain text); `400` if `string` is missing |
| `GET /classify/home/` | hello page |
| `/` | Django admin |

Production: `gunicorn smswebservice.wsgi` (see `Procfile`) with these environment variables:

| Variable | Default |
|---|---|
| `DJANGO_SECRET_KEY` | insecure development key, **set this** |
| `DJANGO_DEBUG` | `0` (set `1` for debug) |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,[::1]` (comma-separated) |

## What changed from `original`

- `requirements.txt` (Django 2.1, scikit-learn 0.20 and 40 other pins) replaced by `pyproject.toml` + `uv.lock`.
- The 2019 model pickles no longer load with current scikit-learn. They're replaced by the paper's model: the linear SVM
  from `sms-classifier-model` (master @ `753b682`, trained on all 4,125 messages), with its matching preprocessing and
  1,500-word vocabulary, in `smsclassifiermodel/classifier.py` and `smsclassifiermodel/model/`.
  scikit-learn is pinned to the version that made the pickle.
- The model loads once per process instead of on every request. A missing `string` now returns 400.
- `/classify/` is routed before the admin. Since Django 3.2 the admin's catch-all route would otherwise take it over.
- The secret key, debug flag and allowed hosts come from environment variables. The old key was also removed from the whole git history.
- Removed: the bundled `nltk_data` (its `punkt` pickles are rejected by current NLTK; `punkt_tab` downloads on first use),
  `db.sqlite3`, `__pycache__` folders and the Heroku-specific host.
- `Procfile` runs gunicorn instead of the development server.

## License

[CC BY-SA 4.0](LICENSE). If you use this work, please credit the authors and cite the [paper](https://doi.org/10.1109/EIConCIT50028.2021.9431859).

## Repository history

The whole history (including `original`) was rewritten in November 2026 to remove secrets, `db.sqlite3`, `__pycache__` folders and the third-party Tempo news corpus, and to mask phone numbers in the SMS data and to add the licence
to every commit. Commit hashes before that date no longer exist.
