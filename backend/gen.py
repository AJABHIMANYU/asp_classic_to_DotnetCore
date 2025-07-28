
# #rag implementation 
# #gen.py
# import base64
# import os
# import json
# import re
# import zipfile
# import shutil
# from urllib.parse import unquote, urljoin
# import uuid
# import ssl
# import certifi
# import asyncio
# import aiohttp
# from fastapi import FastAPI, UploadFile, Form, File, HTTPException
# from fastapi.responses import FileResponse
# import aiofiles
# from collections import defaultdict
# from fastapi.middleware.cors import CORSMiddleware
# from llama_index.core import Settings
# from llama_index.llms.azure_openai import AzureOpenAI
# from llama_index.core import StorageContext, load_index_from_storage

 
# generation_app = FastAPI()
 


# project_structures = {}
# # Configuration
# AZURE_ENDPOINT = "https://azure-openai-uk.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
# AZURE_API_KEY = "NkHVD9xPtHLIvi2cgfcdfNdZnMdyZFpl02NvDHuW7fRf36cxrHerJQQJ99ALACmepeSXJ3w3AAABACOGrbaC"

# # --- Global LlamaIndex LLM Configuration ---
# # We need to configure the LLM for LlamaIndex's internal use (e.g., for query engines)
# try:
#     # Parse the components from your full endpoint URL
#     # This is the most reliable way to configure the client.
#     AZURE_LLM_BASE_ENDPOINT = "https://azure-openai-uk.openai.azure.com/"
#     AZURE_LLM_DEPLOYMENT_NAME = "gpt-4o"
#     AZURE_LLM_API_VERSION = "2024-08-01-preview"
    
#     # Create an instance of the Azure LLM client
#     llm = AzureOpenAI(
#         model="gpt-4o", # The underlying model name
#         deployment_name=AZURE_LLM_DEPLOYMENT_NAME,
#         api_key=AZURE_API_KEY,
#         azure_endpoint=AZURE_LLM_BASE_ENDPOINT,
#         api_version=AZURE_LLM_API_VERSION,
#     )

#     # Set this as the global default LLM for all LlamaIndex operations
#     Settings.llm = llm

#     print("✅ LlamaIndex LLM configured successfully to use Azure OpenAI.")

# except Exception as e:
#     print(f"❌ CRITICAL ERROR: Failed to configure LLM. LlamaIndex query engines will not work. Error: {e}")
#     raise e


# def analyze_project_structure(analysis_data: dict) -> dict:
#     """
#     Analyzes the entire project structure to identify and DE-DUPLICATE
#     all unique components needed for the new application, now using the
#     detailed 'modern_mvc_mapping' for accuracy.
#     """
#     project_plan = {
#         'entities': set(),
#         'services': set(),
#         'service_interfaces': set(),
#         'repositories': set(),
#         'controllers': set(),
#         # The 'views' set stores tuples of (controller_name, view_name) for uniqueness
#         'views': set() 
#     }
   
#     if not isinstance(analysis_data, dict):
#         print("Warning: analysis_data is not a dict.")
#         return project_plan
   
#     files_analyzed = analysis_data.get("files_analyzed", [])
#     if not isinstance(files_analyzed, list):
#         print("Warning: files_analyzed is not a list.")
#         return project_plan
   
#     print(f"Aggregating and de-duplicating analysis for {len(files_analyzed)} files...")
   
#     for file_analysis in files_analyzed:
#         if not isinstance(file_analysis, dict):
#             continue
            
#         # --- 1. Aggregate Onion Architecture Components (using sets for auto-deduplication) ---
#         onion_mapping = file_analysis.get("onion_architecture_mapping", {})
#         if isinstance(onion_mapping, dict):
#             # Domain Entities
#             domain = onion_mapping.get("domain_layer", {})
#             if isinstance(domain, dict):
#                 for entity in domain.get("components", []):
#                     if entity: 
#                         # Clean up names like "Book entity" to just "Book"
#                         clean_name = entity.replace(" entity", "").strip()
#                         if clean_name: project_plan['entities'].add(clean_name)
            
#             # Application Services and Interfaces
#             application = onion_mapping.get("application_layer", {})
#             if isinstance(application, dict):
#                 for service in application.get("components", []):
#                     if service and "service" in service.lower():
#                         clean_name = service.strip()
#                         project_plan['services'].add(clean_name)
#                         if not clean_name.startswith('I'):
#                             project_plan['service_interfaces'].add(f"I{clean_name}")

#             # Infrastructure Repositories
#             infrastructure = onion_mapping.get("infrastructure_layer", {})
#             if isinstance(infrastructure, dict):
#                 for repo in infrastructure.get("components", []):
#                     if repo and "repository" in repo.lower():
#                         project_plan['repositories'].add(repo.strip())

#         # --- 2. Aggregate and De-duplicate Controllers and Views using the NEW `modern_mvc_mapping` ---
#         mvc_map = file_analysis.get('modern_mvc_mapping')
#         if isinstance(mvc_map, dict):
#             controller = mvc_map.get('controller')
#             view_name = mvc_map.get('view_name')
            
#             # Add the controller to its set (duplicates are ignored automatically)
#             if controller:
#                 project_plan['controllers'].add(controller)
                
#             # Ensure view_name is a single file (e.g., 'Edit.cshtml'), not a nested path
#             if controller and view_name:
#                 view_name = os.path.basename(view_name).strip()
#                 if view_name.lower().endswith('.cshtml'):
#                     project_plan['views'].add((controller, view_name))

#     # Convert sets to sorted lists for predictable ordering in the generation queue
#     final_structure = {key: sorted(list(value)) for key, value in project_plan.items()}
    
#     print(f"Final project master plan: {final_structure}")
#     return final_structure

# def create_generation_queue(project_plan: dict, namespace: str) -> list:
#     queue = []

#     if not isinstance(project_plan, dict):
#         raise ValueError("project_plan must be a dictionary")

#     # Layer 1: Domain (Only include entities from project_plan['entities'])
#     for entity in project_plan.get('entities', []):
#         queue.append({"path": f"Domain/Entities/{entity}.cs", "type": "Entity", "entity_name": entity})

#     # Layer 2: Application Interfaces
#     for repo in project_plan.get('repositories', []):
#         entity_name = repo.replace('Repository', '')
#         queue.append({"path": f"Application/Interfaces/I{entity_name}Repository.cs", "type": "RepositoryInterface", "entity_name": entity_name})
    
#     for service in project_plan.get('service_interfaces', []):
#         entity_name = service.replace('Service', '').lstrip('I')
#         queue.append({"path": f"Application/Interfaces/{service}.cs", "type": "ServiceInterface", "entity_name": entity_name})

#     # Layer 3: Infrastructure
#     for repo in project_plan.get('repositories', []):
#         entity_name = repo.replace('Repository', '')
#         queue.append({"path": f"Infrastructure/Repositories/{entity_name}Repository.cs", "type": "Repository", "entity_name": entity_name})
    
#     # Add DbContext
#     all_entities_str = ",".join(project_plan.get('entities', []))
#     queue.append({"path": "Infrastructure/Data/ApplicationDbContext.cs", "type": "DbContext", "entity_name": all_entities_str})

#     # Layer 4: Application Services
#     for service in project_plan.get('services', []):
#         entity_name = service.replace('Service', '')
#         queue.append({"path": f"Application/Services/{service}.cs", "type": "Service", "entity_name": entity_name})

#     # Layer 5: Presentation Layer
#     for controller_name in project_plan.get('controllers', []):
#         entity_name = controller_name.replace('Controller', '')
#         queue.append({"path": f"Presentation/Controllers/{controller_name}.cs", "type": "Controller", "entity_name": entity_name})

#     for controller_name, view_file_name in project_plan.get('views', []):
#         controller_folder = controller_name.replace('Controller', '')
#         entity_name = controller_folder.rstrip('s')
#         queue.append({
#             "path": f"Presentation/Views/{controller_folder}/{view_file_name}",
#             "type": "View",
#             "entity_name": entity_name
#         })

#     # Add HomeController and Index.cshtml with a distinct entity_name
#     queue.append({
#         "path": "Presentation/Controllers/HomeController.cs",
#         "type": "HomeController",
#         "entity_name": "DefaultPage"  # Use a distinct name to avoid entity confusion
#     })
#     queue.append({
#         "path": "Presentation/Views/Home/Index.cshtml",
#         "type": "HomeView",
#         "entity_name": "DefaultPage"
#     })

#     return queue

# async def generate_single_file(item: dict, query_engines: dict, generated_code_cache: dict, namespace: str, project_plan: dict, rag_cache: dict = None) -> str:
#     """
#     Generates a single file using an ADVANCED targeted prompt and a rich RAG context.
#     """
#     if rag_cache is None:
#         rag_cache = {}  # Initialize cache if not provided
#     file_type = item['type']
#     entity_name = item.get('entity_name', 'General')

#     # Handle DbContext (unchanged)
#     if file_type == 'DbContext':
#         print("  -> Using deterministic template for DbContext.")
#         entity_name_list = item.get('entity_name', '').split(',')
#         all_entities = [name for name in entity_name_list if name]
#         db_set_properties = "        // No entities were found to create DbSet properties.\n" if not all_entities else "".join(f"        public DbSet<{entity}> {entity}s {{ get; set; }}\n" for entity in sorted(all_entities))
#         db_context_code = f"""using Microsoft.EntityFrameworkCore;
# using {namespace}.Domain.Entities;

# namespace {namespace}.Infrastructure.Data
# {{
#     public class ApplicationDbContext : DbContext
#     {{
#         public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
#             : base(options)
#         {{
#         }}

# {db_set_properties}
#         protected override void OnModelCreating(ModelBuilder modelBuilder)
#         {{
#             base.OnModelCreating(modelBuilder);
#             // You can add entity configurations here if needed in the future.
#         }}
#     }}
# }}
# """
#         return db_context_code

#     # Fallback content
#     fallback_home_controller = f"""using Microsoft.AspNetCore.Mvc;

# namespace {namespace}.Presentation.Controllers
# {{
#     public class HomeController : Controller
#     {{
#         public IActionResult Index()
#         {{
#             return View();
#         }}

#         public IActionResult Error()
#         {{
#             return View();
#         }}
#     }}
# }}"""

#     fallback_index_cshtml = f"""@{{
#     ViewData["Title"] = "Home Page";
# }}

# <div class="text-center">
#     <h1 class="display-4">Welcome to {namespace}</h1>
#     <p>This is the default home page for your migrated ASP.NET Core application.</p>
# </div>"""

#     # Initialize context
#     context = ""
#     legacy_context = ""

#     # Provide necessary 'using' statements
#     required_using_statements = f"using {namespace}.Domain.Entities;\n"
#     if file_type in ['Service', 'Repository', 'Controller', 'HomeController']:
#         required_using_statements += f"using {namespace}.Application.Interfaces;\n"
#     if file_type == 'Repository':
#         required_using_statements += f"using {namespace}.Infrastructure.Data;\n"
#     if file_type == 'HomeController':
#         required_using_statements += f"using Microsoft.AspNetCore.Mvc;\n"

#     context += f"// CONTEXT: You MUST include these using statements if they are relevant:\n{required_using_statements}\n"

#     # Provide interface and dependency context
#     if file_type == 'Service':
#         interface_name = f"I{entity_name}Service.cs"
#         repo_interface_name = f"I{entity_name}Repository.cs"
#         if interface_name in generated_code_cache:
#             context += f"// CONTEXT: The service MUST implement this interface:\n// --- {interface_name} ---\n{generated_code_cache[interface_name]}\n\n"
#         if repo_interface_name in generated_code_cache:
#             context += f"// CONTEXT: The service's constructor should inject this repository interface:\n// --- {repo_interface_name} ---\n{generated_code_cache[repo_interface_name]}\n\n"
    
#     if file_type == 'Repository':
#         interface_name = f"I{entity_name}Repository.cs"
#         if interface_name in generated_code_cache:
#             context += f"// CONTEXT: The repository MUST implement this interface:\n// --- {interface_name} ---\n{generated_code_cache[interface_name]}\n\n"
            
#     if file_type == 'Controller':
#         service_entity_name = entity_name.rstrip('s')
#         service_interface_name = f"I{service_entity_name}Service.cs"
#         if service_interface_name in generated_code_cache:
#             context += f"// CONTEXT: The controller MUST use this service interface:\n// --- {service_interface_name} ---\n{generated_code_cache[service_interface_name]}\n\n"

#     # RAG queries with caching
#     cache_key = f"{entity_name}_{file_type}"
#     if cache_key in rag_cache:
#         legacy_context = rag_cache[cache_key]
#         print(f"Using cached RAG data for {cache_key}")
#     else:
#         try:
#             if file_type in ['HomeController', 'HomeView']:
#                 analysis_query = "Retrieve the detailed analysis for the legacy project's default page (e.g., default.asp, index.asp, or the main landing page)."
#                 source_query = "Retrieve the full source code of the legacy project's default page (e.g., default.asp, index.asp, or the main landing page)."
#             else:
#                 analysis_query = f"Retrieve the detailed analysis for all legacy files related to the '{entity_name}' entity or feature."
#                 source_query = f"Retrieve the full source code of the single most relevant legacy file for implementing the '{entity_name}' feature."
            
#             analysis_response = await asyncio.to_thread(query_engines['analysis'].query, analysis_query)
#             source_response = await asyncio.to_thread(query_engines['source'].query, source_query)
            
#             legacy_context += f"// LEGACY ANALYSIS:\n// {analysis_query}\n/*\n{str(analysis_response)}\n*/\n\n"
#             legacy_context += f"// LEGACY SOURCE CODE:\n// {source_query}\n/*\n{str(source_response)}\n*/\n"
            
#             rag_cache[cache_key] = legacy_context
#             print(f"Cached RAG data for {cache_key}")
            
#             if not str(analysis_response).strip() or "no relevant data" in str(analysis_response).lower():
#                 print(f"Warning: Insufficient RAG data for {file_type}. Using fallback content.")
#                 return fallback_home_controller if file_type == 'HomeController' else fallback_index_cshtml
#         except Exception as e:
#             print(f"Warning: RAG query failed for {file_type}. Using fallback content. Error: {e}")
#             return fallback_home_controller if file_type == 'HomeController' else fallback_index_cshtml

#     # Prompt for LLM (unchanged)
#     prompt = f"""
# You are an expert C# developer tasked with migrating a single file from a legacy application to a modern ASP.NET Core MVC project with Onion Architecture. Your work must be precise and strictly follow the provided context and rules.

# **Your Task:** Generate the complete and valid {"C# code" if file_type != "HomeView" else "Razor view (CSHTML) code"} for the following file.

# ---
# **FILE SPECIFICATION**
# - **File Path:** {item['path']}
# - **File Type:** {file_type}
# - **Primary Entity:** {entity_name}
# - **Project Namespace:** {namespace}
# ---

# ---
# **CONTEXT & REQUIREMENTS**

# **Generated Code Context:**
# {context if context else "// No previously generated code context was provided."}

# **Legacy System Context (from RAG):**
# {legacy_context if legacy_context else "// No legacy context was retrieved."}
# ---

# ---
# **STRICT GENERATION RULES**

# 1. **Adhere to Context:** You MUST use the information from the 'CONTEXT' sections. The logic from the 'LEGACY SOURCE CODE' should be correctly migrated into the new C# or CSHTML patterns.
# 2. **No Extra Properties (CRITICAL for Entities):** If generating an 'Entity', you MUST ONLY create properties that directly correspond to the database schema described in the 'LEGACY ANALYSIS'. DO NOT add any extra fields like `CreatedAt`, `IsActive`, `PasswordHash`, etc., unless they are explicitly mentioned in the analysis.
# 3. **Implement Interfaces Fully:** If a class implements an interface provided in the context, you MUST implement ALL methods EXACTLY as defined in the interface, including method names, return types, and parameter lists.
# 4. **Correct Inheritance:** Controllers (including HomeController) MUST inherit from `Microsoft.AspNetCore.Mvc.Controller`. Repositories and Services MUST implement their respective interfaces from the context.
# 5. **Return Types:** Controller actions (including HomeController) MUST return `IActionResult` (e.g., `View(model)`). They are NOT API controllers.
# 6. **Code Purity:** Generate ONLY the raw code for the specified file. Do not include any explanations, comments, or markdown wrappers like ```csharp or ```html
# 7. **Method Signature Consistency:** When implementing an interface, the method names, return types, and parameters MUST EXACTLY match the interface definition provided in the context.
# 8. **Dependency Injection:** For Services and Repositories, use constructor injection to inject their dependencies (e.g., `I{entity_name}Repository` for Services, `ApplicationDbContext` for Repositories) as shown in the context.
# 9. **HomeController Specifics:** If generating a HomeController, it should implement the logic of the legacy project's default page (e.g., default.asp, index.asp) as described in the 'LEGACY ANALYSIS' and 'LEGACY SOURCE CODE'. It should include an `Index` action that returns a view, and optionally an `Error` action.
# 10. **HomeView Specifics:** If generating a HomeView (Index.cshtml), it should be a Razor view that renders the UI of the legacy project's default page based on the 'LEGACY ANALYSIS' and 'LEGACY SOURCE CODE'. Include necessary HTML, Bootstrap classes, and form elements as described. Set `ViewData["Title"]` appropriately.
# ---

# Generate the code now.
# """
    
#     headers = {"Content-Type": "application/json", "api-key": AZURE_API_KEY}
#     payload = {"messages": [{"role": "user", "content": prompt}], "max_tokens": 4096, "temperature": 0.05}
    
#     async with aiohttp.ClientSession() as session:
#         async with session.post(AZURE_ENDPOINT, json=payload, headers=headers) as response:
#             if response.status == 200:
#                 response_json = await response.json()
#                 return response_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
#             else:
#                 error_text = await response.text()
#                 print(f"Error generating {item['path']}: {error_text}")
#                 return fallback_home_controller if file_type == 'HomeController' else fallback_index_cshtml if file_type == 'HomeView' else f"// ERROR: Could not generate file. Status: {response.status}"

# async def fetch_with_relaxed_ssl(file_path, raw_url):
#     """Fallback method with relaxed SSL verification."""
#     try:
#         print(f"Attempting fallback with relaxed SSL for {file_path}")
#         ssl_context = ssl.create_default_context()
#         ssl_context.check_hostname = False
#         ssl_context.verify_mode = ssl.CERT_NONE
       
#         connector = aiohttp.TCPConnector(ssl=ssl_context)
#         timeout = aiohttp.ClientTimeout(total=30)
       
#         async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
#             async with session.get(raw_url) as response:
#                 if response.status == 200:
#                     content = await response.text()
#                     print(f"Successfully fetched {file_path} with relaxed SSL")
#                     return content
#                 else:
#                     print(f"HTTP {response.status} for {file_path} even with relaxed SSL")
#                     return None
                   
#     except Exception as e:
#         print(f"Fallback also failed for {file_path}: {str(e)}")
#         return None
 
# async def fetch_via_github_api(file_path, github_repo, session):
#     """Alternative method using GitHub API."""
#     try:
#         if 'github.com' in github_repo:
#             repo_part = github_repo.replace('https://github.com/', '').rstrip('/')
#             if '/' not in repo_part:
#                 print(f"Invalid repository format: {github_repo}")
#                 return None
 
#             owner, repo = repo_part.split('/', 1)
 
#             # Fix: Avoid backslash inside f-string
#             safe_path = file_path.replace('\\', '/')
#             api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{safe_path}"
 
#             print(f"Trying GitHub API for {file_path}: {api_url}")
 
#             async with session.get(api_url) as response:
#                 if response.status == 200:
#                     data = await response.json()
#                     if data.get('encoding') == 'base64':
#                         import base64
#                         content = base64.b64decode(data['content']).decode('utf-8')
#                         print(f"Successfully fetched {file_path} via GitHub API")
#                         return content
#                 else:
#                     print(f"GitHub API returned {response.status} for {file_path}")
#                     return None
 
#     except Exception as e:
#         print(f"GitHub API fetch failed for {file_path}: {str(e)}")
#         return None
 
#     return None
 
 
 
# # async def create_project_structure(output_dir, project_name):
# #     """
# #     Creates the ASP.NET Core project structure directories and
# #     returns the content for the .sln and .csproj files.
# #     """
# #     solution_name = project_name
# #     projects = [
# #         {"name": f"{solution_name}.Domain", "type": "ClassLibrary", "path": "Domain"},
# #         {"name": f"{solution_name}.Application", "type": "ClassLibrary", "path": "Application"},
# #         {"name": f"{solution_name}.Infrastructure", "type": "ClassLibrary", "path": "Infrastructure"},
# #         {"name": f"{solution_name}.Presentation", "type": "AspNetCore", "path": "Presentation"}
# #     ]

# #     # This list will hold the generated file data
# #     structure_files = []

# #     # --- Create Directory Structure (this part can remain) ---
# #     os.makedirs(output_dir, exist_ok=True)
# #     os.makedirs(os.path.join(output_dir, "Presentation", "wwwroot", "css"), exist_ok=True)
# #     os.makedirs(os.path.join(output_dir, "Presentation", "wwwroot", "js"), exist_ok=True)
# #     os.makedirs(os.path.join(output_dir, "Presentation", "Views", "Shared"), exist_ok=True)
# #     os.makedirs(os.path.join(output_dir, "Presentation", "Views", "Home"), exist_ok=True)
# #     os.makedirs(os.path.join(output_dir, "Presentation", "Controllers"), exist_ok=True)
# #     os.makedirs(os.path.join(output_dir, "Domain", "Entities"), exist_ok=True)
# #     os.makedirs(os.path.join(output_dir, "Application", "Interfaces"), exist_ok=True)
# #     os.makedirs(os.path.join(output_dir, "Application", "Services"), exist_ok=True)
# #     os.makedirs(os.path.join(output_dir, "Infrastructure", "Data"), exist_ok=True)
# #     os.makedirs(os.path.join(output_dir, "Infrastructure", "Repositories"), exist_ok=True)


# #     # --- Generate .sln file content ---
# #     project_guids = {project['name']: str(uuid.uuid4()).upper() for project in projects}
# #     solution_content = f"""Microsoft Visual Studio Solution File, Format Version 12.00
# # # Visual Studio Version 17
# # VisualStudioVersion = 17.3.32924.211
# # MinimumVisualStudioVersion = 10.0.40219.1
# # """
# #     for project in projects:
# #         project_guid = project_guids[project['name']]
# #         project_path = os.path.join(project['path'], f"{project['name']}.csproj").replace('/', '\\')
# #         solution_content += f"""Project("{{9A19103F-16F7-4668-BE54-9A1E7A4F7556}}") = "{project['name']}", "{project_path}", "{{{project_guid}}}"
# # EndProject
# # """
# #     solution_content += """Global
# # 	GlobalSection(SolutionConfigurationPlatforms) = preSolution
# # 		Debug|Any CPU = Debug|Any CPU
# # 		Release|Any CPU = Release|Any CPU
# # 	EndGlobalSection
# # 	GlobalSection(ProjectConfigurationPlatforms) = postSolution
# # """
# #     for project in projects:
# #         project_guid = project_guids[project['name']]
# #         solution_content += f"""		{{{project_guid}}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
# # 		{{{project_guid}}}.Debug|Any CPU.Build.0 = Debug|Any CPU
# # 		{{{project_guid}}}.Release|Any CPU.ActiveCfg = Release|Any CPU
# # 		{{{project_guid}}}.Release|Any CPU.Build.0 = Release|Any CPU
# # """
# #     solution_content += """	EndGlobalSection
# # 	GlobalSection(SolutionProperties) = preSolution
# # 		HideSolutionNode = FALSE
# # 	EndGlobalSection
# # EndGlobal
# # """
# #     # ADD .sln file to the list to be returned
# #     structure_files.append({
# #         "path": f"{solution_name}.sln",
# #         "content": solution_content
# #     })

# #     # --- Generate .csproj file content ---
# #     for project in projects:
# #         csproj_content = ""
# #         if project["type"] == "ClassLibrary":
# #             if "Domain" in project["name"]:
# #                 csproj_content = """<Project Sdk="Microsoft.NET.Sdk">
# #   <PropertyGroup>
# #     <TargetFramework>net8.0</TargetFramework>
# #     <ImplicitUsings>enable</ImplicitUsings>
# #     <Nullable>enable</Nullable>
# #   </PropertyGroup>
# # </Project>
# # """
# #             elif "Application" in project["name"]:
# #                 csproj_content = f"""<Project Sdk="Microsoft.NET.Sdk">
# #   <PropertyGroup>
# #     <TargetFramework>net8.0</TargetFramework>
# #     <ImplicitUsings>enable</ImplicitUsings>
# #     <Nullable>enable</Nullable>
# #   </PropertyGroup>
# #   <ItemGroup>
# #     <ProjectReference Include="..\\Domain\\{solution_name}.Domain.csproj" />
# #   </ItemGroup>
# # </Project>
# # """
# #             else: # Infrastructure
# #                 csproj_content = f"""<Project Sdk="Microsoft.NET.Sdk">
# #   <PropertyGroup>
# #     <TargetFramework>net8.0</TargetFramework>
# #     <ImplicitUsings>enable</ImplicitUsings>
# #     <Nullable>enable</Nullable>
# #   </PropertyGroup>
# #   <ItemGroup>
# #     <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
# #     <PackageReference Include="Pomelo.EntityFrameworkCore.MySql" Version="8.0.0" />
# #     <PackageReference Include="Microsoft.EntityFrameworkCore.Tools" Version="8.0.0" />
# #   </ItemGroup>
# #   <ItemGroup>
# #     <ProjectReference Include="..\\Domain\\{solution_name}.Domain.csproj" />
# #     <ProjectReference Include="..\\Application\\{solution_name}.Application.csproj" />
# #   </ItemGroup>
# # </Project>
# # """
# #         else: # Presentation (AspNetCore) project
# #             csproj_content = f"""<Project Sdk="Microsoft.NET.Sdk.Web">
# #   <PropertyGroup>
# #     <TargetFramework>net8.0</TargetFramework>
# #     <Nullable>enable</Nullable>
# #     <ImplicitUsings>enable</ImplicitUsings>
# #   </PropertyGroup>
# #   <ItemGroup>
# #     <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
# #     <PackageReference Include="Pomelo.EntityFrameworkCore.MySql" Version="8.0.0" />
# #     <PackageReference Include="Microsoft.EntityFrameworkCore.Tools" Version="8.0.0" />
# #   </ItemGroup>
# #   <ItemGroup>
# #     <ProjectReference Include="..\\Infrastructure\\{solution_name}.Infrastructure.csproj" />
# #     <ProjectReference Include="..\\Application\\{solution_name}.Application.csproj" />
# #     <ProjectReference Include="..\\Domain\\{solution_name}.Domain.csproj" />
# #   </ItemGroup>
# # </Project>
# # """
# #         # ADD .csproj file to the list to be returned
# #         structure_files.append({
# #             "path": os.path.join(project["path"], f"{project['name']}.csproj"),
# #             "content": csproj_content
# #         })

# #     # Return the list of generated structure files
# #     return structure_files
# # Modified create_project_structure
# async def create_project_structure(output_dir, project_name):
#     """
#     Creates the ASP.NET Core project structure directories and returns .sln and .csproj files.
#     """
#     solution_name = project_name
#     projects = [
#         {"name": f"{solution_name}.Domain", "type": "ClassLibrary", "path": "Domain"},
#         {"name": f"{solution_name}.Application", "type": "ClassLibrary", "path": "Application"},
#         {"name": f"{solution_name}.Infrastructure", "type": "ClassLibrary", "path": "Infrastructure"},
#         {"name": f"{solution_name}.Presentation", "type": "AspNetCore", "path": "Presentation"}
#     ]
#     structure_files = []
#     os.makedirs(output_dir, exist_ok=True)
#     os.makedirs(os.path.join(output_dir, "Presentation", "wwwroot", "css"), exist_ok=True)
#     os.makedirs(os.path.join(output_dir, "Presentation", "wwwroot", "js"), exist_ok=True)
#     os.makedirs(os.path.join(output_dir, "Presentation", "wwwroot", "images"), exist_ok=True)  # Added images folder
#     os.makedirs(os.path.join(output_dir, "Presentation", "Views", "Shared"), exist_ok=True)
#     os.makedirs(os.path.join(output_dir, "Presentation", "Views", "Home"), exist_ok=True)
#     os.makedirs(os.path.join(output_dir, "Presentation", "Controllers"), exist_ok=True)
#     os.makedirs(os.path.join(output_dir, "Domain", "Entities"), exist_ok=True)
#     os.makedirs(os.path.join(output_dir, "Application", "Interfaces"), exist_ok=True)
#     os.makedirs(os.path.join(output_dir, "Application", "Services"), exist_ok=True)
#     os.makedirs(os.path.join(output_dir, "Infrastructure", "Data"), exist_ok=True)
#     os.makedirs(os.path.join(output_dir, "Infrastructure", "Repositories"), exist_ok=True)
#     project_guids = {project['name']: str(uuid.uuid4()).upper() for project in projects}
#     solution_content = f"""Microsoft Visual Studio Solution File, Format Version 12.00
# # Visual Studio Version 17
# VisualStudioVersion = 17.3.32924.211
# MinimumVisualStudioVersion = 10.0.40219.1
# """
#     for project in projects:
#         project_guid = project_guids[project['name']]
#         project_path = os.path.join(project['path'], f"{project['name']}.csproj").replace('/', '\\')
#         solution_content += f"""Project("{{9A19103F-16F7-4668-BE54-9A1E7A4F7556}}") = "{project['name']}", "{project_path}", "{{{project_guid}}}"
# EndProject
# """
#     solution_content += """Global
# 	GlobalSection(SolutionConfigurationPlatforms) = preSolution
# 		Debug|Any CPU = Debug|Any CPU
# 		Release|Any CPU = Release|Any CPU
# 	EndGlobalSection
# 	GlobalSection(ProjectConfigurationPlatforms) = postSolution
# """
#     for project in projects:
#         project_guid = project_guids[project['name']]
#         solution_content += f"""		{{{project_guid}}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
# 		{{{project_guid}}}.Debug|Any CPU.Build.0 = Debug|Any CPU
# 		{{{project_guid}}}.Release|Any CPU.ActiveCfg = Release|Any CPU
# 		{{{project_guid}}}.Release|Any CPU.Build.0 = Release|Any CPU
# """
#     solution_content += """	EndGlobalSection
# 	GlobalSection(SolutionProperties) = preSolution
# 		HideSolutionNode = FALSE
# 	EndGlobalSection
# EndGlobal
# """
#     structure_files.append({
#         "path": f"{solution_name}.sln",
#         "content": solution_content
#     })
#     for project in projects:
#         csproj_content = ""
#         if project["type"] == "ClassLibrary":
#             if "Domain" in project["name"]:
#                 csproj_content = """<Project Sdk="Microsoft.NET.Sdk">
#   <PropertyGroup>
#     <TargetFramework>net8.0</TargetFramework>
#     <ImplicitUsings>enable</ImplicitUsings>
#     <Nullable>enable</Nullable>
#   </PropertyGroup>
# </Project>
# """
#             elif "Application" in project["name"]:
#                 csproj_content = f"""<Project Sdk="Microsoft.NET.Sdk">
#   <PropertyGroup>
#     <TargetFramework>net8.0</TargetFramework>
#     <ImplicitUsings>enable</ImplicitUsings>
#     <Nullable>enable</Nullable>
#   </PropertyGroup>
#   <ItemGroup>
#     <ProjectReference Include="..\\Domain\\{solution_name}.Domain.csproj" />
#   </ItemGroup>
# </Project>
# """
#             else:
#                 csproj_content = f"""<Project Sdk="Microsoft.NET.Sdk">
#   <PropertyGroup>
#     <TargetFramework>net8.0</TargetFramework>
#     <ImplicitUsings>enable</ImplicitUsings>
#     <Nullable>enable</Nullable>
#   </PropertyGroup>
#   <ItemGroup>
#     <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
#     <PackageReference Include="Pomelo.EntityFrameworkCore.MySql" Version="8.0.0" />
#     <PackageReference Include="Microsoft.EntityFrameworkCore.Tools" Version="8.0.0" />
#   </ItemGroup>
#   <ItemGroup>
#     <ProjectReference Include="..\\Domain\\{solution_name}.Domain.csproj" />
#     <ProjectReference Include="..\\Application\\{solution_name}.Application.csproj" />
#   </ItemGroup>
# </Project>
# """
#         else:
#             csproj_content = f"""<Project Sdk="Microsoft.NET.Sdk.Web">
#   <PropertyGroup>
#     <TargetFramework>net8.0</TargetFramework>
#     <Nullable>enable</Nullable>
#     <ImplicitUsings>enable</ImplicitUsings>
#   </PropertyGroup>
#   <ItemGroup>
#     <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
#     <PackageReference Include="Pomelo.EntityFrameworkCore.MySql" Version="8.0.0" />
#     <PackageReference Include="Microsoft.EntityFrameworkCore.Tools" Version="8.0.0" />
#   </ItemGroup>
#   <ItemGroup>
#     <ProjectReference Include="..\\Infrastructure\\{solution_name}.Infrastructure.csproj" />
#     <ProjectReference Include="..\\Application\\{solution_name}.Application.csproj" />
#     <ProjectReference Include="..\\Domain\\{solution_name}.Domain.csproj" />
#   </ItemGroup>
# </Project>
# """
#         structure_files.append({
#             "path": os.path.join(project["path"], f"{project['name']}.csproj"),
#             "content": csproj_content
#         })
#     return structure_files

# # Modified write_generated_files
# async def write_generated_files(output_dir, generated_files):
#     """Write generated files, including binary images, with duplicate prevention."""
#     written_files = set()
#     tasks = []
#     skipped_count = 0

#     async def write_single_file(file_info):
#         file_path = os.path.join(output_dir, file_info["path"])
#         file_dir = os.path.dirname(file_path)
#         if file_dir:
#             os.makedirs(file_dir, exist_ok=True)
#         try:
#             if file_info.get("is_binary", False):
#                 content = base64.b64decode(file_info["content"])
#                 async with aiofiles.open(file_path, "wb") as f:
#                     await f.write(content)
#             else:
#                 async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
#                     await f.write(file_info["content"])
#         except Exception as e:
#             print(f"Error writing file {file_info['path']}: {str(e)}")

#     for file_info in generated_files:
#         if not file_info or 'path' not in file_info or 'content' not in file_info:
#             print(f"Skipping invalid file entry: {file_info}")
#             continue
#         file_path = os.path.join(output_dir, file_info["path"])
#         normalized_path = os.path.normpath(file_path)
#         if normalized_path in written_files:
#             skipped_count += 1
#             print(f"Skipping duplicate file: {file_info['path']}")
#             continue
#         written_files.add(normalized_path)
#         tasks.append(write_single_file(file_info))

#     if tasks:
#         print(f"Concurrently writing {len(tasks)} unique files...")
#         await asyncio.gather(*tasks)
    
#     print(f"Finished writing. Total unique files: {len(tasks)}, skipped duplicates: {skipped_count}")

# async def create_zip(output_dir, zip_name):
#     """Zip the project directory."""
#     try:
#         def zip_directory():
#             with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
#                 for root, _, files in os.walk(output_dir):
#                     for file in files:
#                         file_path = os.path.join(root, file)
#                         arcname = os.path.relpath(file_path, output_dir)
#                         zipf.write(file_path, arcname)
       
#         await asyncio.get_event_loop().run_in_executor(None, zip_directory)
#         print(f"Project zipped to {zip_name}")
       
#     except Exception as e:
#         print(f"Error creating zip file: {str(e)}")
#         raise
 
# # ================================================================= #
# # MODIFICATION 1: Add this new function                             #
# # ================================================================= #


# @generation_app.post("/generate-project")
# async def generate_project(
#     bundle_file: UploadFile = File(...),
#     namespace: str = Form(default="MyApplication")
# ):
#     temp_bundle_dir = f"temp_bundle_{uuid.uuid4()}"
#     os.makedirs(temp_bundle_dir, exist_ok=True)
    
#     output_dir = "generated_project"
#     zip_name = f"{namespace}.zip"

#     if os.path.exists(output_dir):
#         shutil.rmtree(output_dir)
#     if os.path.exists(zip_name):
#         os.remove(zip_name)
    
#     try:
#         # 1. UNPACK THE BUNDLE
#         bundle_path = os.path.join(temp_bundle_dir, bundle_file.filename)
#         async with aiofiles.open(bundle_path, 'wb') as f:
#             content = await bundle_file.read()
#             await f.write(content)
        
#         unzip_dir = os.path.join(temp_bundle_dir, "unzipped")
#         with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
#             zip_ref.extractall(unzip_dir)
#         print("Successfully extracted analysis bundle.")

#         # 2. LOAD ANALYSIS DATA AND RAG INDEXES
#         with open(os.path.join(unzip_dir, "analysis.json"), 'r', encoding='utf-8') as f:
#             analysis_data = json.load(f)
        
#         storage_context_analysis = StorageContext.from_defaults(
#             persist_dir=os.path.join(unzip_dir, "analysis_index")
#         )
#         index_analysis = load_index_from_storage(storage_context_analysis)
        
#         storage_context_source = StorageContext.from_defaults(
#             persist_dir=os.path.join(unzip_dir, "source_code_index")
#         )
#         index_source = load_index_from_storage(storage_context_source)
        
#         query_engines = {
#             "analysis": index_analysis.as_query_engine(),
#             "source": index_source.as_query_engine()
#         }
#         print("RAG query engines loaded successfully.")

#         # 3. CREATE THE MASTER PLAN AND GENERATION QUEUE
#         project_plan = analyze_project_structure(analysis_data)
       
#        #=======================================================================
#         # <-- ADD THIS BLOCK TO PRINT THE PROJECT PLAN -->
#         print("\n" + "="*80)
#         print("--- [GEN.PY] RETURN VALUE OF analyze_project_structure (Project Plan) ---")
#         print("="*80)
#         # The project_plan contains sets, which are not JSON serializable by default.
#         # We convert them to lists for printing.
#         plan_for_printing = {key: sorted(list(value)) for key, value in project_plan.items()}
#         print(json.dumps(plan_for_printing, indent=2))
#         print("="*80 + "\n")
#         # =======================================================================

#         generation_queue = create_generation_queue(project_plan, namespace)
        
#          # =======================================================================
#         # <-- ADD THIS BLOCK TO PRINT THE GENERATION QUEUE -->
#         print("\n" + "="*80)
#         print("--- [GEN.PY] RETURN VALUE OF create_generation_queue (Generation Queue) ---")
#         print("="*80)
#         print(json.dumps(generation_queue, indent=2))
#         print("="*80 + "\n")
#         # =======================================================================


#         # 4. START THE ITERATIVE, STATE-AWARE GENERATION PIPELINE
#         generated_files = []
#         generated_code_cache = {}
#         rag_cache = {}  # Initialize RAG cache for query reuse
#         print(f"Starting generation for {len(generation_queue)} files...")

#         # Group files by layer to respect dependencies
#         layer_groups = {
#             'Entity': [],
#             'RepositoryInterface': [],
#             'ServiceInterface': [],
#             'Repository': [],
#             'DbContext': [],
#             'Service': [],
#             'Controller': [],
#             'View': [],
#             'HomeController': [],
#             'HomeView': []
#         }
#         for item in generation_queue:
#             layer_groups[item['type']].append(item)
        
#         # Process each layer sequentially, parallelize within each layer
#         for layer, items in layer_groups.items():
#             if not items:
#                 continue
#             print(f"Generating {len(items)} files for layer: {layer}")
#             tasks = [
#                 generate_single_file(item, query_engines, generated_code_cache, namespace, project_plan, rag_cache)
#                 for item in items
#             ]
#             results = await asyncio.gather(*tasks, return_exceptions=True)
#             for item, result in zip(items, results):
#                 if isinstance(result, Exception):
#                     print(f"Error generating {item['path']}: {str(result)}")
#                     continue
#                 clean_content = re.sub(r'^```(csharp|json|html)?\s*|\s*```$', '', result, flags=re.MULTILINE).strip()
#                 generated_files.append({"path": item['path'], "content": clean_content})
#                 generated_code_cache[os.path.basename(item['path'])] = clean_content
#         print("Iterative generation finished.")

#         # 5. HANDLE STATIC ASSETS
#         static_files = []
#         for asset in analysis_data.get("static_assets", []):
#             file_name = asset["file_name"]
#             content = asset["content"]
#             file_type = asset["type"]
#             if file_name.lower().endswith(('.js',)):
#                 target_path = os.path.join("Presentation", "wwwroot", "js", os.path.basename(file_name))
#             elif file_name.lower().endswith(('.css',)):
#                 target_path = os.path.join("Presentation", "wwwroot", "css", os.path.basename(file_name))
#             elif file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.ico')):
#                 target_path = os.path.join("Presentation", "wwwroot", "images", os.path.basename(file_name))
#             else:
#                 print(f"Skipping unrecognized static asset: {file_name}")
#                 continue
#             static_files.append({
#                 "path": target_path,
#                 "content": content,
#                 "is_binary": file_type == "image"
#             })

#         # 6. GENERATE BOILERPLATE AND PROJECT STRUCTURE FILES
#         structure_files = await create_project_structure(output_dir, namespace)
#         final_files_list = generated_files + structure_files + static_files

#         # 7. DYNAMICALLY CREATE Program.cs and other boilerplate
#         existing_paths = {os.path.normcase(f["path"]) for f in final_files_list}
#         boilerplate_files_to_add = []
#         entities = sorted(list(project_plan.get('entities', {'Entity'})))
#         di_registrations = []
#         for entity in entities:
#             di_registrations.append(f'builder.Services.AddScoped<I{entity}Repository, {entity}Repository>();')
#             di_registrations.append(f'builder.Services.AddScoped<I{entity}Service, {entity}Service>();')
#         di_registrations_string = '\n'.join(f'    {line}' for line in di_registrations)
#         program_content = f"""using Microsoft.EntityFrameworkCore;
# using {namespace}.Application.Interfaces;
# using {namespace}.Application.Services;
# using {namespace}.Infrastructure.Data;
# using {namespace}.Infrastructure.Repositories;

# var builder = WebApplication.CreateBuilder(args);

# builder.Services.AddDbContext<ApplicationDbContext>(options =>
#     options.UseMySql(builder.Configuration.GetConnectionString("DefaultConnection"),
#         ServerVersion.AutoDetect(builder.Configuration.GetConnectionString("DefaultConnection"))));

# // Register all discovered services and repositories
# {di_registrations_string}

# builder.Services.AddControllersWithViews();

# var app = builder.Build();

# if (!app.Environment.IsDevelopment())
# {{
#     app.UseExceptionHandler("/Home/Error");
#     app.UseHsts();
# }}

# app.UseHttpsRedirection();
# app.UseStaticFiles();
# app.UseRouting();
# app.UseAuthorization();

# app.MapControllerRoute(
#     name: "default",
#     pattern: "{{controller=Home}}/{{action=Index}}/{{id?}}");

# app.Run();"""
#         view_imports_content = f"@using {namespace}.Presentation\n@using {namespace}.Domain.Entities\n@addTagHelper *, Microsoft.AspNetCore.Mvc.TagHelpers"
#         view_start_content = "@{\n    Layout = \"_Layout\";\n}"
#         layout_content = f"""<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="utf-8" />
#     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
#     <title>@ViewData["Title"] - {namespace}</title>
#     <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" />
#     <link rel="stylesheet" href="~/css/site.css" asp-append-version="true" />
# </head>
# <body>
#     <header>
#         <nav class="navbar navbar-expand-sm navbar-toggleable-sm navbar-light bg-white border-bottom box-shadow mb-3">
#             <div class="container-fluid">
#                 <a class="navbar-brand" asp-area="" asp-controller="Home" asp-action="Index">{namespace}</a>
#             </div>
#         </nav>
#     </header>
#     <div class="container">
#         <main role="main" class="pb-3">
#             @RenderBody()
#         </main>
#     </div>
#     <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"></script>
#     <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
#     <script src="~/js/site.js" asp-append-version="true"></script>
#     @await RenderSectionAsync("Scripts", required: false)
# </body>
# </html>"""
#         appsettings_content = """{
#     "ConnectionStrings": {
#         "DefaultConnection": "Server=localhost;Database=UserDB;User=root;Password=yourpassword;"
#     },
#     "Logging": { "LogLevel": { "Default": "Information", "Microsoft.AspNetCore": "Warning" } },
#     "AllowedHosts": "*"
# }"""
#         validation_scripts_content = """<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-validate/1.19.3/jquery.validate.min.js"></script>
# <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-validation-unobtrusive/3.2.12/jquery.validate.unobtrusive.min.js"></script>"""
#         boilerplate_files_to_add.extend([
#             {"path": os.path.join("Presentation", "Program.cs"), "content": program_content},
#             {"path": os.path.join("Presentation", "Views", "_ViewImports.cshtml"), "content": view_imports_content},
#             {"path": os.path.join("Presentation", "Views", "_ViewStart.cshtml"), "content": view_start_content},
#             {"path": os.path.join("Presentation", "Views", "Shared", "_Layout.cshtml"), "content": layout_content},
#             {"path": os.path.join("Presentation", "Views", "Shared", "_ValidationScriptsPartial.cshtml"), "content": validation_scripts_content},
#             {"path": os.path.join("Presentation", "appsettings.json"), "content": appsettings_content},
#         ])
#         final_files_to_write = final_files_list + boilerplate_files_to_add
#         project_structures[namespace] = {
#             "namespace": namespace,
#             "files": final_files_to_write
#         }
#         await write_generated_files(output_dir, final_files_to_write)
#         await create_zip(output_dir, zip_name)
#         return FileResponse(zip_name, media_type="application/zip", filename=zip_name)
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
#     finally:
#         if os.path.exists(temp_bundle_dir):
#             shutil.rmtree(temp_bundle_dir)
#         if os.path.exists(output_dir):
#             shutil.rmtree(output_dir)

# @generation_app.get("/download/{namespace}")
# async def download_project(namespace: str):
#     """
#     Download the generated project ZIP file for the given namespace.
#     """
#     zip_name = f"{namespace}.zip"
#     if not os.path.exists(zip_name):
#         raise HTTPException(status_code=404, detail=f"Project ZIP for namespace '{namespace}' not found. Please generate the project first.")
   
#     try:
#         return FileResponse(
#             zip_name,
#             media_type="application/zip",
#             filename=zip_name
#         )
#     except Exception as e:
#         print(f"Error serving ZIP file for {namespace}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error downloading project: {str(e)}")
 
# @generation_app.get("/file-content/{namespace}/{file_path:path}")
# async def get_file_content(namespace: str, file_path: str):
#     """
#     Retrieve the content of a specific file from the generated project.
#     Note: This assumes the project structure is stored in memory or regenerated.
#     """
#     # Decode the file_path (handles URL-encoded paths)
#     decoded_file_path = unquote(file_path)
   
#     # Check if project structure exists in memory
#     if namespace not in project_structures:
#         raise HTTPException(status_code=404, detail=f"Project structure for namespace '{namespace}' not found.")
   
#     # Find the file in the stored project structure
#     for file in project_structures[namespace].get("files", []):
#         if file.get("path") == decoded_file_path:
#             return {"content": file.get("content", "")}
   
#     raise HTTPException(status_code=404, detail=f"File '{decoded_file_path}' not found in project '{namespace}'.")
 
# @generation_app.get("/project-structure/{namespace}")
# async def get_project_structure(namespace: str):
#     """
#     Retrieve the project structure for the given namespace.
#     """
#     if namespace not in project_structures:
#         raise HTTPException(status_code=404, detail=f"Project structure for namespace '{namespace}' not found.")
   
#     return project_structures[namespace]
 

# @generation_app.get("/")
# async def root():
#     return {"message": "ASP.NET Core Project Generator API"}
 
# @generation_app.get("/health")
# async def health_check():
#     return {"status": "healthy"}
 
# if __name__ == "__main__":
#     import uvicorn
#     print("Starting Generation API server (standalone)...")
#     uvicorn.run(generation_app, host="0.0.0.0", port=8002)
   





































































































# gen.py

import base64
import os
import json
import re
import zipfile
import shutil
from urllib.parse import unquote
import uuid
import asyncio
import aiohttp
from fastapi import FastAPI, UploadFile, Form, File, HTTPException, Body
from fastapi.responses import FileResponse
import aiofiles
from collections import defaultdict
from llama_index.core import Settings, StorageContext, load_index_from_storage, VectorStoreIndex, Document, SimpleDirectoryReader
from llama_index.llms.azure_openai import AzureOpenAI
from typing import Dict, Any, List

generation_app = FastAPI(title="Project Generation Service")

# A new base directory for temporary session data, matching analysis.py
SESSION_TEMP_BASE_DIR = "temp_sessions"
project_structures = {} # In-memory cache for file preview

# --- LlamaIndex LLM Configuration ---
AZURE_ENDPOINT = "https://azure-openai-uk.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
AZURE_API_KEY = "NkHVD9xPtHLIvi2cgfcdfNdZnMdyZFpl02NvDHuW7fRf36cxrHerJQQJ99ALACmepeSXJ3w3AAABACOGrbaC"

try:
    AZURE_LLM_BASE_ENDPOINT = "https://azure-openai-uk.openai.azure.com/"
    AZURE_LLM_DEPLOYMENT_NAME = "gpt-4o"
    AZURE_LLM_API_VERSION = "2024-08-01-preview"
    llm = AzureOpenAI(
        model="gpt-4o",
        deployment_name=AZURE_LLM_DEPLOYMENT_NAME,
        api_key=AZURE_API_KEY,
        azure_endpoint=AZURE_LLM_BASE_ENDPOINT,
        api_version=AZURE_LLM_API_VERSION,
    )
    Settings.llm = llm
    print("✅ LlamaIndex LLM configured successfully to use Azure OpenAI.")
except Exception as e:
    print(f"❌ CRITICAL ERROR: Failed to configure LLM. LlamaIndex query engines will not work. Error: {e}")
    raise e


def create_generation_queue(project_plan: dict, namespace: str) -> list:
    """Creates a generation queue directly from the user-approved project plan."""
    queue = []
    
    # Layer 1: Domain Entities
    for entity in project_plan.get('entities', []):
        if 'name' in entity:
            queue.append({"path": f"Domain/Entities/{entity['name']}.cs", "type": "Entity", "entity_name": entity['name']})

    # Layer 2: Application Interfaces
    for repo in project_plan.get('repositories', []):
        if 'name' in repo:
            entity_name = repo['name'].replace('Repository', '')
            queue.append({"path": f"Application/Interfaces/I{entity_name}Repository.cs", "type": "RepositoryInterface", "entity_name": entity_name})
    
    for service in project_plan.get('services', []):
        if 'name' in service:
            entity_name = service['name'].replace('Service', '')
            queue.append({"path": f"Application/Interfaces/I{entity_name}Service.cs", "type": "ServiceInterface", "entity_name": entity_name})

    # Layer 3: Infrastructure
    for repo in project_plan.get('repositories', []):
        if 'name' in repo:
            entity_name = repo['name'].replace('Repository', '')
            queue.append({"path": f"Infrastructure/Repositories/{repo['name']}.cs", "type": "Repository", "entity_name": entity_name})
    
    all_entities_str = ",".join([e['name'] for e in project_plan.get('entities', []) if 'name' in e])
    if all_entities_str:
        queue.append({"path": "Infrastructure/Data/ApplicationDbContext.cs", "type": "DbContext", "entity_name": all_entities_str})

    # Layer 4: Application Services
    for service in project_plan.get('services', []):
        if 'name' in service:
            entity_name = service['name'].replace('Service', '')
            queue.append({"path": f"Application/Services/{service['name']}.cs", "type": "Service", "entity_name": entity_name})

    # Layer 5: Presentation Layer
    for controller in project_plan.get('controllers', []):
        if 'name' in controller:
            entity_name = controller['name'].replace('Controller', '')
            queue.append({"path": f"Presentation/Controllers/{controller['name']}.cs", "type": "Controller", "entity_name": entity_name})

    for view in project_plan.get('views', []):
        if 'controller' in view and 'name' in view:
            controller_folder = view['controller'].replace('Controller', '')
            entity_name = controller_folder.rstrip('s')
            queue.append({
                "path": f"Presentation/Views/{controller_folder}/{view['name']}",
                "type": "View",
                "entity_name": entity_name
            })

    queue.append({"path": "Presentation/Controllers/HomeController.cs", "type": "HomeController", "entity_name": "DefaultPage"})
    queue.append({"path": "Presentation/Views/Home/Index.cshtml", "type": "HomeView", "entity_name": "DefaultPage"})

    return queue


async def create_rag_indexes_for_generation(project_plan: dict, source_code_dir: str):
    """
    
    Creates RAG indexes on-the-fly from the source code and the refined plan.
    """
    print("Creating RAG indexes for generation...")
    
    # Index for the refined project plan (this was previously named 'plan', renaming back to 'analysis' for compatibility)
    analysis_docs = [Document(text=json.dumps(project_plan, indent=2), metadata={"source": "refined_project_plan"})]
    analysis_index = VectorStoreIndex.from_documents(analysis_docs)
    print("Refined plan RAG index created in-memory.")

    # Index for the raw source code
    source_reader = SimpleDirectoryReader(input_dir=source_code_dir, recursive=True, exclude=['*.zip', '*.rar', '*.7z'])
    source_docs = source_reader.load_data()
    source_index = VectorStoreIndex.from_documents(source_docs)
    print("Source code RAG index created in-memory.")
    
    # Return a dictionary with the original keys expected by generate_single_file
    return {
        "analysis": analysis_index.as_query_engine(),
        "source": source_index.as_query_engine()
    }
# Replace the entire function with this new version



async def create_project_structure(output_dir, project_name):
    """Creates the ASP.NET Core project structure directories and returns .sln and .csproj files."""
    solution_name = project_name
    projects = [
        {"name": f"{solution_name}.Domain", "type": "ClassLibrary", "path": "Domain"},
        {"name": f"{solution_name}.Application", "type": "ClassLibrary", "path": "Application"},
        {"name": f"{solution_name}.Infrastructure", "type": "ClassLibrary", "path": "Infrastructure"},
        {"name": f"{solution_name}.Presentation", "type": "AspNetCore", "path": "Presentation"}
    ]
    structure_files = []
    
    # ### FIX ### - Added 'images' directory and all other necessary folders for a clean structure.
    os.makedirs(os.path.join(output_dir, "Presentation", "wwwroot", "css"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "Presentation", "wwwroot", "js"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "Presentation", "wwwroot", "images"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "Presentation", "Views", "Shared"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "Presentation", "Views", "Home"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "Domain", "Entities"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "Application", "Services"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "Application", "Interfaces"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "Infrastructure", "Repositories"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "Infrastructure", "Data"), exist_ok=True)
    
    # Generate .sln file content
    project_guids = {p['name']: str(uuid.uuid4()).upper() for p in projects}
    solution_content = f"Microsoft Visual Studio Solution File, Format Version 12.00\n"
    for p in projects:
        project_guid = project_guids[p['name']]
        project_path = os.path.join(p['path'], f"{p['name']}.csproj").replace('/', '\\')
        solution_content += f'Project("{{9A19103F-16F7-4668-BE54-9A1E7A4F7556}}") = "{p["name"]}", "{project_path}", "{{{project_guid}}}"\nEndProject\n'
    solution_content += "Global\n\tGlobalSection(SolutionConfigurationPlatforms) = preSolution\n\t\tDebug|Any CPU = Debug|Any CPU\n\t\tRelease|Any CPU = Release|Any CPU\n\tEndGlobalSection\n\tGlobalSection(ProjectConfigurationPlatforms) = postSolution\n"
    for p in projects:
        project_guid = project_guids[p['name']]
        solution_content += f'\t\t{{{project_guid}}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU\n\t\t{{{project_guid}}}.Debug|Any CPU.Build.0 = Debug|Any CPU\n\t\t{{{project_guid}}}.Release|Any CPU.ActiveCfg = Release|Any CPU\n\t\t{{{project_guid}}}.Release|Any CPU.Build.0 = Release|Any CPU\n'
    solution_content += "\tEndGlobalSection\nEndGlobal\n"
    structure_files.append({"path": f"{solution_name}.sln", "content": solution_content})

    # Generate .csproj files with corrected, explicit logic
    for p in projects:
        csproj_content = ""
        project_path = p["path"]

        if project_path == "Domain":
            csproj_content = '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>'
        
        elif project_path == "Application":
            csproj_content = f'<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup><ItemGroup><ProjectReference Include="..\\Domain\\{solution_name}.Domain.csproj" /></ItemGroup></Project>'
        
        elif project_path == "Infrastructure":
            csproj_content = f"""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
    <PackageReference Include="Pomelo.EntityFrameworkCore.MySql" Version="8.0.0" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.Tools" Version="8.0.0" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\\Domain\\{solution_name}.Domain.csproj" />
    <ProjectReference Include="..\\Application\\{solution_name}.Application.csproj" />
  </ItemGroup>
</Project>"""
        
        elif project_path == "Presentation":
            # ### CORRECTED Presentation.csproj CONTENT ###
            csproj_content = f"""<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
    <PackageReference Include="Pomelo.EntityFrameworkCore.MySql" Version="8.0.0" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.Tools" Version="8.0.0" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\\Infrastructure\\{solution_name}.Infrastructure.csproj" />
    <ProjectReference Include="..\\Application\\{solution_name}.Application.csproj" />
    <ProjectReference Include="..\\Domain\\{solution_name}.Domain.csproj" />
  </ItemGroup>
</Project>"""

        structure_files.append({"path": os.path.join(p["path"], f"{p['name']}.csproj"), "content": csproj_content})
        
    return structure_files

def copy_static_assets(source_dir: str, output_dir: str):
    """
    Scans the source directory and copies static assets to the wwwroot of the output directory.
    """
    print("Copying static assets...")
    wwwroot_path = os.path.join(output_dir, "Presentation", "wwwroot")
    css_path = os.path.join(wwwroot_path, "css")
    js_path = os.path.join(wwwroot_path, "js")
    images_path = os.path.join(wwwroot_path, "images")

    # Ensure target directories exist (they should from create_project_structure, but this is safer)
    os.makedirs(css_path, exist_ok=True)
    os.makedirs(js_path, exist_ok=True)
    os.makedirs(images_path, exist_ok=True)

    copied_files_count = 0
    static_extensions = {
        '.css': css_path,
        '.js': js_path,
        '.png': images_path,
        '.jpg': images_path,
        '.jpeg': images_path,
        '.gif': images_path,
        '.svg': images_path,
        '.ico': images_path,
    }

    for root, _, files in os.walk(source_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in static_extensions:
                source_file_path = os.path.join(root, file)
                target_dir = static_extensions[ext]
                target_file_path = os.path.join(target_dir, os.path.basename(file))
                
                # To avoid overwriting boilerplate files like site.css with originals
                # unless you want that behavior. For now, we'll copy if it doesn't exist.
                if not os.path.exists(target_file_path):
                    shutil.copy2(source_file_path, target_file_path)
                    copied_files_count += 1
    
    print(f"✅ Copied {copied_files_count} static asset(s) to wwwroot.")

async def generate_single_file(item: dict, query_engines: dict, generated_code_cache: dict, namespace: str, project_plan: dict, rag_cache: dict = None) -> str:
    """
    Generates a single file using a refined prompt that STRICTLY adheres to the project plan.
    Uses templates for simple boilerplate and AI for complex, dynamic files.
    """
    if rag_cache is None:
        rag_cache = {}
    file_type = item['type']
    entity_name = item.get('entity_name', 'General')

    # --- TEMPLATE-BASED GENERATION FOR BOILERPLATE ---
    if file_type == 'HomeController':
        print("  -> Using deterministic template for HomeController.")
        return f"""using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;

namespace {namespace}.Presentation.Controllers
{{
    public class HomeController : Controller
    {{
        public IActionResult Index()
        {{
            return View();
        }}

        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public IActionResult Error()
        {{
            return View(new {{ RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier }});
        }}
    }}
}}"""

    if file_type == 'HomeView':
        print("  -> Using deterministic template for HomeView.")
        return f"""@{{
    ViewData["Title"] = "Home Page";
}}

<div class="text-center">
    <h1 class="display-4">Welcome to {namespace}</h1>
    <p>Your application has been successfully generated.</p>
</div>
"""

    if file_type == 'DbContext':
        print("  -> Using deterministic template for DbContext.")
        entity_name_list = item.get('entity_name', '').split(',')
        all_entities = [name for name in entity_name_list if name]
        db_set_properties = "".join(f"        public DbSet<{entity}> {entity}s {{ get; set; }}\n" for entity in sorted(all_entities))
        return f"""using Microsoft.EntityFrameworkCore;
using {namespace}.Domain.Entities;
namespace {namespace}.Infrastructure.Data
{{
    public class ApplicationDbContext : DbContext
    {{
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options) {{ }}
{db_set_properties}
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {{
            base.OnModelCreating(modelBuilder);
        }}
    }}
}}"""

    # --- AI-DRIVEN GENERATION FOR DYNAMIC FILES ---
    specification_context = ""
    try:
        if file_type == 'Entity':
            entity_spec = next((e for e in project_plan.get('entities', []) if e.get('name') == entity_name), None)
            if entity_spec:
                properties_str = "\n".join([f"    - Property: {prop.get('name', 'Unnamed')}, Type: {prop.get('type', 'string')}" for prop in entity_spec.get('properties', [])])
                specification_context = f"Entity Name: {entity_spec['name']}\nProperties:\n{properties_str}"
        elif file_type == 'ServiceInterface':
            service_spec = next((s for s in project_plan.get('services', []) if s.get('name') == f"{entity_name}Service"), None)
            if service_spec:
                methods_str = "\n".join([f"    - Method: {method}" for method in service_spec.get('methods', [])])
                specification_context = f"Interface Name: I{service_spec['name']}\nMethods to define:\n{methods_str}"
        elif file_type == 'RepositoryInterface':
            repo_spec = next((r for r in project_plan.get('repositories', []) if r.get('name') == f"{entity_name}Repository"), None)
            if repo_spec:
                methods_str = "\n".join([f"    - Method: {method}" for method in repo_spec.get('methods', [])])
                specification_context = f"Interface Name: I{repo_spec['name']}\nMethods to define:\n{methods_str}"
        elif file_type == 'View':
            entity_spec = next((e for e in project_plan.get('entities', []) if e.get('name') == entity_name), None)
            if entity_spec:
                properties_str = "\n".join([f"    - Property: {prop.get('name', 'Unnamed')}, Type: {prop.get('type', 'string')}" for prop in entity_spec.get('properties', [])])
                specification_context = f"This view is for the '{entity_name}' model.\nModel Properties:\n{properties_str}"
    except Exception as e:
        print(f"Warning: Could not build specification context for {file_type} {entity_name}. Error: {e}")

    context = ""
    required_using_statements = f"using {namespace}.Domain.Entities;\n"
    if file_type in ['Service', 'Repository', 'Controller']:
        required_using_statements += f"using {namespace}.Application.Interfaces;\n"
    if file_type == 'Repository':
        required_using_statements += f"using {namespace}.Infrastructure.Data;\n"
    if file_type == 'Controller':
        required_using_statements += f"using Microsoft.AspNetCore.Mvc;\n"
    context += f"// CONTEXT: You MUST include these using statements if relevant:\n{required_using_statements}\n"

    if file_type == 'Service':
        interface_name = f"I{entity_name}Service.cs"
        repo_interface_name = f"I{entity_name}Repository.cs"
        if interface_name in generated_code_cache:
            context += f"// CONTEXT: Implement this interface:\n{generated_code_cache[interface_name]}\n"
        if repo_interface_name in generated_code_cache:
            context += f"// CONTEXT: Inject this repository:\n{generated_code_cache[repo_interface_name]}\n"
    if file_type == 'Repository':
        interface_name = f"I{entity_name}Repository.cs"
        if interface_name in generated_code_cache:
            context += f"// CONTEXT: Implement this interface:\n{generated_code_cache[interface_name]}\n"
    if file_type == 'Controller':
        service_entity_name = entity_name.rstrip('s')
        service_interface_name = f"I{service_entity_name}Service.cs"
        if service_interface_name in generated_code_cache:
            context += f"// CONTEXT: Inject this service:\n{generated_code_cache[service_interface_name]}\n"

    legacy_context = ""
    cache_key = f"{entity_name}_{file_type}"
    if cache_key in rag_cache:
        legacy_context = rag_cache[cache_key]
        print(f"Using cached RAG data for {cache_key}")
    else:
        try:
            analysis_query = f"Retrieve the detailed analysis for all legacy files related to the '{entity_name}' entity or feature."
            source_query = f"Retrieve the full source code of the single most relevant legacy file for implementing the '{entity_name}' feature."
            analysis_response = await asyncio.to_thread(query_engines['analysis'].query, analysis_query)
            source_response = await asyncio.to_thread(query_engines['source'].query, source_query)
            legacy_context += f"// LEGACY ANALYSIS:\n/*\n{str(analysis_response)}\n*/\n\n"
            legacy_context += f"// LEGACY SOURCE CODE:\n/*\n{str(source_response)}\n*/\n"
            rag_cache[cache_key] = legacy_context
            print(f"Cached RAG data for {cache_key}")
        except Exception as e:
            print(f"Warning: RAG query failed for {file_type}. Error: {e}")
            return f"// ERROR: RAG query failed for {file_type}."

    prompt = f"""You are an expert C# developer migrating a legacy application. Your work must be precise and strictly follow all rules.

---
**FILE SPECIFICATION**
- **File Path:** {item['path']}
- **File Type:** {file_type}
- **Primary Entity:** {entity_name}
- **Project Namespace:** {namespace}
---
**CONTEXT & REQUIREMENTS**

**PROJECT PLAN SPECIFICATION (Source of Truth):**
This is the user-approved plan. It is the absolute source of truth for all structural elements like class names, property names, types, and method signatures.
{specification_context if specification_context else "No specific plan details provided for this file."}
**Generated Code Context (Dependencies):**
{context if context else "// No previously generated code context was provided."}

**Legacy System Context (For Business Logic INSPIRATION ONLY):**
{legacy_context if legacy_context else "// No legacy context was retrieved."}
---
**STRICT GENERATION RULES**

1.  **PRIORITY #1 - ADHERE TO THE PLAN:** You MUST generate code that **exactly** matches the `PROJECT PLAN SPECIFICATION`. For example, if the plan specifies an entity has 5 properties, you MUST generate exactly those 5 properties. This plan OVERRULES any conflicting information from the legacy context.
2.  **Use Legacy Context for Logic:** The `Legacy System Context` should ONLY be used as inspiration for the business logic *inside* the methods. Do not infer any structural elements from it.
3.  **Correct Inheritance:** Controllers MUST inherit from `Microsoft.AspNetCore.Mvc.Controller`.
4.  **Code Purity:** Generate ONLY the raw C# or CSHTML code for the specified file. Do not include any explanations or markdown wrappers.
5.  **Dependency Injection:** Use constructor injection for dependencies as shown in the `Generated Code Context`.
---
Generate the code now.
"""

    headers = {"Content-Type": "application/json", "api-key": AZURE_API_KEY}
    payload = {"messages": [{"role": "user", "content": prompt}], "max_tokens": 4096, "temperature": 0.05}
    async with aiohttp.ClientSession() as session:
        async with session.post(AZURE_ENDPOINT, json=payload, headers=headers) as response:
            if response.status == 200:
                response_json = await response.json()
                return response_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            else:
                error_text = await response.text()
                print(f"Error generating {item['path']}: {error_text}")
                return f"// ERROR: Could not generate file. Status: {response.status}"



def create_boilerplate_files(namespace, project_plan):
    """Creates content for standard files like Program.cs, _Layout.cshtml, etc."""
    
    # ### FIX ### - This logic now ONLY uses entities defined in the approved plan.
    # It will no longer try to create a non-existent "DefaultPage" service.
    di_registrations = []
    if 'services' in project_plan and 'repositories' in project_plan:
        # Create a mapping for easy lookup
        service_map = {s['name']: s for s in project_plan.get('services', [])}
        
        for repo in project_plan.get('repositories', []):
            repo_name = repo.get('name')
            if not repo_name: continue
            
            # Infer service name from repository name (e.g., UserRepository -> UserService)
            entity_name = repo_name.replace('Repository', '')
            service_name = f"{entity_name}Service"
            
            # Check if the corresponding service exists in the plan before adding DI
            if service_name in service_map:
                interface_repo_name = f"I{repo_name}"
                interface_service_name = f"I{service_name}"
                di_registrations.append(f'builder.Services.AddScoped<{interface_repo_name}, {repo_name}>();')
                di_registrations.append(f'builder.Services.AddScoped<{interface_service_name}, {service_name}>();')

    di_registrations_string = '\n'.join(f'    {line}' for line in di_registrations)
    
    # --- The rest of the boilerplate content is largely the same ---
    
    program_content = f"""using Microsoft.EntityFrameworkCore;
using {namespace}.Application.Interfaces;
using {namespace}.Application.Services;
using {namespace}.Infrastructure.Data;
using {namespace}.Infrastructure.Repositories;

var builder = WebApplication.CreateBuilder(args);

var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseMySql(connectionString, ServerVersion.AutoDetect(connectionString)));

// Register all discovered services and repositories from the project plan
{di_registrations_string}

builder.Services.AddControllersWithViews();
var app = builder.Build();

if (!app.Environment.IsDevelopment())
{{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}}
app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();
app.UseAuthorization();
app.MapControllerRoute(
    name: "default",
    pattern: "{{controller=Home}}/{{action=Index}}/{{id?}}");
app.Run();"""

    layout_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>@ViewData["Title"] - {namespace}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" />
    <link rel="stylesheet" href="~/css/site.css" asp-append-version="true" />
</head>
<body>
    <header>
        <nav class="navbar navbar-expand-sm navbar-toggleable-sm navbar-light bg-white border-bottom box-shadow mb-3">
            <div class="container-fluid">
                <a class="navbar-brand" asp-area="" asp-controller="Home" asp-action="Index">{namespace}</a>
            </div>
        </nav>
    </header>
    <div class="container">
        <main role="main" class="pb-3">
            @RenderBody()
        </main>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="~/js/site.js" asp-append-version="true"></script>
    @await RenderSectionAsync("Scripts", required: false)
</body>
</html>"""
    
    appsettings_content = """{
    "ConnectionStrings": {
        "DefaultConnection": "Server=localhost;Database=librarysystem;User=root;Password=xxxxx;"
    },
    "Logging": { "LogLevel": { "Default": "Information", "Microsoft.AspNetCore": "Warning" } },
    "AllowedHosts": "*"
}"""
    
    validation_scripts_content = """<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-validate/1.19.3/jquery.validate.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-validation-unobtrusive/3.2.12/jquery.validate.unobtrusive.min.js"></script>"""
    
    return [
        {"path": os.path.join("Presentation", "Program.cs"), "content": program_content},
        {"path": os.path.join("Presentation", "Views", "_ViewImports.cshtml"), "content": f"@using {namespace}.Presentation\n@using {namespace}.Domain.Entities\n@addTagHelper *, Microsoft.AspNetCore.Mvc.TagHelpers"},
        {"path": os.path.join("Presentation", "Views", "_ViewStart.cshtml"), "content": "@{\n    Layout = \"_Layout\";\n}"},
        {"path": os.path.join("Presentation", "Views", "Shared", "_Layout.cshtml"), "content": layout_content},
        {"path": os.path.join("Presentation", "Views", "Shared", "_ValidationScriptsPartial.cshtml"), "content": validation_scripts_content},
        {"path": os.path.join("Presentation", "appsettings.json"), "content": appsettings_content},
    ]

async def write_generated_files(output_dir, generated_files):
    """Writes generated files with duplicate prevention."""
    written_files = set()
    tasks = []
    
    async def write_single_file(file_info):
        file_path = os.path.join(output_dir, file_info["path"])
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(file_info["content"])

    for file_info in generated_files:
        if not file_info or 'path' not in file_info or 'content' not in file_info:
            continue
        
        file_path = os.path.join(output_dir, file_info["path"])
        normalized_path = os.path.normpath(file_path)
        if normalized_path in written_files:
            continue
        written_files.add(normalized_path)
        tasks.append(write_single_file(file_info))
    
    await asyncio.gather(*tasks)


async def create_zip(output_dir, zip_name):
    """Zips the project directory."""
    await asyncio.get_event_loop().run_in_executor(
        None, lambda: shutil.make_archive(zip_name.replace('.zip', ''), 'zip', output_dir)
    )
    print(f"Project zipped to {zip_name}")


@generation_app.post("/generate-project-from-plan")
async def generate_project_from_plan(
    namespace: str = Form(...),
    session_id: str = Form(...),
    refined_plan: str = Form(...),
    
):
    try:
        project_plan = json.loads(refined_plan)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for refined_plan.")
        
    session_dir = os.path.join(SESSION_TEMP_BASE_DIR, session_id)
    output_dir = f"generated_project_{session_id}"
    zip_name = f"{namespace}.zip"

    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found or has expired.")

    if os.path.exists(output_dir): shutil.rmtree(output_dir)
    if os.path.exists(zip_name): os.remove(zip_name)
    
    try:
        query_engines = await create_rag_indexes_for_generation(project_plan, session_dir)
        generation_queue = create_generation_queue(project_plan, namespace)
        
        generated_files = []
        generated_code_cache = {}
        rag_cache = {}
        print(f"Starting generation for {len(generation_queue)} files based on refined plan...")
        
        layer_groups = defaultdict(list)
        for item in generation_queue:
            layer_groups[item['type']].append(item)
        
        ordered_layers = ['Entity', 'RepositoryInterface', 'ServiceInterface', 'Repository', 'DbContext', 'Service', 'Controller', 'View', 'HomeController', 'HomeView']
        for layer in ordered_layers:
            items = layer_groups[layer]
            if not items: continue
            print(f"Generating {len(items)} files for layer: {layer}")
            tasks = [generate_single_file(item, query_engines, generated_code_cache, namespace, project_plan, rag_cache) for item in items]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for item, result in zip(items, results):
                if isinstance(result, Exception):
                    print(f"Error generating {item['path']}: {str(result)}")
                    continue
                clean_content = re.sub(r'^```(csharp|json|html)?\s*|\s*```$', '', result, flags=re.MULTILINE).strip()
                generated_files.append({"path": item['path'], "content": clean_content})
                generated_code_cache[os.path.basename(item['path'])] = clean_content
        print("Iterative generation finished.")

        # ### MODIFIED SECTION ###
        
        # 1. Create the project directory structure FIRST
        structure_files = await create_project_structure(output_dir, namespace)
        
        # 2. Write the generated C# and CSHTML files
        boilerplate_files = create_boilerplate_files(namespace, project_plan)
        final_files_to_write = generated_files + structure_files + boilerplate_files
        project_structures[namespace] = {"namespace": namespace, "files": final_files_to_write}
        await write_generated_files(output_dir, final_files_to_write)
        
        # 3. NOW, copy the static assets from the original source to the new structure
        copy_static_assets(source_dir=session_dir, output_dir=output_dir)
        
        # 4. Finally, zip the completed directory
        await create_zip(output_dir, zip_name)
        
        return FileResponse(zip_name, media_type="application/zip", filename=zip_name)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error during generation: {str(e)}")
    finally:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
# --- Other endpoints for file preview and management ---


@generation_app.get("/project-structure/{namespace}")
async def get_project_structure(namespace: str):
    if namespace not in project_structures:
        raise HTTPException(status_code=404, detail=f"Project structure for namespace '{namespace}' not found.")
    return project_structures[namespace]

@generation_app.get("/file-content/{namespace}/{file_path:path}")
async def get_file_content(namespace: str, file_path: str):
    decoded_file_path = unquote(file_path)
    if namespace not in project_structures:
        raise HTTPException(status_code=404, detail=f"Project for namespace '{namespace}' not found.")
    
    for file in project_structures[namespace].get("files", []):
        if file.get("path") == decoded_file_path:
            return {"content": file.get("content", "")}
    
    raise HTTPException(status_code=404, detail=f"File '{decoded_file_path}' not found.")

@generation_app.get("/")
async def root():
    return {"message": "ASP.NET Core Project Generator API"}
 
@generation_app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("Starting Generation API server (standalone)...")
    uvicorn.run(generation_app, host="0.0.0.0", port=8002)