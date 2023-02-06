# veryfi_code_challenge
This repository contains my rendition of the code challenge provided and all its related files.

1. [Setup](#Setup-)
2. [Running the notebook](#running-the-notebook-)
3. [Using the CLI](#using-the-cli-)
4. [Testing](#Testing-)
---

## Setup [↑](#contents) 
* Create a virtualenv: `python -m venv virtualenv` and activate it `. virtualenv/bin/activate`.
* Install the dependencies: `pip install -r requirements.txt`.
## Running the notebook [↑](#contents) 
The notebook `rendition.ipynb` describes all and any assumptions made during the development of this challenge. There's 2 ways of running it:
* Via VS Code: Download the extension `Jupyter` within the marketplace.
* Running a Jupyter server: The resulting environment from following the steps in the [Setup](#Setup-) has all the dependencies required. On a terminal with the environment activated run `jupyter notebook`.
## Using the CLI [↑](#contents) 
To run this project with single files or a batch of JSON inputs, go to the root folder and run the command:  

`python src -b [-f [<file_name>]]`  

Where:  

-b &ensp;&ensp;&ensp;Extracts in batch every file within the folder ocr/  
-f &ensp;&ensp;&ensp; Is the filename for the JSON in ocr/ e.g. ticket1.json
## Testing [↑](#contents) 
This project uses `pytest` for its unit tests, to execute them run the command `pytest tests/`.