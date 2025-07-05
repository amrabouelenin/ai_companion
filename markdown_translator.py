#!/usr/bin/env python3
"""
Markdown Translator Script

This script translates markdown files using a local Ollama API.
Usage: python markdown_translator.py <input_file> <target_language> [--model MODEL_NAME]
"""

import argparse
import json
import os
import sys
import requests
from pathlib import Path

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def read_markdown_file(file_path):
    """Read content from a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def write_translated_file(content, original_path, target_language):
    """Write translated content to a new file with language suffix."""
    original_path = Path(original_path)
    new_filename = f"{original_path.stem}_{target_language}{original_path.suffix}"
    new_path = original_path.parent / new_filename
    
    try:
        with open(new_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return new_path
    except Exception as e:
        print(f"Error writing translated file: {e}")
        sys.exit(1)

def translate_text(text, target_language, model="phi3-optimized"):
    """Translate text using Ollama API."""
    prompt = f"""
    You are a professional translator specializing in technical Markdown documentation.

    Translate the following markdown text into {target_language} only Do not use or mix in other languages.
    
        Ensure that:
        - Don't make literal translations.
        - All headings, code blocks, links, and formatting are preserved exactly.
        - Technical and domain-specific terms are translated with care, not literally.
        - Sentences and paragraphs remain semantically equivalent to the original English.
        - Do NOT translate or modify Markdown links or images. This means the entire expression [link text](URL) or ![alt text](URL) must be preserved exactly 
        - Do NOT translate text inside backticks (`...`), single quotes ('...'), or angle brackets (<...>) — they may represent code, UI labels, or placeholders, and must be left as-is.
        - Do NOT translate anything inside fenced code blocks (those surrounded by triple backticks like ```bash ... ``` or ```python ... ```).
    Text to translate:
    
    {text}
    """
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result["response"]
        else:
            print(f"API Error: {response.status_code}")
            print(response.text)
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        print("Make sure Ollama is running locally at http://localhost:11434")
        sys.exit(1)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Translate markdown files using Ollama API')
    parser.add_argument('input_file', help='Path to the markdown file to translate')
    parser.add_argument('target_language', help='Target language for translation (e.g. French, Spanish, German)')
    parser.add_argument('--model', default='phi3-optimized', help='Ollama model to use for translation (default: phi3-optimized)')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    print(f"Reading markdown file: {args.input_file}")
    content = read_markdown_file(args.input_file)
    
    print(f"Translating to {args.target_language} using model {args.model}...")
    translated_content = translate_text(content, args.target_language, args.model)
    
    output_path = write_translated_file(translated_content, args.input_file, args.target_language)
    print(f"Translation complete! Saved to: {output_path}")

if __name__ == "__main__":
    main()
