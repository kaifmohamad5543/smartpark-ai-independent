from pathlib import Path

import app.ml.generate_dataset as generator


EVALUATION_SEED = 2026
EVALUATION_ROWS = 2500

EVALUATION_PATH = Path(
    "data/evaluation/parking_demand_evaluation_v2.csv"
)


def generate_evaluation_dataset():
    original_seed = generator.RANDOM_SEED
    original_rows = generator.NUMBER_OF_ROWS
    original_path = generator.OUTPUT_PATH

    try:
        generator.RANDOM_SEED = EVALUATION_SEED
        generator.NUMBER_OF_ROWS = EVALUATION_ROWS
        generator.OUTPUT_PATH = EVALUATION_PATH

        dataset = generator.generate_dataset()

    finally:
        generator.RANDOM_SEED = original_seed
        generator.NUMBER_OF_ROWS = original_rows
        generator.OUTPUT_PATH = original_path

    print(
        "\n===== INDEPENDENT SYNTHETIC EVALUATION SET ====="
    )
    print(f"Seed: {EVALUATION_SEED}")
    print(f"Rows: {len(dataset)}")
    print(f"Output: {EVALUATION_PATH}")
    print(
        "Location-code feature present:",
        "parking_location" in dataset.columns
    )


if __name__ == "__main__":
    generate_evaluation_dataset()
