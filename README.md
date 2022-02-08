# SMEAGOL (Sequence Motif Enrichment And Genome annOtation Library)

Smeagol is a library to identify and visualize enrichment (or depletion) of motifs in DNA/RNA sequences.

## Setup

It is recommended to install in a conda environment or virtualenv. SMEAGOL is compatible with Python 3.7 and higher.

If you have conda installed on your machine you can create a novel virtual environment like this:
```
conda create --name SMEAGOL python=3.7
```

After the installation was successful, you need to activate the created virtual environment before you can install SMEAGOL into it, which can be done as follows:

```
conda activate SMEAGOL
```

### 1. Clone this git repository
```
git clone https://github.com/gruber-sciencelab/SMEAGOL
```

### 2. Install pip dependencies
```
cd SMEAGOL && pip install -r requirements.txt
```

### 3. Install SMEAGOL
```
pip install .
```

### 4. Run tests locally (optional)
```
cd tests
pytest
```


## Usage

In your python script / notebook, you can import modules or functions from SMEAGOL. For example:
```
import smeagol.visualize
```
```
from smeagol.visualize import plot_background
```

## Modules

Smeagol contains the following modules:

- smeagol.matrices: functions to analyze PPMs and PWMs
- smeagol.io: functions to read and write data
- smeagol.models: tensorflow encoding of PWMs 
- smeagol.encode: functions to encode DNA sequences
- smeagol.scan: functions to score binding sites 
- smeagol.enrich: functions to calculate binding site enrichment
- smeagol.variant: functions to predict the effects of sequence variants
- smeagol.visualize: functions to generate plots



## Tutorials

See the [vignette](vignette_1.ipynb) for an example workflow using SMEAGOL.
