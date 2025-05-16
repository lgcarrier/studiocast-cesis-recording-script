#!/usr/bin/env python3

import os
import re
import json
import time
import logging
import argparse
from pathlib import Path
from typing import List

import dotenv
from tqdm import tqdm
from google import genai
from google.genai import types

# ------------------------------------------------------------------ Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s  %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("analyze_set.log", encoding="utf-8")
    ],
)
logger = logging.getLogger(__name__)

# Debug logger for detailed debugging
debug_logger = logging.getLogger('debug')
debug_logger.setLevel(logging.DEBUG)
debug_file_handler = logging.FileHandler('analyze_set_debug.log')
debug_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
debug_logger.addHandler(debug_file_handler)
debug_logger.propagate = False

# ------------------------------------------------------------------ Helpers
def strip_set_metadata(raw: str) -> str:
    """Remove metadata or formatting lines from a .srt file, return clean text."""
    cleaned_lines: List[str] = []
    # Adjust regex based on .srt file format (assuming similar to .srt with timecodes or indices)
    metadata_re = re.compile(r"^\d+$|^\d{2}:\d{2}:\d{2},\d{3}")
    for line in raw.splitlines():
        line = line.strip()
        if not line or metadata_re.match(line):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()

def chunk_text(text: str, max_tokens: int = 14_000) -> List[str]:
    """Split text into chunks that fit within token limits."""
    paragraphs = text.split("\n\n")
    chunks, current = [], []
    char_budget = max_tokens * 4  # Approximate token-to-char ratio
    for para in paragraphs:
        if sum(len(p) for p in current) + len(para) > char_budget:
            chunks.append("\n\n".join(current))
            current = [para]
        else:
            current.append(para)
    if current:
        chunks.append("\n\n".join(current))
    return chunks

def save_analysis_files(analysis_text: str, set_path: str, save_text: bool = True, save_json: bool = True) -> tuple:
    """Save analysis results as markdown and JSON files."""
    txt_path = None
    json_path = None
    
    if save_text:
        txt_path = str(Path(set_path).with_suffix('.md'))
        try:
            Path(txt_path).write_text(analysis_text, encoding='utf-8')
            logger.info(f"Saved analysis markdown to {txt_path}")
        except Exception as e:
            logger.error(f"Error saving analysis markdown: {e}")
            txt_path = None
    
    if save_json:
        json_path = str(Path(set_path).with_suffix('.json'))
        try:
            json_pattern = r'```json\s*([\s\S]*?)\s*```'
            json_match = re.search(json_pattern, analysis_text)
            json_content = json.loads(json_match.group(1)) if json_match else {"analysis": analysis_text}
            
            Path(json_path).write_text(
                json.dumps(json_content, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            logger.info(f"Saved analysis JSON to {json_path}")
        except Exception as e:
            logger.error(f"Error saving analysis JSON: {e}")
            json_path = None
    
    return txt_path, json_path

def analyze_set_with_gemini(set_path: str, prompt: str = "Summarize this document") -> str:
    """
    Analyze a single .srt file using Google's Gemini AI model.
    
    Args:
        set_path (str): Path to the .srt file
        prompt (str): Prompt to send to Gemini along with the .srt content
        
    Returns:
        str: The analysis result text
    """
    try:
        # Check for API key
        if not os.environ.get("GOOGLE_API_KEY"):
            error_msg = "GOOGLE_API_KEY environment variable not found. Please set it and try again."
            logger.error(error_msg)
            return error_msg
        
        logger.info(f"Analyzing SET file: {set_path}")
        client = genai.Client()
        
        # Prepare the .srt file
        filepath = Path(set_path)
        
        if not filepath.exists():
            error_msg = f"SET file not found: {set_path}"
            logger.error(error_msg)
            return error_msg
        
        # Create a progress bar for the analysis
        filename = os.path.basename(set_path)
        analysis_steps = ['Loading SET', 'Sending to Gemini', 'Processing with AI', 'Receiving response']
        step_pbar = tqdm(analysis_steps, desc=f"Analyzing {filename}", position=2, leave=False)
        
        # Read and clean the .srt content (first step)
        step_pbar.set_description(f"Loading {filename}")
        raw_text = filepath.read_text(encoding="utf-8", errors="ignore")
        set_text = strip_set_metadata(raw_text)
        step_pbar.update(1)
        
        # Prepare the request (second step)
        step_pbar.set_description(f"Preparing request")
        contents = [set_text, prompt]  # Pass text directly as content
        step_pbar.update(1)
        
        # Generate content with the model (third step)
        try:
            step_pbar.set_description(f"Analyzing with Gemini")
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=contents
            )
            step_pbar.update(1)
            
            # Process response (fourth step)
            step_pbar.set_description(f"Processing response")
            result = response.text
            step_pbar.update(1)
            
            # Complete
            step_pbar.set_description(f"Analysis complete")
            step_pbar.close()
            
            logger.info(f"Successfully analyzed SET file: {set_path}")
            return result
        except Exception as e:
            step_pbar.set_description(f"Analysis failed")
            step_pbar.close()
            
            error_msg = f"Error generating content with Gemini: {str(e)}"
            logger.error(error_msg)
            return error_msg
    except ImportError as e:
        error_msg = f"Missing required package: {str(e)}. Please install google-genai package."
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        logger.error(f"Error analyzing SET file {set_path}: {e}", exc_info=True)
        return f"Analysis failed: {str(e)}"

def analyze_set_file(set_path: str, prompt: str, max_tokens: int = 14_000, skip_analyzed: bool = False) -> List[str]:
    """Analyze a single .srt file, splitting into chunks if needed."""
    logger.info(f"Analyzing SET file: {set_path}")
    
    # Check if analysis files already exist
    if skip_analyzed:
        txt_path = str(Path(set_path).with_suffix('.txt'))
        json_path = str(Path(set_path).with_suffix('.json'))
        if os.path.exists(txt_path) or os.path.exists(json_path):
            logger.info(f"Skipping already analyzed file: {set_path}")
            return []
    
    try:
        raw_set = Path(set_path).read_text(encoding="utf-8", errors="ignore")
        plain_text = strip_set_metadata(raw_set)
        chunks = chunk_text(plain_text, max_tokens=max_tokens)
        
        answers = []
        filename = Path(set_path).name

        chunk_pbar = tqdm(chunks, desc="Processing chunks", position=1)
        for chunk in chunk_pbar:
            try:
                # Combine prompt with chunk content
                chunk_prompt = f"{prompt}\n\nContent chunk:\n{chunk}"
                answer = analyze_set_with_gemini(set_path, chunk_prompt)
                answers.append(answer)
                time.sleep(1.0)  # Polite spacing
            except Exception as e:
                error_msg = f"Chunk analysis failed: {str(e)}"
                logger.error(error_msg)
                answers.append(f"[{error_msg}]")
                
        return answers
    
    except Exception as e:
        logger.error(f"Failed to analyze {set_path}: {e}")
        return [f"Analysis failed: {str(e)}"]

def main() -> None:
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(description="Analyze a SET file with Gemini")
    parser.add_argument("--file", "-f", type=Path, default=Path("output/transcript.set"),
                       help="Path to the .srt file")
    parser.add_argument("--prompt", "-p", type=str,
                       default="Summarize the content of this transcript. List main topics and key points.",
                       help="Prompt to send along with the transcript")
    parser.add_argument("--model", "-m", type=str, default="gemini-1.5-flash",
                       help="Gemini model name")
    parser.add_argument("--max-tokens", type=int, default=14_000,
                       help="Approx token budget per chunk")
    parser.add_argument("--skip-analyzed", action="store_true",
                       help="Skip files that already have analysis files")
    parser.add_argument("--no-text-files", action="store_true",
                       help="Do not save analysis results as text files")
    args = parser.parse_args()

    if not args.file.exists():
        logger.error("File not found: %s", args.file)
        return

    try:
        # Analyze the SET file
        answers = analyze_set_file(str(args.file), args.prompt, args.max_tokens, args.skip_analyzed)
        if not answers:
            return  # Skip if no new analysis was performed
        
        combined = "\n\n---\n\n".join(answers)

        # Save results
        save_text = not args.no_text_files
        save_analysis_files(combined, str(args.file), save_text=save_text, save_json=True)

    except Exception as e:
        logger.error("Analysis failed: %s", str(e), exc_info=True)

if __name__ == "__main__":
    main()