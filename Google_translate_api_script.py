import os
import time
from typing import List
import argparse
import subprocess

# Function to split text into chunks based on input/output character limits
def split_text_into_chunks(sentences: List[str], input_limit: int, output_limit: int, safety_margin: float = 0.8):
    input_limit = int(input_limit * safety_margin)
    output_limit = int(output_limit * safety_margin)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence)
        if current_length + sentence_length > input_limit:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_length = 0
        
        current_chunk.append(sentence)
        current_length += sentence_length
    
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    
    return chunks

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\HP\Downloads\hindi-treebank-text\credentials.json"
from google.cloud import translate_v2 as translate

# Initialize the client once
translate_client = translate.Client()
def translate_text(target: str, text: str) -> dict:
    """
    Uses Google Cloud Translation API to translate a chunk of text.
    :param target: Target language code (e.g., 'hi' for Hindi)
    :param text: Text to translate (can contain multiple lines)
    :return: Dictionary with key 'translatedText'
    """
    result = translate_client.translate(text, target_language=target, format_='text')
    return {"translatedText": result["translatedText"]}

# Function to process a file and translate it
def process_file(source_file: str, target_file: str, target_lang: str, input_limit: int, output_limit: int, rate_limit: int):
    with open(source_file, "r", encoding="utf-8") as f:
        sentences = f.read().strip().split("\n")
    
    chunks = split_text_into_chunks(sentences, input_limit, output_limit)
    translated_sentences = []

    for i, chunk in enumerate(chunks):
        if i > 0 and i % rate_limit == 0:
            time.sleep(60)  # Respect rate limit
        
        result = translate_text(target_lang, chunk)
        translated_sentences.extend(result["translatedText"].split("\n"))
    
    with open(target_file, "w", encoding="utf-8") as f:
        f.write("\n".join(translated_sentences))

# Function to traverse directories and process files
def process_directory(source_dir: str, target_dir: str, target_lang: str, input_limit: int, output_limit: int, rate_limit: int):
    for root, _, files in os.walk(source_dir):
        rel_path = os.path.relpath(root, source_dir)
        target_root = os.path.join(target_dir, rel_path)
        os.makedirs(target_root, exist_ok=True)
        
        text_extensions = ['.txt', '.csv', '.tsv']  # Add more if needed

        for file in files:
            if not any(file.lower().endswith(ext) for ext in text_extensions):
                print(f"⚠️ Skipping non-text file: {file}")
                continue
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_root, file)
            print(f"Processing: {source_file} -> {target_file}")
            process_file(source_file, target_file, target_lang, input_limit, output_limit, rate_limit)

def run_command_on_files(directory: str, command: str):
    """
    Recursively traverse a directory and run a given console command on all files.
    
    :param directory: Path to the directory to traverse.
    :param command: The console command to run on each file.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                subprocess.run([command, file_path], check=True)
                print(f"Processed: {file_path}")
            except subprocess.CalledProcessError as e:
                print(f"Error processing {file_path}: {e}")

def convert_line_endings_to_unix(directory: str):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                content = content.replace(b'\r\n', b'\n')
                with open(file_path, 'wb') as f:
                    f.write(content)
                print(f"Converted: {file_path}")
            except Exception as e:
                print(f"Error converting {file_path}: {e}")

# Example Usage:
# run_command_on_files("/path/to/directory", "dos2unix")


# Example usage
#if __name__ == "__main__":
    # source_directory = "data/source"
    # target_directory = "data/translated"
    # target_language = "hi"  # Hindi
    
    # requests_per_minute = 60
    # input_char_limit = 5000
    # output_char_limit = 10000
    
    # process_directory(source_directory, target_directory, target_language, input_char_limit, output_char_limit, requests_per_minute)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Translate text files using Google Cloud Translation API.")
#     parser.add_argument("source_directory", type=str, help="Path to the source directory containing text files.")
#     parser.add_argument("target_directory", type=str, help="Path to the target directory for translated files.")
#     parser.add_argument("target_language", type=str, help="ISO code of the target language.")
#     parser.add_argument("requests_per_minute", type=int, help="Limit on the number of requests per minute.")
#     parser.add_argument("input_char_limit", type=int, help="Limit on the number of input characters per request.")
#     parser.add_argument("output_char_limit", type=int, help="Limit on the number of output characters per request.")
    
#     args = parser.parse_args()
    
#     process_directory(args.source_directory, args.target_directory, args.target_language, args.input_char_limit, args.output_char_limit, args.requests_per_minute)

# Command line argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate text files using Google Cloud Translation API.")

    parser.add_argument("-sd", "--source_directory", type=str, required=True, help=r"C:\Users\HP\Downloads\hindi-treebank-text\hindi-treebank-text")
    parser.add_argument("-td", "--target_directory", type=str, required=True, help=r"C:\Users\HP\Downloads\hindi-treebank-text\Bhojpuri-treebank-text")
    parser.add_argument("-tl", "--target_language", type=str, required=True, help="ISO 639-1 or Google-supported language code for the target language.")
    parser.add_argument("-rpm", "--requests_per_minute", type=int, required=True, help="Maximum number of translation requests allowed per minute.")
    parser.add_argument("-ic", "--input_char_per_request", type=int, required=True, help="Maximum input character limit per request (before translation).")
    parser.add_argument("-oc", "--output_char_per_request", type=int, required=True, help="Maximum output character limit per request (after translation).")

    args = parser.parse_args()

    convert_line_endings_to_unix(args.source_directory)
    process_directory(
        source_dir=args.source_directory,
        target_dir=args.target_directory,
        target_lang=args.target_language,
        input_limit=args.input_char_per_request,
        output_limit=args.output_char_per_request,
        rate_limit=args.requests_per_minute
    )

    print(f'Completed translating source language directory {args.source_directory} and saving to the target language {args.target_language} {args.target_directory}')