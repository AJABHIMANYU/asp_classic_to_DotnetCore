
# #rag implementation 
# #analysis.py
# import base64
# import os
# import shutil
# import subprocess
# import json
# import uuid
# import requests
# import time
# import stat
# import errno
# from urllib.parse import unquote, urljoin
# from fastapi import FastAPI, Form, File, UploadFile, HTTPException,BackgroundTasks
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse, JSONResponse
# from typing import Optional
# import uvicorn
# import asyncio # <-- ADD THIS
# import aiohttp # <-- ADD THIS
# from tenacity import retry, stop_after_attempt, wait_random_exponential 
# import re 
# import aiofiles # Make sure you have this
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
# from llama_index.readers.json import JSONReader
# from llama_index.core import Settings
# from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
 
# # Configuration
# AZURE_ENDPOINT = "https://azure-openai-uk.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
# AZURE_API_KEY = "NkHVD9xPtHLIvi2cgfcdfNdZnMdyZFpl02NvDHuW7fRf36cxrHerJQQJ99ALACmepeSXJ3w3AAABACOGrbaC"
# OUTPUT_FILE = "analysis_result.json"
# TEMP_DIR = "temp_repo"
# AZURE_EMBEDDING_ENDPOINT = "https://azure-openai-uk.openai.azure.com/" # The BASE URL of your resource
# AZURE_EMBEDDING_DEPLOYMENT_NAME = "text-embedding-3-large" # The exact name of your embedding deployment in Azure
# AZURE_EMBEDDING_API_VERSION = "2023-05-15" # The api-version from your original URL
# AZURE_EMBEDDING_MODEL_NAME = "text-embedding-3-large" # The underlying model name

# # --- Global LlamaIndex Configuration Block ---
# try:
#     # Initialize the embedding model client using the separate components.
#     # This is the most reliable method.
#     embed_model = AzureOpenAIEmbedding(
#         model=AZURE_EMBEDDING_MODEL_NAME,
#         deployment_name=AZURE_EMBEDDING_DEPLOYMENT_NAME,
#         api_key=AZURE_API_KEY, # Use the same key if they are from the same resource
#         azure_endpoint=AZURE_EMBEDDING_ENDPOINT,
#         api_version=AZURE_EMBEDDING_API_VERSION,
#     )
    
#     # Set this as the global default embedding model for all LlamaIndex operations
#     Settings.embed_model = embed_model
    
#     print("✅ LlamaIndex embedding model configured successfully using separate Azure components.")

# except Exception as e:
#     print(f"❌ CRITICAL ERROR: Failed to configure embedding model. LlamaIndex will not work. Error: {e}")
#     raise e

# # --- END OF CORRECTED CONFIGURATION ---

# analysis_app = FastAPI(title="Repository Analyzer API", version="1.0.0") 

 
# def remove_readonly(func, path, _):
#     """Clear read-only attribute and retry the function."""
#     try:
#         os.chmod(path, stat.S_IWRITE)
#         func(path)
#     except OSError as e:
#         if e.errno != errno.EACCES:
#             raise
 
# def remove_git_files(directory):
#     """Remove .git directory and other git-related files with retry mechanism."""
#     git_dir = os.path.join(directory, ".git")
#     if os.path.exists(git_dir):
#         for attempt in range(3):
#             try:
#                 shutil.rmtree(git_dir, onerror=remove_readonly)
#                 print(f"Removed .git directory from {directory}")
#                 break
#             except PermissionError as e:
#                 if attempt == 2:
#                     raise Exception(f"Failed to remove .git directory after retries: {str(e)}")
#                 print(f"Permission error, retrying in 1 second... ({attempt + 1}/3)")
#                 time.sleep(1)
   
#     for root, _, files in os.walk(directory):
#         for file in files:
#             if file in [".gitignore", ".gitattributes"]:
#                 file_path = os.path.join(root, file)
#                 try:
#                     os.chmod(file_path, stat.S_IWRITE)
#                     os.remove(file_path)
#                     print(f"Removed {file_path}")
#                 except OSError as e:
#                     print(f"Warning: Could not remove {file_path}: {str(e)}")
 
# def clone_repo(repo_url, temp_dir, git_token=None):
#     """Clone the GitHub repository to a temporary directory with optional token."""
#     git_config = ["-c", "core.protectNTFS=false"]
#     if git_token:
#         # Extract repository path and construct authenticated URL
#         repo_path = repo_url.split("github.com/")[1]
#         authenticated_url = f"https://{git_token}@github.com/{repo_path}"
#         cmd = ["git", "clone"] + git_config + [authenticated_url, temp_dir]
#     else:
#         # --- MODIFY THIS LINE ---
#         cmd = ["git", "clone"] + git_config + [repo_url, temp_dir]
   
#     try:
#         subprocess.run(cmd, check=True, capture_output=True, text=True, shell=True) 
#         print(f"Cloned repository to {temp_dir}")
#     except subprocess.CalledProcessError as e:
#         raise Exception(f"Failed to clone repository: {e.stderr}")
 
# # def read_file_content(file_path):
# #     """Read the content of a file with multiple encoding attempts."""
# #     encodings = ["utf-8", "latin-1", "windows-1252"]
# #     for enc in encodings:
# #         try:
# #             with open(file_path, "r", encoding=enc) as f:
# #                 return f.read()
# #         except UnicodeDecodeError:
# #             continue
# #     return f"Error reading file: Unsupported encoding"
 
# def read_file_content(file_path, is_binary=False):
#     """Read file content in text or binary mode."""
#     if is_binary:
#         with open(file_path, "rb") as f:
#             return f.read()
#     encodings = ["utf-8", "latin-1", "windows-1252"]
#     for enc in encodings:
#         try:
#             with open(file_path, "r", encoding=enc) as f:
#                 return f.read()
#         except UnicodeDecodeError:
#             continue
#     return "Error reading file: Unsupported encoding"

# @retry(
#     wait=wait_random_exponential(min=1, max=60),
#     stop=stop_after_attempt(3),
#     retry_error_callback=lambda retry_state: {
#         "file_name": retry_state.args[2],
#         "error": f"Failed after {retry_state.attempt_number} attempts: {retry_state.outcome.exception()}"
#     }
# )
# async def analyze_file_with_azure(session, content, file_name, azure_endpoint, azure_api_key):
#     """Analyze file content using Azure OpenAI API with retries."""
#     prompt = f"""
# You are an expert software analyst converting a Classic ASP file to ASP.NET Onion Architecture.
# Analyze the file named '{file_name}' and provide a detailed JSON response.

# **CRITICAL INSTRUCTION**: Your entire response MUST be a single, valid JSON object enclosed in triple backticks.
# You MUST strictly follow the JSON structure provided in the example below, especially for the `onion_architecture_mapping` section.

# **Onion Architecture Mapping Rules:**
# - You MUST use the exact keys: `domain_layer`, `application_layer`, `infrastructure_layer`, `presentation_layer`.
# - Inside each layer, the `components` key MUST contain a JSON array of strings.
# - **Domain Layer**: List the names of Domain Entities (e.g., "Book entity", "User entity").
# - **Application Layer**: List the names of Application Services (e.g., "BookService", "UserService").
# - **Infrastructure Layer**: List the names of Repositories and the DbContext (e.g., "BookRepository", "ApplicationDbContext").
# - **Presentation Layer**: List the names of MVC Controllers (e.g., "BooksController", "HomeController").- **CRITICAL NAMING RULE**: Controller names for a specific entity MUST ALWAYS be **plural** (e.g., "UsersController", "ProductsController", "OrdersController"). Never use a singular form like "UserController" or "ProductConttroller".
# - If a layer is not applicable for this file, you MUST provide an empty array `[]` for its `components`. DO NOT use `null` or "N/A".
# - **Technical Details**: Additional specifics, such as:
#     - Database schema (table, columns, data types) if relevant.

# **EXAMPLE JSON STRUCTURE TO FOLLOW:**
# ```json
# {{
#   "file_name": "example.asp",
#   "purpose": "A concise description of the file's role.",
#   "requirements": {{
#     "form_fields": [
#       {{
#         "name": "title",
#         "type": "text",
#         "required": true,
#         "validation_rules": "must not be empty"
#       }}
#     ],
#     "database_operations": {{
#       "operation": "INSERT",
#       "table": "books"
#     }}
#   }},
#   "onion_architecture_mapping": {{
#     "domain_layer": {{
#       "components": ["Book entity"]
#     }},
#     "application_layer": {{
#       "components": ["BookService"]
#     }},
#     "infrastructure_layer": {{
#       "components": ["BookRepository"]
#     }},
#     "presentation_layer": {{
#       "components": ["BooksController"]
#     }}
#   }},
#   "modern_mvc_mapping": {{
#     "controller": "BooksController",
#     "action": "Edit",
#     "view_name": "Edit.cshtml",
#     "http_method": "GET_POST"
#   }},
#   "technical_details": {{}},
#   "conversion_recommendations": {{}}
# }}
# File content:
# {content}
# """

#     headers = {
#         "Content-Type": "application/json",
#         "api-key": azure_api_key
#     }

#     payload = {
#         "messages": [
#             {"role": "system", "content": "You are a helpful assistant analyzing code files and returning strictly JSON responses."},
#             {"role": "user", "content": prompt}
#         ],
#         "max_tokens": 2048,
#         "temperature": 0.1
#     }

#     timeout = aiohttp.ClientTimeout(total=180)  # 3 minutes

#     async with session.post(azure_endpoint, headers=headers, json=payload, timeout=timeout) as response:
#         if response.status == 200:
#             result = await response.json()
#             api_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

#             # Extract JSON block using regex
#             json_match = re.search(r'```json\s*(\{.*?\})\s*```', api_content, re.DOTALL)
#             if json_match:
#                 api_content = json_match.group(1)
#             else:
#                 # Fallback cleanup
#                 if api_content.startswith("```"):
#                     api_content = api_content.strip("` \n")

#             try:
#                 parsed_result = json.loads(api_content)
#                 parsed_result["file_name"] = file_name
#                 print(f"✅ Successfully analyzed: {file_name}")
#                 return parsed_result
#             except json.JSONDecodeError as e:
#                 print(f"❌ JSON Decode Error for {file_name} after cleaning: {e}")
#                 raise e  # retry via tenacity
#         else:
#             error_text = await response.text()
#             print(f"❌ API Error {response.status} for {file_name}: {error_text}")
#             response.raise_for_status()

# async def create_rag_indexes(analysis_json_path: str, source_code_dir: str, output_index_dir: str):
#     """Creates RAG indexes for both analysis data and source code."""
#     print("Creating RAG indexes...")
    
#     # 1. Create index for the analysis JSON
#     analysis_index_path = os.path.join(output_index_dir, "analysis_index")
#     os.makedirs(analysis_index_path, exist_ok=True)
    
#     try:
#         with open(analysis_json_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)

#         files_to_index = data.get("files_analyzed", [])
#         analysis_docs = []
#         for file_analysis in files_to_index:
#             doc_content = json.dumps(file_analysis, indent=2)
#             doc_metadata = {"file_name": file_analysis.get("file_name", "unknown")}
#             analysis_docs.append(Document(text=doc_content, metadata=doc_metadata))
            
#         if not analysis_docs:
#             print("Warning: No 'files_analyzed' data found to create analysis index.")
#             return

#         analysis_index = VectorStoreIndex.from_documents(analysis_docs)
#         analysis_index.storage_context.persist(persist_dir=analysis_index_path)
#         print(f"Analysis RAG index created at: {analysis_index_path}")

#     except Exception as e:
#         print(f"Error preparing analysis documents for indexing: {e}")
#         raise

#     # 2. Create index for the raw source code with excluded extensions
#     source_index_path = os.path.join(output_index_dir, "source_code_index")
#     os.makedirs(source_index_path, exist_ok=True)
    
#     # Define file extensions to exclude (multimedia, binary, documents, non-web images)
#     exclude_extensions = [
#         '*.mp3', '*.mp4', '*.wav', '*.ogg', '*.flac', '*.avi', '*.mov', '*.wmv', '*.mkv',
#         '*.psd', '*.db', '*.mdb', '*.zip', '*.rar', '*.swf', '*.fla', '*.aac', '*.wma',
#         '*.flv', '*.mpg', '*.mpeg', '*.7z', '*.gz', '*.tar', '*.tar.gz', '*.z', '*.exe',
#         '*.pdf', '*.ppt', '*.doc', '*.xls', '*.bmp', '*.pbm', '*.wbm', '*.tif'
#     ]
    
#     # Use SimpleDirectoryReader with exclude parameter
#     source_reader = SimpleDirectoryReader(
#         input_dir=source_code_dir,
#         recursive=True,
#         exclude=exclude_extensions
#     )
#     source_docs = source_reader.load_data()
    
#     source_index = VectorStoreIndex.from_documents(source_docs)
#     source_index.storage_context.persist(persist_dir=source_index_path)
#     print(f"Source code RAG index created at: {source_index_path}")
# async def analyze_repository(repo_url, git_token=None):
#     """Clone, clean, and analyze repository files, including static assets."""
#     if os.path.exists(TEMP_DIR):
#         try:
#             shutil.rmtree(TEMP_DIR, onerror=remove_readonly)
#             print(f"Cleared existing {TEMP_DIR}")
#         except Exception as e:
#             print(f"Warning: Could not clean up existing {TEMP_DIR}: {str(e)}")

#     os.makedirs(TEMP_DIR, exist_ok=True)

#     try:
#         if not repo_url.startswith("https://github.com/"):
#             raise ValueError("Invalid GitHub repository URL")

#         clone_repo(repo_url, TEMP_DIR, git_token)
#         remove_git_files(TEMP_DIR)

#         tasks = []
#         static_assets = []
#         semaphore = asyncio.Semaphore(5)

#         async def bound_analyze_file(session, content, relative_path):
#             async with semaphore:
#                 return await analyze_file_with_azure(session, content, relative_path, AZURE_ENDPOINT, AZURE_API_KEY)

#         async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=10)) as session:
#             # Define included extensions
#             included_extensions = [
#                 '.asp', '.cs', '.cshtml', '.vb', '.js', '.css', '.html',
#                 '.json', '.xml', '.config', '.txt', '.md', '.png', '.jpg', '.jpeg', '.gif', '.ico'
#             ]
#             for root, _, files in os.walk(TEMP_DIR):
#                 for file in files:
#                     file_path = os.path.join(root, file)
#                     relative_path = os.path.relpath(file_path, TEMP_DIR)
                    
#                     # Only process files with included extensions
#                     if not any(relative_path.lower().endswith(ext) for ext in included_extensions):
#                         print(f"Skipping non-relevant file: {relative_path}")
#                         continue
                    
#                     # Handle static assets (.js, .css, images)
#                     if any(relative_path.lower().endswith(ext) for ext in ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.ico']):
#                         if relative_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.ico')):
#                             content = read_file_content(file_path, is_binary=True)
#                             static_assets.append({
#                                 "file_name": relative_path,
#                                 "type": "image",
#                                 "content": base64.b64encode(content).decode('utf-8')
#                             })
#                         else:
#                             content = read_file_content(file_path, is_binary=False)
#                             if "Error reading file" not in content:
#                                 static_assets.append({
#                                     "file_name": relative_path,
#                                     "type": "text",
#                                     "content": content
#                                 })
#                             else:
#                                 print(f"Skipping unreadable static file: {relative_path}")
#                         continue

#                     # Analyze other files (code files)
#                     content = read_file_content(file_path)
#                     if "Error reading file" in content:
#                         print(f"Skipping unreadable file: {relative_path}")
#                         continue

#                     task = bound_analyze_file(session, content, relative_path)
#                     tasks.append(task)

#             if not tasks and not static_assets:
#                 raise Exception("No readable files or static assets found to analyze.")

#             print(f"Starting analysis of {len(tasks)} files with a concurrency limit of 5...")
#             analysis_results = await asyncio.gather(*tasks, return_exceptions=True)
#             print("All files analyzed.")

#         successful_analyses = [r for r in analysis_results if not isinstance(r, Exception) and "error" not in r]
#         failed_analyses = [r for r in analysis_results if isinstance(r, Exception) or "error" in r]

#         print(f"Analysis complete. Successful: {len(successful_analyses)}, Failed: {len(failed_analyses)}, Static Assets: {len(static_assets)}")
#         if failed_analyses:
#             print("--- Failed Files ---")
#             for failed in failed_analyses:
#                 print(f"- {failed.get('file_name', 'Unknown')}: {str(failed)}")
#             print("--------------------")

#         result = {
#             "repository_url": repo_url,
#             "files_analyzed": successful_analyses,
#             "static_assets": static_assets
#         }

#            # ==========================================================
#         # <-- ADD THIS BLOCK TO PRINT THE FULL ANALYSIS JSON -->
#         print("\n" + "="*80)
#         print("--- [ANALYSIS.PY] FINAL ANALYSIS.JSON CONTENT ---")
#         print("="*80)
#         # Use json.dumps to pretty-print the dictionary
#         print(json.dumps(result, indent=2))
#         print("="*80 + "\n")
#         # ==========================================================

#         with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#             json.dump(result, f, indent=2)

#         print(f"Analysis saved to {OUTPUT_FILE}")
#         return result

#     except Exception as e:
#         if os.path.exists(TEMP_DIR):
#             shutil.rmtree(TEMP_DIR, onerror=remove_readonly)
#         print(f"Analysis failed: {str(e)}")
#         return {"repository_url": repo_url, "error": str(e)}

# @analysis_app.get("/")
# async def root():
#     """Health check endpoint."""
#     return {"message": "Repository Analyzer API is running"}
 

# def cleanup_directory(path: str):
#     """A simple synchronous function to remove a directory."""
#     if os.path.exists(path):
#         shutil.rmtree(path, onerror=remove_readonly)
#         print(f"Background task: Cleaned up directory {path}")

# @analysis_app.post('/generate-project-analysis')
# async def generate_project_analysis(
#     background_tasks: BackgroundTasks,
#     github_link: str = Form(...),
#     git_token: Optional[str] = Form(None)
# ):
#     """
#     Clones a repo, analyzes it, creates RAG indexes, and returns a ZIP file containing
#     analysis.json, RAG indexes, and static assets.
#     """
#     analysis_dir = f"analysis_{uuid.uuid4()}"
#     os.makedirs(analysis_dir, exist_ok=True)
    
#     zip_name = f"{os.path.basename(unquote(github_link))}_bundle.zip"
#     final_zip_path = os.path.join(analysis_dir, zip_name)

#     try:
#         # Step 1: Run the analysis
#         analysis_json = await analyze_repository(github_link, git_token)

#         # Step 2: Set up the bundle directory
#         bundle_dir = os.path.join(analysis_dir, "bundle")
#         os.makedirs(bundle_dir, exist_ok=True)

#         # Step 3: Save the analysis JSON
#         analysis_json_path = os.path.join(bundle_dir, "analysis.json")
#         with open(analysis_json_path, "w", encoding="utf-8") as f:
#             json.dump(analysis_json, f, indent=2)

#         # Step 4: Create RAG indexes
#         print("Creating RAG indexes from cloned repository content...")
#         await create_rag_indexes(
#             analysis_json_path=analysis_json_path, 
#             source_code_dir=TEMP_DIR,
#             output_index_dir=bundle_dir
#         )

#         print(f"RAG indexes and analysis.json created in bundle directory: {bundle_dir}")

#         # Step 5: Zip the bundle directory
#         shutil.make_archive(os.path.join(analysis_dir, os.path.splitext(zip_name)[0]), 'zip', bundle_dir)

#         # Step 6: Schedule cleanup
#         background_tasks.add_task(cleanup_directory, analysis_dir)
#         background_tasks.add_task(cleanup_directory, TEMP_DIR)

#         return FileResponse(
#             path=final_zip_path,
#             media_type="application/zip",
#             filename=zip_name
#         )

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         cleanup_directory(analysis_dir)
#         cleanup_directory(TEMP_DIR)
#         raise HTTPException(status_code=500, detail=f"Error creating analysis bundle: {str(e)}")

# if __name__ == "__main__":
#     print("Starting Analysis API server (standalone)...")
#     uvicorn.run(
#         "app:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         reload_excludes=["**/tmp_*"],  # ignore all temp dirs
#     )























































































# analysis.py

import base64
import os
import shutil
import subprocess
import json
import uuid
import time
import stat
import errno
from urllib.parse import unquote
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, BackgroundTasks, Body
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List, Dict, Any
import uvicorn
import asyncio
import aiohttp
from tenacity import retry, stop_after_attempt, wait_random_exponential
import re
import aiofiles
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index.core import Settings
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

# --- Configuration ---
AZURE_ENDPOINT = "https://azure-openai-uk.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
AZURE_API_KEY = "NkHVD9xPtHLIvi2cgfcdfNdZnMdyZFpl02NvDHuW7fRf36cxrHerJQQJ99ALACmepeSXJ3w3AAABACOGrbaC"
SESSION_TEMP_BASE_DIR = "temp_sessions"

AZURE_EMBEDDING_ENDPOINT = "https://azure-openai-uk.openai.azure.com/"
AZURE_EMBEDDING_DEPLOYMENT_NAME = "text-embedding-3-large"
AZURE_EMBEDDING_API_VERSION = "2023-05-15"
AZURE_EMBEDDING_MODEL_NAME = "text-embedding-3-large"

# --- LlamaIndex Configuration ---
try:
    embed_model = AzureOpenAIEmbedding(
        model=AZURE_EMBEDDING_MODEL_NAME,
        deployment_name=AZURE_EMBEDDING_DEPLOYMENT_NAME,
        api_key=AZURE_API_KEY,
        azure_endpoint=AZURE_EMBEDDING_ENDPOINT,
        api_version=AZURE_EMBEDDING_API_VERSION,
    )
    Settings.embed_model = embed_model
    print("✅ LlamaIndex embedding model configured successfully.")
except Exception as e:
    print(f"❌ CRITICAL ERROR: Failed to configure embedding model. Error: {e}")
    raise e

analysis_app = FastAPI(title="Repository Analyzer API", version="1.0.0")

# --- Helper Functions ---
def remove_readonly(func, path, _):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except OSError as e:
        if e.errno != errno.EACCES:
            raise

def remove_git_files(directory):
    git_dir = os.path.join(directory, ".git")
    if os.path.exists(git_dir):
        shutil.rmtree(git_dir, onerror=remove_readonly)
        print(f"Removed .git directory from {directory}")

def clone_repo(repo_url, temp_dir, git_token=None):
    if git_token:
        repo_path = repo_url.split("github.com/")[1]
        authenticated_url = f"https://{git_token}@github.com/{repo_path}"
        cmd = ["git", "clone", authenticated_url, temp_dir]
    else:
        cmd = ["git", "clone", repo_url, temp_dir]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, shell=True)
        print(f"Cloned repository to {temp_dir}")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to clone repository: {e.stderr}")

def read_file_content(file_path):
    encodings = ["utf-8", "latin-1", "windows-1252"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return f"Error reading file: Unsupported encoding"

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
async def analyze_file_with_azure_detailed(session: aiohttp.ClientSession, content: str, file_name: str) -> dict:
    prompt = f"""
You are an expert software analyst. Analyze the file named '{file_name}' from a Classic ASP project.
Your task is to extract a detailed, structured JSON representation of its components.

**CRITICAL INSTRUCTION**: Your entire response MUST be a single, valid JSON object enclosed in triple backticks.
You MUST strictly follow the JSON structure provided in the example below.

```json
{{
  "file_name": "pages/AddUser.asp",
  "summary": "Handles the addition of a new user to the database via a form submission.",
  "entities_mentioned": [
    {{
      "name": "User",
      "properties": ["firstname", "lastname", "email", "phone"]
    }}
  ],
  "database_operations": [
    {{
      "type": "INSERT",
      "table": "users",
      "description": "Inserts a new record into the users table with form data."
    }}
  ],
  "business_logic": [
    {{
      "function_name": "(Form-POST-Processing)",
      "description": "Validates that form fields are not empty before database insertion. Redirects to ListUser.asp on success.",
      "dependencies": ["../includes/db_connection.asp"]
    }}
  ]
}}
File Content to Analyze:
{content}
"""
    headers = {"Content-Type": "application/json", "api-key": AZURE_API_KEY}
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that analyzes code and returns ONLY a single, valid JSON object in triple backticks."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2048,
        "temperature": 0.1
    }
    timeout = aiohttp.ClientTimeout(total=180)
    async with session.post(AZURE_ENDPOINT, headers=headers, json=payload, timeout=timeout) as response:
        if response.status == 200:
            result = await response.json()
            api_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', api_content, re.DOTALL)
            if not json_match:
                json_match = re.search(r'(\{.*\})', api_content, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
                parsed_result = json.loads(json_string)
                parsed_result["file_name"] = file_name
                print(f"✅ Successfully analyzed: {file_name}")
                return parsed_result
            else:
                raise ValueError(f"No JSON object found in LLM response for {file_name}")
        else:
            error_text = await response.text()
            print(f"❌ API Error {response.status} for {file_name}: {error_text}")
            response.raise_for_status()

async def call_azure_llm(prompt: str) -> str:
    headers = {"Content-Type": "application/json", "api-key": AZURE_API_KEY}
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful software architect assistant that returns ONLY a single, valid JSON object in triple backticks."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4096,
        "temperature": 0.1
    }
    timeout = aiohttp.ClientTimeout(total=300)
    async with aiohttp.ClientSession() as session:
        async with session.post(AZURE_ENDPOINT, headers=headers, json=payload, timeout=timeout) as response:
            if response.status == 200:
                result = await response.json()
                api_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', api_content, re.DOTALL)
                if json_match:
                    return json_match.group(1)
                return api_content
            else:
                error_text = await response.text()
                raise HTTPException(status_code=response.status, detail=f"LLM aggregation call failed: {error_text}")

@analysis_app.post("/perform-initial-analysis")
async def perform_initial_analysis(
    background_tasks: BackgroundTasks,
    github_link: str = Form(...),
    git_token: Optional[str] = Form(None)
):
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(SESSION_TEMP_BASE_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    background_tasks.add_task(cleanup_directory, session_dir, delay=3600)

    try:
        clone_repo(github_link, session_dir, git_token)
        remove_git_files(session_dir)

        tasks = []
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=10)) as session:
            for root, _, files in os.walk(session_dir):
                for file in files:
                    if not any(file.lower().endswith(ext) for ext in ['.asp', '.html', '.js', '.css', '.inc', '.config']):
                        continue
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, session_dir)
                    content = read_file_content(file_path)
                    if "Error reading file" not in content:
                        tasks.append(analyze_file_with_azure_detailed(session, content, relative_path))

            if not tasks:
                raise HTTPException(status_code=400, detail="No relevant files found to analyze.")

            print(f"Starting detailed analysis of {len(tasks)} files...")
            analysis_results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_analyses = [r for r in analysis_results if not isinstance(r, Exception)]
        failed_analyses = [str(r) for r in analysis_results if isinstance(r, Exception)]

        if failed_analyses:
            print(f"Warning: {len(failed_analyses)} files failed to analyze.")
            print("Failures:", failed_analyses)

        # ====================================================================
        # <-- ADD THIS BLOCK TO PRINT THE INITIAL RAW ANALYSIS -->
        print("\n" + "="*80)
        print("--- [ANALYSIS.PY] INITIAL RAW FILE-BY-FILE ANALYSIS ---")
        print("="*80)
        # Use json.dumps to pretty-print the list of dictionaries
        print(json.dumps(successful_analyses, indent=2))
        print("="*80 + "\n")
        # ====================================================================

        return {
            "session_id": session_id,
            "repository_url": github_link,
            "raw_file_analyses": successful_analyses,
        }

    except Exception as e:
        cleanup_directory(session_dir)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@analysis_app.post("/aggregate-project-plan")
async def aggregate_project_plan(
    raw_analysis: List[Dict[str, Any]] = Body(..., alias="rawFileAnalyses")
):
    aggregation_prompt = f"""
You are an expert software architect. Below is a series of JSON objects, where each object
is a detailed analysis of a single file from a legacy Classic ASP project.
Your task is to analyze all of these pieces of information and create a single, unified,
and structured JSON object representing the complete project plan for a modern
ASP.NET Core application with Onion Architecture.
Rules & Logic:
Consolidate Entities: Identify all unique entities (e.g., 'User', 'Book'). Merge properties from all files that mention the same entity. Ensure property names are consistent (e.g., 'firstname' and 'FirstName' should become 'FirstName').
Define Architecture: Based on the aggregated logic, define the necessary components for the Onion Architecture:
entities: A list of objects, each with a name and a list of properties (each property as an object with name and type).
controllers: A list of objects, each with a name (MUST be plural, e.g., 'UsersController') and a list of actions (e.g., 'Index', 'Create', 'Edit', 'Delete').
services: A list of objects, each with a name (e.g., 'UserService') and a list of methods.
repositories: A list of objects, each with a name (e.g., 'UserRepository') and a list of methods.
Map Views: Create a list of all .cshtml views that will be needed, specifying their name and which controller they belong to.
Non-Functional Requirements: Summarize any non-functional requirements like security, logging, or specific configurations mentioned in the analysis.
Output a single, editable JSON object and nothing else.
RAW ANALYSIS DATA:
{json.dumps(raw_analysis, indent=2)}
"""
    try:
        print("Starting LLM aggregation for the project plan...")
        llm_response_str = await call_azure_llm(aggregation_prompt)
        editable_project_plan = json.loads(llm_response_str)
        
          # ====================================================================
        # <-- ADD THIS BLOCK TO PRINT THE AGGREGATED PLAN -->
        print("\n" + "="*80)
        print("--- [ANALYSIS.PY] AI-AGGREGATED PROJECT PLAN (EDITABLE BY USER) ---")
        print("="*80)
        # Use json.dumps to pretty-print the dictionary
        print(json.dumps(editable_project_plan, indent=2))
        print("="*80 + "\n")
        # ====================================================================


        print("✅ Successfully aggregated project plan.")
        return editable_project_plan
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse the aggregated plan from LLM response. Content: {llm_response_str}. Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse the aggregated plan from LLM response.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred during plan aggregation: {str(e)}")

def cleanup_directory(path: str, delay: int = 0):
    if delay > 0:
        time.sleep(delay)
    if os.path.exists(path):
        try:
            shutil.rmtree(path, onerror=remove_readonly)
            print(f"Background task: Cleaned up directory {path}")
        except Exception as e:
            print(f"Error during scheduled cleanup of {path}: {e}")

if __name__ == "__main__":
    print("Starting Analysis API server (standalone)...")
    if not os.path.exists(SESSION_TEMP_BASE_DIR):
        os.makedirs(SESSION_TEMP_BASE_DIR)
    uvicorn.run("analysis:analysis_app", host="0.0.0.0", port=8001, reload=True)
