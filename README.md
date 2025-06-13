# PyDice

## Setup

```bash
# Set up python virtual environment
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest
```

## Adding a new distribution

To add a custom probability distribution, you only need to create a new
python file in `src/distributions/` that contains a class inheriting from
`CustomDistribution`. See `uniform.py` for an example.
