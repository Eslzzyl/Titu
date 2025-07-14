import os
import json
import argparse
from pathlib import Path
import sys

# Add project root directory to path for module import
sys.path.append(str(Path(__file__).parent.parent))

from models.gemini import ChatGemini
from config import (
    EVALUATE_MODEL_API_BASE_URL,
    EVALUATE_MODEL_API_KEY,
    EVALUATE_MODEL_NAME,
    EVALUATE_MODEL_TEMPERATURE,
)


def read_scripts(script_dir):
    """Read all script files in the directory"""
    scripts = []
    if not os.path.exists(script_dir):
        print(f"Directory {script_dir} does not exist")
        return scripts

    # Read all files in the directory
    files = sorted(
        [
            f
            for f in os.listdir(script_dir)
            if os.path.isfile(os.path.join(script_dir, f))
        ]
    )

    for file in files:
        file_path = os.path.join(script_dir, file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                scripts.append({"filename": file, "content": content})
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")

    return scripts


def construct_prompt(scripts):
    """Construct evaluation prompt"""
    combined_scripts = "\n\n===== Next Script =====\n\n".join(
        [f"Filename: {script['filename']}\n\n{script['content']}" for script in scripts]
    )

    prompt = f"""As a strict and professional script evaluation expert, please evaluate the following script files. These scripts may be different chapters or scenes of a story. Please evaluate and give a score from 1 to 10 (10 being the highest) for the following aspects:

1. Story Quality: Is the story engaging, are the characters well-developed, is the conflict reasonable, is the plot rich, and is there sufficient length?
2. Script Performance: Are the scene descriptions vivid, are the dialogues natural, and are the stage directions clear?
3. Chapter Coherence: Are the transitions between multiple scenes or chapters smooth, is the plot logical, and are the story branches reasonable?
4. Overall Creativity: The originality and novelty of the story.

Please provide a specific score for each evaluation dimension, along with detailed analysis and suggestions for improvement. Do not provide chapter analysis, only give an overall analysis.

=== The following are the scripts to be evaluated ===

{combined_scripts}
"""
    return prompt


def evaluate_scripts(model_name, api_key, script_dir, temperature=0.7, base_url=None):
    """Evaluate scripts and return results"""
    # Read scripts
    scripts = read_scripts(script_dir)
    if not scripts:
        return {"error": "No valid script files found"}

    # Construct prompt
    prompt = construct_prompt(scripts)

    # Call model
    try:
        gemini = ChatGemini(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
        )
        response = gemini.invoke(prompt)

        return {
            "scripts_count": len(scripts),
            "scripts_names": [script["filename"] for script in scripts],
            "evaluation_result": response,
        }
    except Exception as e:
        return {"error": f"Model invocation failed: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(description="Evaluate scripts using Gemini model")
    parser.add_argument(
        "--script_dir",
        type=str,
        default="./temp/script/",
        help="Path to the directory containing scripts",
    )
    parser.add_argument(
        "--output", type=str, help="Output results to the specified JSON file"
    )

    args = parser.parse_args()

    result = evaluate_scripts(
        model_name=EVALUATE_MODEL_NAME,
        api_key=EVALUATE_MODEL_API_KEY,
        script_dir=args.script_dir,
        temperature=EVALUATE_MODEL_TEMPERATURE,
        base_url=EVALUATE_MODEL_API_BASE_URL,
    )

    # Print results
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Evaluated {result['scripts_count']} script files:")
        for name in result["scripts_names"]:
            print(f"- {name}")
        print("\n=== Evaluation Result ===\n")
        print(result["evaluation_result"])

        # Output to file
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\nResults saved to: {args.output}")


if __name__ == "__main__":
    main()
