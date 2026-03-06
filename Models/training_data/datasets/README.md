# Training Datasets

This directory is intended for storing training datasets.

Currently, the primary training data consists of all `.qentl` files located in the `../../QEntL/` directory. The training script `../../training_scripts/qentl_unified_training_system.py` reads them directly from their source location. This approach ensures that we are always training on the most up-to-date version of our codebase.

Future datasets, such as processed Yi-language PDFs or web-scraped data, will be stored here. 