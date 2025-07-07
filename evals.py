import pandas as pd
from datasets import load_dataset
from sklearn.metrics import accuracy_score, classification_report
from tqdm import tqdm
from loguru import logger

from mri_swarm.mri_agents import mri_swarm


def evaluate_mri_swarm():
    """
    Evaluate the MRI-Swarm system on the brain tumor MRI dataset.
    """
    # Load dataset
    logger.info("Starting MRI-Swarm evaluation")
    logger.info("Loading brain tumor MRI dataset...")
    ds = load_dataset("Simezu/brain-tumour-MRI-scan", split="test")
    logger.info(f"Dataset loaded successfully. Size: {len(ds['train'])} samples")

    # Initialize results storage
    predictions = []
    true_labels = []

    # Run evaluation
    logger.info("Beginning evaluation loop...")
    for idx, sample in enumerate(tqdm(ds["train"])):
        logger.debug(f"Processing sample {idx + 1}/{len(ds['train'])}")

        # Get image and true label
        image = sample["image"]
        label = sample["label"]
        logger.debug(f"Sample {idx + 1} true label: {label}")

        try:
            # Run MRI-Swarm analysis
            logger.debug(f"Running MRI-Swarm analysis for sample {idx + 1}")
            analysis = mri_swarm(
                task="Analyze this brain MRI scan and determine if there is a tumor present. "
                "Respond with exactly 'tumor' or 'no-tumor' as the first line of your response.",
                img=image,
            )

            # Extract prediction from analysis
            pred = "tumor" if "tumor" in analysis.lower().split("\n")[0] else "no-tumor"
            pred_label = 1 if pred == "tumor" else 0
            logger.debug(f"Sample {idx + 1} prediction: {pred} (label: {pred_label})")

            # Store results
            predictions.append(pred_label)
            true_labels.append(label)

            # Log prediction correctness
            is_correct = pred_label == label
            logger.info(
                f"Sample {idx + 1} - Prediction: {pred}, True Label: {label}, "
                f"Correct: {is_correct}"
            )

            # Save intermediate results every 10 samples
            if (idx + 1) % 10 == 0:
                logger.info(f"Saving intermediate results at sample {idx + 1}")
                save_results(predictions, true_labels)

        except Exception as e:
            logger.error(f"Error processing sample {idx + 1}: {str(e)}")
            logger.exception("Full traceback:")
            continue

    # Calculate final metrics
    logger.info("Evaluation complete. Calculating final metrics...")
    print_metrics(predictions, true_labels)
    logger.info("Evaluation pipeline finished successfully")


def save_results(predictions, true_labels):
    """Save intermediate results to a CSV file."""
    try:
        results_df = pd.DataFrame({"predicted": predictions, "true_label": true_labels})
        results_df.to_csv("mri_swarm_results.csv", index=False)
        logger.info("Successfully saved results to mri_swarm_results.csv")
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")
        logger.exception("Full traceback:")


def print_metrics(predictions, true_labels):
    """Print evaluation metrics."""
    try:
        # Calculate accuracy
        acc = accuracy_score(true_labels, predictions)
        logger.info(f"Final Accuracy: {acc:.4f}")
        print(f"Accuracy: {acc:.4f}")

        # Print detailed classification report
        report = classification_report(
            true_labels, predictions, target_names=["No Tumor", "Tumor"]
        )
        logger.info(f"Classification Report:\n{report}")
        print("\nDetailed Classification Report:")
        print(report)
    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")
        logger.exception("Full traceback:")


if __name__ == "__main__":
    logger.info("Starting MRI-Swarm evaluation script")
    try:
        evaluate_mri_swarm()
    except Exception as e:
        logger.critical(f"Critical error in main evaluation loop: {str(e)}")
        logger.exception("Full traceback:")
    logger.info("Evaluation script completed")
