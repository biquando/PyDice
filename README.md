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

## Running PyDice
```
usage: python src/PyDice.py [-h] [--bdd] [-n NUM_ITS] [input_file]

positional arguments:
  input_file            input file

options:
  -h, --help            show this help message and exit
  --bdd                 enable bdd computation
  -n, --num-its NUM_ITS
                        number of sampling iterations (default 10000)
```

## Adding a new distribution

To add a custom probability distribution, you only need to create a new
python file in `src/distributions/` that contains a class inheriting from
`CustomDistribution`. See `uniform.py` for an example.
