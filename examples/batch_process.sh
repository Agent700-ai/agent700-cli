#!/bin/bash
# Example: Process a prompt file and save the response
#
# Usage:
#   ./batch_process.sh prompt.txt output.txt
#
# This script reads a prompt from a file, sends it to the agent,
# and saves the response to an output file.

INPUT_FILE="${1:-prompt.txt}"
OUTPUT_FILE="${2:-response.txt}"

if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' not found"
    echo "Usage: $0 <input_file> [output_file]"
    exit 1
fi

echo "Sending prompt from: $INPUT_FILE"
echo "Saving response to: $OUTPUT_FILE"

a700cli --input-file "$INPUT_FILE" --output-file "$OUTPUT_FILE" --quiet

if [ $? -eq 0 ]; then
    echo "Done! Response saved to $OUTPUT_FILE"
else
    echo "Error: Failed to get response from agent"
    exit 1
fi
