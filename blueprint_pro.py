# Blueprint Generator - Enhanced Context & Features (v5 - Deployment Target Added)
# Left: Tabs (Setup, Modules, Preview/Gen) | Right: Options (Design, AI, Gen)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import threading
import importlib.util
import subprocess
from abc import ABC, abstractmethod
# import uuid # Keep integer IDs for simplicity with Treeview iid

# --- AI Library Imports & Checks ---
openai_available = importlib.util.find_spec("openai") is not None
gemini_available = importlib.util.find_spec("google.generativeai") is not None

if openai_available:
    from openai import OpenAI, AuthenticationError, APIConnectionError, NotFoundError
else:
    OpenAI, AuthenticationError, APIConnectionError, NotFoundError = None, Exception, Exception, Exception

if gemini_available:
    import google.generativeai as genai
    from google.api_core import exceptions as google_exceptions
else:
    genai, google_exceptions = None, None


# --- Configuration Data ---
# ... (LANGUAGE_MAP, FRAMEWORKS, etc. tetap sama) ...
PROGRAMMING_LANGUAGES = sorted(list(set(["Python", "JavaScript", "TypeScript", "Java", "C#", "C++", "PHP", "Go", "Ruby", "Swift", "Kotlin", "Rust", "HTML", "CSS", "SQL", "Bash/Shell", "PowerShell", "Dart", "Scala", "Perl", "R", "Objective-C", "Lua", "Groovy", "MATLAB", "Assembly", "C", "GDScript", "Julia", "Zig"])))
LANGUAGE_MAP = { "Web": sorted(["HTML", "CSS", "JavaScript", "TypeScript", "Python", "PHP", "Ruby", "Java", "C#", "Go", "Rust", "Kotlin", "Swift", "SQL", "Bash/Shell"]), "Desktop App (EXE/DMG)": sorted(["Python", "C#", "Java", "C++", "Swift", "Objective-C", "Rust", "JavaScript", "Dart", "C", "Kotlin"]), "Mobile App": sorted(["Kotlin", "Java", "Swift", "Objective-C", "Dart", "JavaScript", "TypeScript", "C#", "C++", "Rust"]), "API Only": sorted(["Python", "Go", "Java", "C#", "Ruby", "PHP", "JavaScript", "TypeScript", "Rust", "Kotlin", "Swift", "Scala", "SQL", "Bash/Shell"]), "CLI Tool": sorted(["Python", "Go", "Rust", "Bash/Shell", "PowerShell", "C++", "C", "C#", "Java", "Ruby", "Perl", "JavaScript", "Swift", "Zig"]), "Library/SDK": sorted(["Python", "Java", "C#", "C++", "C", "JavaScript", "TypeScript", "Go", "Rust", "Swift", "Kotlin", "PHP", "Ruby", "Objective-C", "Zig"]), "Data Science": sorted(["Python", "R", "SQL", "Scala", "Java", "MATLAB", "Julia"]), "Game": sorted(["C++", "C#", "Java", "Python", "Lua", "JavaScript", "Rust", "GDScript", "Swift"]), "IoT": sorted(["C", "C++", "Python", "Java", "JavaScript", "Lua", "Rust", "Bash/Shell", "Go"]), "__fallback__": sorted(PROGRAMMING_LANGUAGES)}
all_langs_in_map = set(lang for sublist in LANGUAGE_MAP.values() for lang in sublist if lang != "__fallback__"); PROGRAMMING_LANGUAGES = sorted(list(set(PROGRAMMING_LANGUAGES) | all_langs_in_map)); LANGUAGE_MAP["__fallback__"] = sorted(PROGRAMMING_LANGUAGES)
WEB_FRAMEWORKS = { "python": ["Django", "Flask", "FastAPI", "Pyramid", "None"], "javascript": ["Express", "Koa", "NestJS", "Next.js (React)", "Nuxt.js (Vue)", "SvelteKit", "None"], "typescript": ["Express", "Koa", "NestJS", "Next.js (React)", "Nuxt.js (Vue)", "Angular", "SvelteKit", "None"], "java": ["Spring Boot", "Quarkus", "Jakarta EE", "Micronaut", "None"], "c#": ["ASP.NET Core", "None"], "ruby": ["Ruby on Rails", "Sinatra", "None"], "php": ["Laravel", "Symfony", "CodeIgniter", "None"], "go": ["Gin", "Echo", "Fiber", "net/http", "None"], "rust": ["Actix Web", "Rocket", "Axum", "Warp", "None"], "kotlin": ["Spring Boot", "Ktor", "None"], "swift": ["Vapor", "Hummingbird", "None"],}
UI_LIBS = { "javascript": ["React", "Vue", "Angular", "Svelte", "SolidJS", "Preact", "Alpine.js", "HTMX", "None"], "typescript": ["React", "Vue", "Angular", "Svelte", "SolidJS", "Preact", "None"], "python": ["HTMX (with backend)", "Streamlit", "Dash", "NiceGUI", "None"], "dart": ["Flutter", "None"], "c#": ["Blazor", "MAUI", "WinForms", "WPF", "Uno Platform", "Avalonia UI", "None"], "swift": ["SwiftUI", "UIKit", "None"], "kotlin": ["Jetpack Compose (Android/Desktop)", "None"], "java": ["JavaFX", "Swing", "None"], "rust": ["Leptos", "Dioxus", "Yew", "Iced", "None"]}
STATE_MANAGEMENT = { "javascript": ["Redux", "Zustand", "Jotai", "Valtio", "Recoil", "Pinia (Vue)", "NgRx (Angular)", "Context API (React)", "None"], "typescript": ["Redux", "Zustand", "Jotai", "Valtio", "Recoil", "Pinia (Vue)", "NgRx (Angular)", "Context API (React)", "None"], "dart": ["Provider", "Riverpod", "Bloc/Cubit", "GetX", "None"], "rust": ["Sycamore Signals", "Leptos Signals", "Dioxus Signals", "Shared State Libs", "None"]}
DATABASES = sorted(["PostgreSQL", "MySQL", "SQLite", "SQL Server", "Oracle", "MongoDB", "Redis", "Cassandra", "Elasticsearch", "DynamoDB", "Firebase Realtime/Firestore", "Supabase (Postgres)", "None"])


# --- AI Service Abstraction & Implementations ---
class AIService(ABC):
    @abstractmethod
    def list_models(self, api_key: str) -> list[str]: pass
    @abstractmethod
    def generate_text(self, api_key: str, model: str, prompt: str, temperature: float = 0.3) -> str: pass

class OpenAIService(AIService):
    # ... (Implementasi OpenAIService tetap sama) ...
    def list_models(self, api_key: str) -> list[str]:
        if not openai_available: raise ImportError("OpenAI package not installed.")
        if not api_key: raise ValueError("OpenAI API Key required.")
        try:
            client=OpenAI(api_key=api_key); models=client.models.list()
            gpt_models=sorted([m.id for m in models.data if'gpt'in m.id and m.id.find('instruct')==-1 and m.id.find('vision')==-1 and m.id.find('embedding')==-1 and m.id.find('audio')==-1 and m.id.find('tts')==-1 and m.id.find('whisper')==-1 and m.id.find('dall-e')==-1 and not m.id.endswith(('-0301','-0314','-0613'))])
            priority=['gpt-4o','gpt-4-turbo','gpt-4','gpt-3.5-turbo']; ordered=[p for p in priority if p in gpt_models]; ordered.extend([m for m in gpt_models if m not in priority]); return ordered
        except AuthenticationError: raise ValueError("Invalid OpenAI API Key.")
        except APIConnectionError as e: raise ConnectionError(f"OpenAI Connection Error: {e}")
        except Exception as e: raise RuntimeError(f"OpenAI Model List Error: {e}")
    def generate_text(self, api_key: str, model: str, prompt: str, temperature: float = 0.3) -> str:
        if not openai_available: raise ImportError("OpenAI package not installed.")
        if not api_key or not model: raise ValueError("OpenAI API Key/Model required.")
        try:
            client=OpenAI(api_key=api_key); response=client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], temperature=temperature)
            if response.choices and response.choices[0].message: return response.choices[0].message.content.strip()
            else: raise RuntimeError("Invalid OpenAI response.")
        except AuthenticationError: raise ValueError("Invalid OpenAI API Key.")
        except APIConnectionError as e: raise ConnectionError(f"OpenAI Connection Error: {e}")
        except NotFoundError: raise ValueError(f"OpenAI Model '{model}' not found.")
        except Exception as e:
            if "does not exist" in str(e): raise ValueError(f"OpenAI Model '{model}' not found.")
            raise RuntimeError(f"OpenAI Generation Error: {e}")

class GeminiService(AIService):
    # ... (Implementasi GeminiService tetap sama dengan perbaikan try-except terakhir) ...
    def list_models(self, api_key: str) -> list[str]:
        if not gemini_available: raise ImportError("Gemini package not installed.")
        if not api_key: raise ValueError("Gemini API Key required.")
        try:
            genai.configure(api_key=api_key)
            models_list=[m.name.replace("models/", "") for m in genai.list_models() if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name]
            common=['gemini-1.5-pro-latest','gemini-1.5-flash-latest','gemini-pro']; [models_list.append(cm) for cm in common if not any(m.startswith(cm.split('-latest')[0]) for m in models_list)]
            priority=['gemini-1.5-pro-latest','gemini-1.5-flash-latest','gemini-pro']; ordered=[p for p in priority if p in models_list]; ordered.extend(sorted([m for m in models_list if m not in priority])); return list(dict.fromkeys(ordered))
        except (google_exceptions.PermissionDenied, google_exceptions.Unauthenticated): raise ValueError("Invalid Gemini API Key/permission.")
        except Exception as e:
            if "API key not valid" in str(e): raise ValueError("Invalid Gemini API Key.")
            raise RuntimeError(f"Gemini Model List Error: {e}")
    def generate_text(self, api_key: str, model: str, prompt: str, temperature: float = 0.3) -> str:
        if not gemini_available: raise ImportError("Gemini package not installed.")
        if not api_key or not model: raise ValueError("Gemini API Key/Model required.")
        try:
            genai.configure(api_key=api_key); model_id=f"models/{model}" if not model.startswith("models/") else model
            config=genai.types.GenerationConfig(temperature=temperature)
            safety=[{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT","HARM_CATEGORY_HATE_SPEECH","HARM_CATEGORY_SEXUALLY_EXPLICIT","HARM_CATEGORY_DANGEROUS_CONTENT"]]
            gemini=genai.GenerativeModel(model_id); response=gemini.generate_content(prompt, generation_config=config, safety_settings=safety)
            if response.prompt_feedback and response.prompt_feedback.block_reason: raise ValueError(f"Gemini prompt blocked: {response.prompt_feedback.block_reason.name}.")
            if hasattr(response, 'text'): return response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                try:
                    c = response.candidates[0];
                    if c.finish_reason.name != "STOP": raise RuntimeError(f"Gemini stopped: {c.finish_reason.name}.")
                    return c.content.parts[0].text.strip() if c.content and c.content.parts else ""
                except (AttributeError, IndexError, TypeError) as e: raise RuntimeError(f"Gemini candidate error: {e}.")
            else: raise RuntimeError("Unknown Gemini response.")
        except (google_exceptions.PermissionDenied, google_exceptions.Unauthenticated): raise ValueError("Invalid Gemini API Key/permission.")
        except ValueError as ve: raise ve
        except RuntimeError as rt: raise rt
        except ConnectionError as ce: raise ce
        except Exception as e:
            if "API key not valid" in str(e): raise ValueError("Invalid Gemini API Key.")
            if "404" in str(e) or "not found" in str(e).lower() or ("model" in str(e).lower() and "does not exist" in str(e).lower()): raise ValueError(f"Gemini Model '{model}' not found.")
            if "model" in str(e).lower() and "cannot be accessed" in str(e).lower(): raise ValueError(f"Gemini Model '{model}' cannot be accessed.")
            if "429" in str(e) or "resource exhausted" in str(e).lower(): raise ConnectionError("Gemini quota/rate limit.")
            if "SAFETY" in str(e).upper(): raise ValueError(f"Gemini blocked by safety: {e}")
            raise RuntimeError(f"Gemini text gen error: {e}")


# --- Main Application Class ---
class BlueprintGeneratorApp:
    def __init__(self, root_window):
        # ... (Inisialisasi variabel state lain sama) ...
        self.root = root_window
        self.root.title("Blueprint Generator 1.5")
        self.root.geometry("1250x850")
        self.modul_list = []
        self._next_module_id = 1
        self.treeview_iid_to_module_id = {}
        self.tests_enabled = tk.BooleanVar(value=False)
        self.generate_readme = tk.BooleanVar(value=True)
        self.generate_gitignore = tk.BooleanVar(value=True)
        self.git_init_enabled = tk.BooleanVar(value=False)
        # --- NEW: Deployment Target Variable ---
        self.deployment_target = tk.StringVar(value="Simple Web Server (Apache/Nginx/Local)") # Default
        # --------------------------------------
        self.selected_ai_provider = tk.StringVar(value="OpenAI")
        self.ai_services: dict[str, AIService] = {}
        if openai_available: self.ai_services["OpenAI"] = OpenAIService()
        if gemini_available: self.ai_services["Gemini"] = GeminiService()
        if not self.ai_services: messagebox.showerror("AI Error", "No AI libs. Exiting."); self.root.quit(); return
        self._create_widgets()
        self._update_language_list(); self._update_dynamic_combos(); self._update_api_key_entry()
        self._update_parent_module_combo()
        self.update_status("Ready")

    def _create_widgets(self):
        # ... (Layout PanedWindow, Left Pane, Right Pane Setup sama) ...
        main_paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=6); main_paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        left_pane = ttk.Frame(main_paned_window, width=750); main_paned_window.add(left_pane, stretch="always")
        right_pane = ttk.Frame(main_paned_window, width=450); main_paned_window.add(right_pane, stretch="never")
        self.notebook = ttk.Notebook(left_pane); self.notebook.pack(fill=tk.BOTH, expand=True)
        right_canvas = tk.Canvas(right_pane, borderwidth=0, highlightthickness=0); right_scrollbar = ttk.Scrollbar(right_pane, orient="vertical", command=right_canvas.yview)
        self.right_scrollable_frame = ttk.Frame(right_canvas); self.right_scrollable_frame.bind("<Configure>", lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all"), width=e.width))
        # Bind mouse wheel to canvas for scrolling the right pane
        right_canvas.bind("<Enter>", lambda e: right_canvas.bind_all("<MouseWheel>", lambda e: right_canvas.yview_scroll(-1 * int(e.delta / 60), "units")))
        right_canvas.bind("<Leave>", lambda e: right_canvas.unbind_all("<MouseWheel>"))
        right_canvas_window = right_canvas.create_window((0, 0), window=self.right_scrollable_frame, anchor="nw"); right_canvas.configure(yscrollcommand=right_scrollbar.set)
        right_canvas.pack(side="left", fill="both", expand=True); right_scrollbar.pack(side="right", fill="y")
        def frame_width(event): right_canvas.itemconfig(right_canvas_window, width=event.width)
        right_canvas.bind('<Configure>', frame_width)

        # --- Tab 1: Project Setup ---
        tab_setup = ttk.Frame(self.notebook, padding=10); self.notebook.add(tab_setup, text="1. Project Setup")
        setup_canvas = tk.Canvas(tab_setup, borderwidth=0, highlightthickness=0); setup_scrollbar = ttk.Scrollbar(tab_setup, orient="vertical", command=setup_canvas.yview)
        setup_scrollable_frame = ttk.Frame(setup_canvas); setup_scrollable_frame.bind("<Configure>", lambda e: setup_canvas.configure(scrollregion=setup_canvas.bbox("all"), width=e.width))
        # Bind mouse wheel to canvas for scrolling the setup tab
        setup_canvas.bind("<Enter>", lambda e: setup_canvas.bind_all("<MouseWheel>", lambda e: setup_canvas.yview_scroll(-1 * int(e.delta / 60), "units")))
        setup_canvas.bind("<Leave>", lambda e: setup_canvas.unbind_all("<MouseWheel>"))
        setup_canvas_window = setup_canvas.create_window((0, 0), window=setup_scrollable_frame, anchor="nw"); setup_canvas.configure(yscrollcommand=setup_scrollbar.set)
        setup_canvas.pack(side="left", fill="both", expand=True); setup_scrollbar.pack(side="right", fill="y")
        def setup_frame_width(event): setup_canvas.itemconfig(setup_canvas_window, width=event.width)
        setup_canvas.bind('<Configure>', setup_frame_width)
        # Widgets for Project Setup Tab (Parent: setup_scrollable_frame)
        core_info_frame = ttk.LabelFrame(setup_scrollable_frame, text="Core Information", padding=10); core_info_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5); core_info_frame.columnconfigure(1, weight=1)
        ttk.Label(core_info_frame, text="Project Name:").grid(row=0, column=0, sticky="w", padx=5, pady=3); self.entry_name = ttk.Entry(core_info_frame, width=60); self.entry_name.grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        ttk.Label(core_info_frame, text="Purpose/Goal:").grid(row=1, column=0, sticky="nw", padx=5, pady=3); self.text_purpose = tk.Text(core_info_frame, height=3, width=60, wrap=tk.WORD); self.text_purpose.grid(row=1, column=1, sticky="ew", padx=5, pady=3)
        ttk.Label(core_info_frame, text="Target Users:").grid(row=2, column=0, sticky="nw", padx=5, pady=3); self.text_target_users = tk.Text(core_info_frame, height=3, width=60, wrap=tk.WORD); self.text_target_users.grid(row=2, column=1, sticky="ew", padx=5, pady=3)
        ttk.Label(core_info_frame, text="Main Workflow:").grid(row=3, column=0, sticky="nw", padx=5, pady=3); self.text_main_workflow = tk.Text(core_info_frame, height=4, width=60, wrap=tk.WORD); self.text_main_workflow.grid(row=3, column=1, sticky="ew", padx=5, pady=3)
        ttk.Label(core_info_frame, text="Core Entities:").grid(row=4, column=0, sticky="nw", padx=5, pady=3); self.text_data_entities = tk.Text(core_info_frame, height=3, width=60, wrap=tk.WORD); self.text_data_entities.grid(row=4, column=1, sticky="ew", padx=5, pady=3); ttk.Label(core_info_frame, text="(e.g., User, Product)").grid(row=5, column=1, sticky="w", padx=5, pady=0)
        features_frame = ttk.LabelFrame(setup_scrollable_frame, text="Features", padding=10); features_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5); features_frame.columnconfigure(1, weight=1)
        ttk.Label(features_frame, text="Key Features:").grid(row=0, column=0, sticky="nw", padx=5, pady=3); self.text_features = tk.Text(features_frame, height=5, width=60, wrap=tk.WORD); self.text_features.grid(row=0, column=1, sticky="ew", padx=5, pady=3); ttk.Label(features_frame, text="Define Modules in Tab 2").grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=3)
        tech_stack_frame = ttk.LabelFrame(setup_scrollable_frame, text="Technical Stack", padding=10); tech_stack_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5); tech_stack_frame.columnconfigure(1, weight=1); tech_stack_frame.columnconfigure(3, weight=1)
        ttk.Label(tech_stack_frame, text="App Type:").grid(row=0, column=0, sticky="w", padx=5, pady=3); app_types = sorted(list(LANGUAGE_MAP.keys() - {"__fallback__"})); self.combo_type = ttk.Combobox(tech_stack_frame, values=app_types, width=30, state="readonly"); self.combo_type.grid(row=0, column=1, sticky="ew", padx=5, pady=3); default_type = "Web" if "Web" in app_types else (app_types[0] if app_types else ""); self.combo_type.set(default_type); self.combo_type.bind("<<ComboboxSelected>>", self._on_app_type_or_language_change)
        ttk.Label(tech_stack_frame, text="Languages:").grid(row=0, column=2, sticky="nw", padx=(15, 5), pady=3); lang_list_frame = ttk.Frame(tech_stack_frame);
        # --- ADJUSTED ROWSPAN for lang_list_frame ---
        # Calculate number of rows used by widgets in column 0/1 before Key Libs
        # Rows 0, 1, 2, 3, 4, 7 -> 6 rows before Key Libs starts at row 8
        lang_list_frame.grid(row=0, column=3, rowspan=8, sticky="nsew", padx=5, pady=3) # Rowspan is 8
        lang_list_frame.rowconfigure(0, weight=1); lang_list_frame.columnconfigure(0, weight=1); self.listbox_language = tk.Listbox(lang_list_frame, height=8, selectmode=tk.EXTENDED, exportselection=False); lang_scrollbar = ttk.Scrollbar(lang_list_frame, orient="vertical", command=self.listbox_language.yview); self.listbox_language.config(yscrollcommand=lang_scrollbar.set); self.listbox_language.grid(row=0, column=0, sticky="nsew"); lang_scrollbar.grid(row=0, column=1, sticky="ns"); self.listbox_language.bind("<<ListboxSelect>>", self._on_app_type_or_language_change)
        ttk.Label(tech_stack_frame, text="Web Fw:").grid(row=1, column=0, sticky="w", padx=5, pady=3); self.combo_web_framework = ttk.Combobox(tech_stack_frame, values=["Select Lang"], width=30, state="readonly"); self.combo_web_framework.grid(row=1, column=1, sticky="ew", padx=5, pady=3); self.combo_web_framework.set("None")
        ttk.Label(tech_stack_frame, text="UI Lib/Fw:").grid(row=2, column=0, sticky="w", padx=5, pady=3); self.combo_ui_lib = ttk.Combobox(tech_stack_frame, values=["Select Lang"], width=30, state="readonly"); self.combo_ui_lib.grid(row=2, column=1, sticky="ew", padx=5, pady=3); self.combo_ui_lib.set("None")
        ttk.Label(tech_stack_frame, text="State Mgmt:").grid(row=3, column=0, sticky="w", padx=5, pady=3); self.combo_state_mgmt = ttk.Combobox(tech_stack_frame, values=["Select UI Lib"], width=30, state="readonly"); self.combo_state_mgmt.grid(row=3, column=1, sticky="ew", padx=5, pady=3); self.combo_state_mgmt.set("None")
        ttk.Label(tech_stack_frame, text="Database:").grid(row=4, column=0, sticky="w", padx=5, pady=3); self.combo_database = ttk.Combobox(tech_stack_frame, values=DATABASES, width=30, state="readonly"); self.combo_database.grid(row=4, column=1, sticky="ew", padx=5, pady=3); self.combo_database.set("None")
        # --- NEW: Deployment Target ---
        ttk.Label(tech_stack_frame, text="Deployment Target:").grid(row=7, column=0, sticky="w", padx=5, pady=3) # Added at row 7
        deployment_options = ["Simple Web Server (Apache/Nginx/Local)", "Container (Docker)", "Cloud Platform (AWS/Azure/GCP/Vercel)", "Not Decided / Other"]
        self.combo_deployment = ttk.Combobox(tech_stack_frame, textvariable=self.deployment_target, values=deployment_options, width=30, state="readonly")
        self.combo_deployment.grid(row=7, column=1, sticky="ew", padx=5, pady=3) # Added at row 7
        # --- Shift Key Libs down ---
        ttk.Label(tech_stack_frame, text="Key Libs:").grid(row=8, column=0, sticky="nw", padx=5, pady=3) # Shifted to row 8
        self.text_key_libs = tk.Text(tech_stack_frame, height=3, width=60, wrap=tk.WORD); self.text_key_libs.grid(row=8, column=1, columnspan=3, sticky="ew", padx=5, pady=3) # Shifted to row 8
        ttk.Label(tech_stack_frame, text="(Comma-separated)").grid(row=9, column=1, columnspan=3, sticky="w", padx=5, pady=0) # Shifted to row 9

        # --- Widgets for Right Pane (Parent: self.right_scrollable_frame) ---
        design_frame = ttk.LabelFrame(self.right_scrollable_frame, text="Design & Constraints", padding=10); design_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5); design_frame.columnconfigure(1, weight=1)
        ttk.Label(design_frame, text="Principles:").grid(row=0, column=0, sticky="nw", padx=5, pady=3); self.text_design_principles = tk.Text(design_frame, height=4, width=35, wrap=tk.WORD); self.text_design_principles.grid(row=0, column=1, sticky="ew", padx=5, pady=3); ttk.Label(design_frame, text="(e.g., SOLID)").grid(row=1, column=1, sticky="w", padx=5, pady=0)
        ttk.Label(design_frame, text="Key NFRs:").grid(row=2, column=0, sticky="nw", padx=5, pady=3); self.text_nfrs = tk.Text(design_frame, height=4, width=35, wrap=tk.WORD); self.text_nfrs.grid(row=2, column=1, sticky="ew", padx=5, pady=3); ttk.Label(design_frame, text="(e.g., <500ms)").grid(row=3, column=1, sticky="w", padx=5, pady=0)
        ttk.Label(design_frame, text="Add. Notes:").grid(row=4, column=0, sticky="nw", padx=5, pady=3); self.text_notes = tk.Text(design_frame, height=5, width=35, wrap=tk.WORD); self.text_notes.grid(row=4, column=1, sticky="ew", padx=5, pady=3)
        ai_frame = ttk.LabelFrame(self.right_scrollable_frame, text="AI Configuration", padding=10); ai_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5); ai_frame.columnconfigure(1, weight=1)
        ttk.Label(ai_frame, text="Provider:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3); self.combo_provider = ttk.Combobox(ai_frame, textvariable=self.selected_ai_provider, values=list(self.ai_services.keys()), width=10, state="readonly"); self.combo_provider.grid(row=0, column=1, sticky=tk.W, padx=5, pady=3); self.combo_provider.bind("<<ComboboxSelected>>", self._update_api_key_entry)
        self.btn_fetch_models = ttk.Button(ai_frame, text="Fetch Models", command=self.fetch_models, width=12); self.btn_fetch_models.grid(row=0, column=2, sticky="e", padx=5, pady=3)
        ttk.Label(ai_frame, text="Model:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3); self.combo_model = ttk.Combobox(ai_frame, values=[], width=30, state="readonly"); self.combo_model.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=3)
        self.api_key_frame = ttk.Frame(ai_frame); self.api_key_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(5,0)); self.api_key_frame.columnconfigure(0, weight=1)
        self.openai_api_key_frame = ttk.Frame(self.api_key_frame); label_oai=ttk.Label(self.openai_api_key_frame, text="OpenAI Key:"); self.entry_openai_apikey = ttk.Entry(self.openai_api_key_frame, width=25, show="*"); label_oai.pack(side=tk.LEFT, padx=(5,2)); self.entry_openai_apikey.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.gemini_api_key_frame = ttk.Frame(self.api_key_frame); label_gem=ttk.Label(self.gemini_api_key_frame, text="Gemini Key:"); self.entry_gemini_apikey = ttk.Entry(self.gemini_api_key_frame, width=25, show="*"); label_gem.pack(side=tk.LEFT, padx=(5,2)); self.entry_gemini_apikey.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        gen_options_frame = ttk.LabelFrame(self.right_scrollable_frame, text="Generation Options", padding=10); gen_options_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.checkbox_tests = ttk.Checkbutton(gen_options_frame, text="Include tests", variable=self.tests_enabled); self.checkbox_tests.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.checkbox_readme = ttk.Checkbutton(gen_options_frame, text="Gen README.md", variable=self.generate_readme); self.checkbox_readme.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.checkbox_gitignore = ttk.Checkbutton(gen_options_frame, text="Gen .gitignore", variable=self.generate_gitignore); self.checkbox_gitignore.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.checkbox_git_init = ttk.Checkbutton(gen_options_frame, text="Init Git Repo", variable=self.git_init_enabled); self.checkbox_git_init.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # --- Tab 2: Modules (Treeview) ---
        # ... (Kode Tab 2 sama) ...
        tab_modul = ttk.Frame(self.notebook, padding=10); self.notebook.add(tab_modul, text="2. Modules")
        modul_entry_frame = ttk.LabelFrame(tab_modul, text="Add/Edit Module", padding=10); modul_entry_frame.pack(fill="x", pady=5, anchor='n'); modul_entry_frame.columnconfigure(1, weight=1)
        ttk.Label(modul_entry_frame, text="Parent Module:").grid(row=0, column=0, sticky="w", padx=5, pady=3); self.combo_parent_module = ttk.Combobox(modul_entry_frame, values=["(Top Level)"], width=38, state="readonly"); self.combo_parent_module.grid(row=0, column=1, sticky="ew", padx=5, pady=3); self.combo_parent_module.set("(Top Level)")
        ttk.Label(modul_entry_frame, text="Module Name:").grid(row=1, column=0, sticky="w", padx=5, pady=3); self.entry_modul_nama = ttk.Entry(modul_entry_frame, width=40); self.entry_modul_nama.grid(row=1, column=1, sticky="ew", padx=5, pady=3)
        ttk.Label(modul_entry_frame, text="Description:").grid(row=2, column=0, sticky="nw", padx=5, pady=3); self.entry_modul_deskripsi = tk.Text(modul_entry_frame, height=4, width=50, wrap=tk.WORD); self.entry_modul_deskripsi.grid(row=2, column=1, sticky="ew", padx=5, pady=3)
        ttk.Button(modul_entry_frame, text="+ Add Module", command=self.tambah_modul).grid(row=3, column=1, sticky="e", pady=5, padx=5)
        modul_list_frame = ttk.LabelFrame(tab_modul, text="Module Hierarchy", padding=10); modul_list_frame.pack(fill="both", expand=True, pady=5); modul_list_frame.rowconfigure(0, weight=1); modul_list_frame.columnconfigure(0, weight=1)
        self.module_tree = ttk.Treeview(modul_list_frame, columns=("Description",), selectmode="browse")
        self.module_tree.heading("#0", text="Module Name"); self.module_tree.heading("Description", text="Description"); self.module_tree.column("#0", width=250, stretch=tk.YES); self.module_tree.column("Description", width=400, stretch=tk.YES)
        tree_scrollbar_y = ttk.Scrollbar(modul_list_frame, orient="vertical", command=self.module_tree.yview); tree_scrollbar_x = ttk.Scrollbar(modul_list_frame, orient="horizontal", command=self.module_tree.xview)
        self.module_tree.configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set); self.module_tree.grid(row=0, column=0, sticky="nsew"); tree_scrollbar_y.grid(row=0, column=1, sticky="ns"); tree_scrollbar_x.grid(row=1, column=0, sticky="ew")
        tree_button_frame = ttk.Frame(tab_modul); tree_button_frame.pack(fill="x", pady=5)
        btn_delete_modul = ttk.Button(tree_button_frame, text="- Remove Selected (and children)", command=self.hapus_modul); btn_delete_modul.pack(side=tk.RIGHT, padx=10)

        # --- Tab 3: Preview & Generate ---
        # ... (Kode Tab 3 sama) ...
        tab_preview = ttk.Frame(self.notebook, padding=10); self.notebook.add(tab_preview, text="3. Preview & Generate")
        action_frame = ttk.Frame(tab_preview); action_frame.pack(pady=(0, 10), fill="x")
        self.btn_generate = ttk.Button(action_frame, text="Generate Files", command=self.generate_blueprint, style="Accent.TButton"); self.btn_generate.pack(side=tk.LEFT, padx=5)
        self.btn_save = ttk.Button(action_frame, text="Save Config", command=self.simpan_project); self.btn_save.pack(side=tk.LEFT, padx=5)
        self.btn_open = ttk.Button(action_frame, text="Load Config", command=self.buka_project); self.btn_open.pack(side=tk.LEFT, padx=5)
        self.btn_clear = ttk.Button(action_frame, text="Clear Form", command=self.clear_form); self.btn_clear.pack(side=tk.RIGHT, padx=5)
        preview_frame = ttk.LabelFrame(tab_preview, text="Preview", padding=10); preview_frame.pack(fill="both", expand=True)
        self.preview_output = scrolledtext.ScrolledText(preview_frame, height=30, width=100, wrap=tk.WORD, state=tk.DISABLED); self.preview_output.pack(fill="both", expand=True)

        # --- Status Bar ---
        self.status_label = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W); self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        # --- Styling ---
        try: style = ttk.Style(self.root); available = style.theme_names(); [style.theme_use(t) for t in ['clam', 'alt', 'default'] if t in available]; style.configure("Accent.TButton", foreground="white", background="#0078D4", padding=5); style.map("Accent.TButton", background=[('active', '#005a9e')])
        except Exception as e: print(f"Info: Style err: {e}")


    # --- METHODS ---
    # ... (Implementasi semua metode lainnya dari versi terakhir) ...
    def _get_module_by_id(self, module_id: int) -> dict | None: return next((mod for mod in self.modul_list if mod['id'] == module_id), None)
    def _get_module_children_ids(self, parent_id: int | None) -> list[int]: return [m['id'] for m in self.modul_list if m['parent_id'] == parent_id]
    def _get_all_descendant_ids(self, module_id: int) -> list[int]: desc = []; children = self._get_module_children_ids(module_id); [ (desc.append(c), desc.extend(self._get_all_descendant_ids(c))) for c in children ]; return desc
    def _get_module_display_name(self, module_id: int, include_parents=True) -> str: mod = self._get_module_by_id(module_id); return "Unknown" if not mod else mod['nama'] if not include_parents or mod['parent_id'] is None else f"{self._get_module_display_name(mod['parent_id'], True)} :: {mod['nama']}"
    def _update_parent_module_combo(self):
        try: current = self.combo_parent_module.get()
        except tk.TclError: current = "(Top Level)"
        parents = ["(Top Level)"]; processed = set()
        def get_name_safe(mod_id): mod = self._get_module_by_id(mod_id); return mod['nama'] if mod else ""
        def add_rec(mod_id, indent=0):
            mod = self._get_module_by_id(mod_id)
            if not mod or mod_id in processed: return
            processed.add(mod_id); parents.append(self._get_module_display_name(mod_id))
            children = self._get_module_children_ids(mod_id)
            try: sorted_children = sorted(children, key=get_name_safe)
            except Exception as e: print(f"Warn: Sort fail children of {mod_id}: {e}"); sorted_children = children
            for child_id in sorted_children: add_rec(child_id, indent + 1)
        top_ids = self._get_module_children_ids(None)
        try: sorted_top = sorted(top_ids, key=get_name_safe)
        except Exception as e: print(f"Warn: Sort fail top level: {e}"); sorted_top = top_ids
        for top_id in sorted_top: add_rec(top_id)
        try: self.combo_parent_module['values'] = parents; self.combo_parent_module.set(current if current in parents else "(Top Level)")
        except tk.TclError as e: print(f"Warn: TclError set parent combo: {e}")
    def _populate_module_treeview(self):
        [self.module_tree.delete(i) for i in self.module_tree.get_children()]; self.treeview_iid_to_module_id.clear()
        mods_by_id = {mod['id']: mod for mod in self.modul_list}; created = {}
        def add_rec(parent_id=None):
            tree_parent = created.get(parent_id, '')
            if parent_id and not self.module_tree.exists(tree_parent) and str(parent_id) != '': print(f"ERR: Tree parent '{tree_parent}'({parent_id}) not found!"); return
            children = sorted(self._get_module_children_ids(parent_id), key=lambda x: mods_by_id.get(x, {}).get('nama', ''))
            for child_id in children:
                mod = mods_by_id.get(child_id); child_iid = str(child_id) # Use module id as iid
                if mod and child_iid not in created:
                    try: new_iid=self.module_tree.insert(tree_parent, tk.END, iid=child_iid, text=mod['nama'], values=(mod['deskripsi'],)); created[child_id]=new_iid; self.treeview_iid_to_module_id[new_iid]=child_id; add_rec(child_id)
                    except tk.TclError as e: print(f"ERR tree insert {child_id}: {e}")
        add_rec(None)
    def tambah_modul(self):
        nama=self.entry_modul_nama.get().strip(); desc=self.entry_modul_deskripsi.get("1.0", tk.END).strip(); parent_disp=self.combo_parent_module.get()
        if not nama or not desc: messagebox.showwarning("Input Missing", "Enter name & desc."); return
        p_id = None;
        if parent_disp != "(Top Level)":
            found = False;
            for mid in [m['id'] for m in self.modul_list]: # Find parent ID from display name
                if self._get_module_display_name(mid) == parent_disp: p_id = mid; found = True; break
            if not found: messagebox.showerror("Error", f"Parent '{parent_disp}' not found."); return
        if any(m['nama'].lower() == nama.lower() for m in self.modul_list if m['parent_id'] == p_id): p_name = parent_disp if p_id else "Top"; messagebox.showwarning("Duplicate", f"'{nama}' exists under '{p_name}'."); return
        new_id = self._next_module_id; self._next_module_id += 1; new_mod = {'id': new_id, 'parent_id': p_id, 'nama': nama, 'deskripsi': desc}; self.modul_list.append(new_mod)
        p_tree_iid = next((tv_iid for tv_iid, mod_id in self.treeview_iid_to_module_id.items() if mod_id == p_id), '') # Find parent's treeview iid
        try: new_tree_iid = self.module_tree.insert(p_tree_iid, tk.END, iid=str(new_id), text=nama, values=(desc,)); self.treeview_iid_to_module_id[new_tree_iid] = new_id
        except tk.TclError as e: print(f"ERR tree insert: {e}"); self.modul_list.pop(); messagebox.showerror("Tree Error", "Failed add."); return
        self.entry_modul_nama.delete(0, tk.END); self.entry_modul_deskripsi.delete("1.0", tk.END); self._update_parent_module_combo(); self.update_status(f"Module '{nama}' added.");
        if p_tree_iid: self.module_tree.item(p_tree_iid, open=True)
    def hapus_modul(self):
        """Removes the selected module and all its descendants."""
        selected_iids = self.module_tree.selection()
        if not selected_iids:
            messagebox.showwarning("No Selection", "Select a module to remove."); return

        selected_iid = selected_iids[0] # Handle single selection
        module_id_to_remove = self.treeview_iid_to_module_id.get(selected_iid)

        if module_id_to_remove is None:
             # This might happen if mapping is somehow inconsistent
             messagebox.showerror("Internal Error", "Could not find internal ID for the selected tree item. Please reload the project.")
             print(f"ERROR: Cannot find module ID for Treeview iid '{selected_iid}' in mapping.")
             return

        # --- FIX: Get module data AFTER checking module_id_to_remove ---
        module_to_remove = self._get_module_by_id(module_id_to_remove)
        # --- FIX: Check if module_to_remove is None BEFORE using it ---
        if not module_to_remove:
             messagebox.showerror("Data Error", f"Could not find data for module ID {module_id_to_remove}. The project data might be inconsistent.")
             print(f"ERROR: Module data not found for existing ID {module_id_to_remove}.")
             # Optionally, try to remove the inconsistent item from tree anyway?
             # if self.module_tree.exists(selected_iid):
             #     self.module_tree.delete(selected_iid)
             # if selected_iid in self.treeview_iid_to_module_id:
             #     del self.treeview_iid_to_module_id[selected_iid]
             return

        # Now it's safe to use module_to_remove['nama']
        confirm_msg = f"Remove '{module_to_remove['nama']}'?"
        descendant_ids = self._get_all_descendant_ids(module_id_to_remove)
        if descendant_ids:
            confirm_msg += f"\nThis will also remove {len(descendant_ids)} sub-module(s)."

        if not messagebox.askyesno("Confirm Removal", confirm_msg):
            return

        # --- Perform Deletion ---
        ids_to_delete = [module_id_to_remove] + descendant_ids

        # 1. Remove from Treeview (using module IDs to find correct iids)
        # FIX: Iterate through ids_to_delete and find corresponding iid
        iids_to_delete_in_tree = []
        temp_mapping_copy = self.treeview_iid_to_module_id.copy() # Avoid modifying dict while iterating
        for iid, mod_id in temp_mapping_copy.items():
            if mod_id in ids_to_delete:
                iids_to_delete_in_tree.append(iid)

        for item_iid in iids_to_delete_in_tree:
             if self.module_tree.exists(item_iid):
                  try:
                       self.module_tree.delete(item_iid)
                  except tk.TclError as e:
                      print(f"Warning: TclError deleting item {item_iid} from tree: {e}")
             # Remove from mapping after deletion from tree
             if item_iid in self.treeview_iid_to_module_id:
                  del self.treeview_iid_to_module_id[item_iid]


        # 2. Remove from self.modul_list
        self.modul_list = [mod for mod in self.modul_list if mod['id'] not in ids_to_delete]

        # 3. Update parent combo
        self._update_parent_module_combo()
        self.update_status(f"Module '{module_to_remove['nama']}' and descendants removed.")
    def _format_modules_hierarchical(self, parent_id=None, indent=0) -> str: md = ""; children = sorted(self._get_module_children_ids(parent_id), key=lambda x: self._get_module_by_id(x)['nama']); indent_s = "    " * indent; [(mod := self._get_module_by_id(mod_id)) and (md := md + f"{indent_s}- **{mod['nama']}:** {mod['deskripsi']}\n" + self._format_modules_hierarchical(mod_id, indent + 1)) for mod_id in children]; return md
    def _on_app_type_or_language_change(self, event=None): self._update_language_list(); self._update_dynamic_combos()
    def _update_language_list(self):
        app_type = self.combo_type.get(); langs = LANGUAGE_MAP.get(app_type, LANGUAGE_MAP["__fallback__"]); old_sel = {self.listbox_language.get(i) for i in self.listbox_language.curselection()}
        self.listbox_language.config(state=tk.NORMAL); self.listbox_language.delete(0, tk.END)
        if langs: [self.listbox_language.insert(tk.END, l) for l in langs]; [self.listbox_language.selection_set(i) for i, l in enumerate(langs) if l in old_sel]
        else: self.listbox_language.insert(tk.END, "N/A"); self.listbox_language.config(state=tk.DISABLED)
    def _update_dynamic_combos(self):
        langs = [self.listbox_language.get(i).lower() for i in self.listbox_language.curselection()]
        def update_combo(combo, source_map, default_val="None"):
            opts = {default_val}; [opts.update(source_map.get(l, [])) for l in langs]; valid = sorted(list(opts)); cur = combo.get()
            combo['values'] = valid; combo.set(cur if cur in valid else (default_val if default_val in valid else (valid[0] if valid else "")))
            combo.config(state="readonly" if valid else tk.DISABLED)
        update_combo(self.combo_web_framework, WEB_FRAMEWORKS); update_combo(self.combo_ui_lib, UI_LIBS)
        state_opts={"None"}; cur_ui=self.combo_ui_lib.get().lower(); [state_opts.update(STATE_MANAGEMENT.get(l, [])) for l in langs if any(ul.lower()==cur_ui for ul in UI_LIBS.get(l, [])) or cur_ui=="none" or not langs]; valid_s=sorted(list(state_opts)); cur_s=self.combo_state_mgmt.get()
        self.combo_state_mgmt['values']=valid_s; self.combo_state_mgmt.set(cur_s if cur_s in valid_s else ("None" if "None" in valid_s else (valid_s[0] if valid_s else ""))); self.combo_state_mgmt.config(state="readonly" if valid_s else tk.DISABLED)
    def update_status(self, message): self.status_label.config(text=message); self.root.update_idletasks()
    def _update_api_key_entry(self, event=None):
        provider=self.selected_ai_provider.get(); self.combo_model.set(''); self.combo_model['values']=[]; self.combo_model.config(state=tk.DISABLED); key_o=self.entry_openai_apikey.get(); key_g=self.entry_gemini_apikey.get()
        self.openai_api_key_frame.pack_forget(); self.gemini_api_key_frame.pack_forget(); cur_key=""
        if provider=="OpenAI": self.openai_api_key_frame.pack(fill=tk.X, expand=True); self.entry_openai_apikey.delete(0, tk.END); self.entry_openai_apikey.insert(0, key_o); cur_key=key_o.strip()
        elif provider=="Gemini": self.gemini_api_key_frame.pack(fill=tk.X, expand=True); self.entry_gemini_apikey.delete(0, tk.END); self.entry_gemini_apikey.insert(0, key_g); cur_key=key_g.strip()
        if cur_key: self.fetch_models()
        else: self.combo_model.set("Enter API Key & Fetch")
    def _get_selected_ai_service(self): provider=self.selected_ai_provider.get(); service=self.ai_services.get(provider); key=""; key = self.entry_openai_apikey.get().strip() if provider=="OpenAI" else (self.entry_gemini_apikey.get().strip() if provider=="Gemini" else ""); return service, key
    def fetch_models(self):
        service, key = self._get_selected_ai_service(); provider=self.selected_ai_provider.get()
        if not service or not key: messagebox.showerror("Error", f"Select Provider & Enter Key for {provider}."); return
        self.update_status(f"Fetching {provider} models..."); self._disable_ui_during_action(fetching=True)
        def load():
            models, err = [], None
            try: models = service.list_models(key)
            except Exception as e: err=f"Error: {e}"
            finally: self.root.after(0, lambda: (self._enable_ui_after_action(fetching=True), (messagebox.showerror(f"Fetch Error", err), self.combo_model.set('Fail'), self.combo_model.config(state=tk.DISABLED), self.update_status(f"Fetch fail.")) if err else ((messagebox.showwarning(f"No Models", "No models found."), self.combo_model.set('None'), self.combo_model.config(state=tk.DISABLED), self.update_status("No models.")) if not models else (self._update_model_combo(models), self.update_status("Models OK."))) ) )
        threading.Thread(target=load, daemon=True).start()
    def _update_model_combo(self, models): self.combo_model["values"] = models; self.combo_model.set(models[0] if models else ""); self.combo_model.config(state="readonly" if models else tk.DISABLED)
    def clear_form(self):
        if not messagebox.askyesno("Confirm", "Clear all inputs?"): return
        for w in [self.entry_name, self.entry_openai_apikey, self.entry_gemini_apikey, self.entry_modul_nama]: w.delete(0, tk.END)
        for w in [self.text_purpose, self.text_target_users, self.text_main_workflow, self.text_data_entities, self.text_features, self.text_key_libs, self.text_design_principles, self.text_nfrs, self.text_notes, self.entry_modul_deskripsi]: w.delete("1.0", tk.END)
        self.preview_output.config(state=tk.NORMAL); self.preview_output.delete("1.0", tk.END); self.preview_output.config(state=tk.DISABLED)
        app_type = "Web" if "Web" in self.combo_type['values'] else (self.combo_type['values'][0] if self.combo_type['values'] else ""); self.combo_type.set(app_type)
        self._update_language_list(); self.listbox_language.selection_clear(0, tk.END); self._update_dynamic_combos(); self.combo_database.set("None"); self.selected_ai_provider.set("OpenAI"); self.combo_model.set(""); self.combo_model['values'] = []; self.modul_list.clear(); self._next_module_id = 1; self.treeview_iid_to_module_id.clear(); [self.module_tree.delete(i) for i in self.module_tree.get_children()]; self._update_parent_module_combo()
        self.tests_enabled.set(False); self.generate_readme.set(True); self.generate_gitignore.set(True); self.git_init_enabled.set(False); self.update_status("Form cleared.")
    def ambil_input_data(self): # FIX: Removed 'data: dict' parameter, it's not used here
        pd = {}; pd["name"]=self.entry_name.get().strip(); pd["purpose"]=self.text_purpose.get("1.0", tk.END).strip(); pd["target_users"]=self.text_target_users.get("1.0", tk.END).strip(); pd["main_workflow"]=self.text_main_workflow.get("1.0", tk.END).strip(); pd["data_entities"]=self.text_data_entities.get("1.0", tk.END).strip(); pd["features_manual"]=self.text_features.get("1.0", tk.END).strip();
        pd["modules"]=self.modul_list; # Save the hierarchical list
        pd["project_type"]=self.combo_type.get(); lang_idx=self.listbox_language.curselection(); pd["language_list"]=[self.listbox_language.get(i) for i in lang_idx]; pd["language"]=", ".join(pd["language_list"]); pd["web_framework"]=self.combo_web_framework.get(); pd["ui_lib"]=self.combo_ui_lib.get(); pd["state_mgmt"]=self.combo_state_mgmt.get(); pd["database"]=self.combo_database.get(); pd["key_libs"]=self.text_key_libs.get("1.0", tk.END).strip(); pd["design_principles"]=self.text_design_principles.get("1.0", tk.END).strip(); pd["nfrs"]=self.text_nfrs.get("1.0", tk.END).strip(); pd["notes"]=self.text_notes.get("1.0", tk.END).strip(); pd["tests_enabled"]=self.tests_enabled.get(); pd["gen_readme"]=self.generate_readme.get(); pd["gen_gitignore"]=self.generate_gitignore.get(); pd["git_init"]=self.git_init_enabled.get()
        pd["deployment_target"] = self.deployment_target.get() # Ensure this line exists
        provider=self.selected_ai_provider.get(); _, key_val = self._get_selected_ai_service()
        if not pd["features_manual"] and not pd["modules"]: messagebox.showerror("Missing", "Need Features or Modules."); return None
        req={"Name":pd["name"], "Purpose":pd["purpose"], "Type":pd["project_type"], "Lang":pd["language"], "Provider":provider, f"API Key":key_val}; miss=[n for n,v in req.items() if not v]
        if miss: messagebox.showerror("Missing", f"Required:\n- {', '.join(miss)}"); return None
        for k in ["web_framework", "ui_lib", "state_mgmt", "database"]: pd[k] = "" if pd[k].lower() == "none" else pd[k]
        pd["_next_module_id"] = self._next_module_id; return pd # Ensure _next_module_id is saved
    def isi_form_data(self, data: dict):
        self.clear_form(); self.entry_name.insert(0, data.get("name", "")); self.text_purpose.insert("1.0", data.get("purpose", "")); self.text_target_users.insert("1.0", data.get("target_users", "")); self.text_main_workflow.insert("1.0", data.get("main_workflow", "")); self.text_data_entities.insert("1.0", data.get("data_entities", "")); self.text_features.insert("1.0", data.get("features_manual", ""));
        app_type=data.get("project_type", "Web"); default=next((v for v in [app_type, "Web"] if v in self.combo_type['values']), self.combo_type['values'][0] if self.combo_type['values'] else ""); self.combo_type.set(default)
        self.deployment_target.set(data.get("deployment_target", "Simple Web Server (Apache/Nginx/Local)")) # Ensure this matches the default value
        # --- FIX: Load Modules data FIRST and correctly ---
        self.modul_list = data.get("modules", []) # Load module data
        self._next_module_id = data.get("_next_module_id", 1) # Restore counter
        self._populate_module_treeview() # Build tree from loaded data
        self._update_parent_module_combo() # Update choices based on loaded tree
        # --- THEN Load rest ---
        self._update_language_list(); self.listbox_language.selection_clear(0, tk.END); langs=data.get("language_list", [])
        if langs: items=self.listbox_language.get(0,tk.END); nf=[l for l in langs if l not in items]; [(self.listbox_language.selection_set(items.index(l)), self.listbox_language.see(items.index(l))) for l in langs if l in items]; (messagebox.showwarning("Lang Mismatch", f"Incompatible langs: {', '.join(nf)}") if nf else None)
        self._update_dynamic_combos();
        for key, combo in [("web_framework",self.combo_web_framework), ("ui_lib",self.combo_ui_lib), ("state_mgmt",self.combo_state_mgmt), ("database",self.combo_database)]:
            val = data.get(key, "") # Default empty if key missing
            combo.set(val if val and val in combo['values'] else "None")
        self.text_key_libs.insert("1.0", data.get("key_libs", "")); self.text_design_principles.insert("1.0", data.get("design_principles", "")); self.text_nfrs.insert("1.0", data.get("nfrs", "")); self.text_notes.insert("1.0", data.get("notes", "")); self.entry_openai_apikey.insert(0, data.get("openai_api_key", "")); self.entry_gemini_apikey.insert(0, data.get("gemini_api_key", ""))
        provider=data.get("ai_provider", "OpenAI"); self.selected_ai_provider.set(provider if provider in self.ai_services else (list(self.ai_services.keys())[0] if self.ai_services else "")); self.root.after(500, lambda: self.combo_model.set(data.get("model", "")))
        self.tests_enabled.set(data.get("tests_enabled", False)); self.generate_readme.set(data.get("gen_readme", True)); self.generate_gitignore.set(data.get("gen_gitignore", True)); self.git_init_enabled.set(data.get("git_init", False)); self.update_status("Project loaded."); self.notebook.select(0)
    def simpan_project(self):
        # --- FIX: Use the clearer implementation ---
        data = self.ambil_input_data()
        if not data: return
        data['ai_provider'] = self.selected_ai_provider.get(); data['model'] = self.combo_model.get()
        data['openai_api_key'] = self.entry_openai_apikey.get(); data['gemini_api_key'] = self.entry_gemini_apikey.get()
        fp = filedialog.asksaveasfilename(defaultextension=".bpgproj",filetypes=[("BPG","*.bpgproj"),("JSON","*.json")],title="Save")
        if fp:
            try: open(fp,'w',encoding='utf-8').write(json.dumps(data,indent=2,ensure_ascii=False)); self.update_status(f"Saved: {os.path.basename(fp)}"); messagebox.showinfo("Save OK","Saved.")
            except Exception as e: messagebox.showerror("Save Error", f"Could not save:\n{e}"); self.update_status("Save error.")
        else: self.update_status("Save cancelled.")
    def buka_project(self):
        fp=filedialog.askopenfilename(filetypes=[("BPG","*.bpgproj"),("JSON","*.json")],title="Load");
        if fp:
            try: data = json.load(open(fp,'r',encoding='utf-8')); self.isi_form_data(data); self.update_status(f"Loaded: {os.path.basename(fp)}")
            except Exception as e: messagebox.showerror("Load Error", f"Failed to load:\n{e}"); self.update_status("Load error.") # Keep it simple
    def _prepare_prompts(self, d: dict):
        prompts = {}; mods = self._format_modules_hierarchical(); feats = d.get('features_manual',''); combined = feats + (f"\n\n## Modules:\n{mods}" if mods else "");
        test_ctx, test_md, test_rules = ("\n- Testing: Include `tests/`.", "**Testing:** Incl tests.", "MUST have tests.") if d['tests_enabled'] else ("\n- Testing: Disabled.", "**Testing:** Disabled.", "NO tests.")
        safety = """Before generating, modifying, deleting, or replacing any code, file, or folder, you MUST FIRST perform a full scan and complete understanding of the ENTIRE codebase. This includes reading all source files, project structure, file contents, configurations, and previously generated outputs. You must never operate on a partial view or act based on assumptions. You are required to detect what parts of the application are already implemented, working as expected, and approved by the user. Do NOT alter any working or finalized component unless explicitly requested. Any modification must be aligned with the existing working structure. When in doubt, stop and ask. Violating this rule will result in corruption of the entire application. This is a MANDATORY FINAL STEP CHECK before every action you perform in this development environment."""
        tech = f"- Langs: {d['language']}"+(f"\n- WebFw: {d['web_framework']}" if d.get('web_framework') else "")+(f"\n- UI Lib: {d['ui_lib']}" if d.get('ui_lib') else "")+(f"\n- State: {d['state_mgmt']}" if d.get('state_mgmt') else "")+(f"\n- DB: {d['database']}" if d.get('database') else "")+(f"\n- Libs: {d['key_libs']}" if d.get('key_libs') else "")
        # --- FIX: Include deployment_target in tech summary ---
        if d.get('deployment_target'): tech += f"\n- **Deployment:** {d['deployment_target']}"
        # --- FIX: Include deployment_target in system prompt ---
        sys_p = f"AI architect for '{d['name']}'. Goal:{d['purpose']}. Users:{d['target_users'] or 'N/A'}. WF:{d['main_workflow'] or 'N/A'}. Data:{d['data_entities'] or 'N/A'}. Type:{d['project_type']}. Stack:\n{tech}\nDeployment Target: {d.get('deployment_target', 'Not specified')}. Principles:{d['design_principles'] or 'N/A'}. NFRs:{d['nfrs'] or 'N/A'}. Notes:{d['notes'] or 'N/A'}{test_ctx}\nStrictly adhere to docs/rules. Clean, modular code."
        rules = [safety.strip(), test_rules, f"Langs:{d['language']}.", f"Type:'{d['project_type']}'.",]+([f"Use '{d[k]}'." for k in ['web_framework','ui_lib','state_mgmt','database'] if d.get(k)])+([f"Apply:{d['design_principles']}."] if d.get('design_principles') else [])
        prompts[".cursorrules"] = json.dumps({"system": sys_p, "rules": rules}, indent=2)
        # --- FIX: Include deployment target instruction in architecture.md prompt ---
        prompts["architecture.md"] = f"Create `arch.md` for '{d['name']}'. Context:\nGoal:{d['purpose']}\nType:{d['project_type']}\nStack:{tech}\nFeatures:{combined}\nUsers:{d['target_users'] or 'N/A'}\nWF:{d['main_workflow'] or 'N/A'}\nData:{d['data_entities'] or 'N/A'}\nPrinciples:{d['design_principles'] or 'N/A'}\nNFRs:{d['nfrs'] or 'N/A'}\nNotes:{d['notes'] or 'N/A'}.\n\nTASK:Detail: 1.Arch Style. 2.Components. 3.Folders(explain,configs). 4.Responsibilities(hierarchical). 5.Data Model. 6.API Contract. 7.Tech Justification. 8.{test_md} 9.Deployment Strategy(Conceptual): **Describe strategy suitable for '{d.get('deployment_target', 'Not specified')}'. Avoid complex setups if 'Simple Web Server' chosen.**"
        # --- FIX: Include deployment target instruction in project_plan.md prompt ---
        prompts["project_plan.md"] = f"Create `plan.md` for '{d['name']}'. Context:\nGoal:{d['purpose']}\nType:{d['project_type']}\nStack:{tech}\nFeatures:{combined}\nUsers:{d['target_users'] or 'N/A'}\nWF:{d['main_workflow'] or 'N/A'}\nData:{d['data_entities'] or 'N/A'}\nNFRs:{d['nfrs'] or 'N/A'}\nNotes:{d['notes'] or 'N/A'}.\n\nTASK:Gen plan: 1.Summary. 2.Scope. 3.Phases. 4.Checklist (`- [ ]`) per phase (realistic, scope, order, incl **setup relevant to '{d.get('deployment_target', 'Not specified')}'**, link tasks to modules, {test_md}). 5.Tech Summary."
        # --- FIX: Include deployment target instruction in README.md prompt ---
        if d['gen_readme']: prompts["README.md"] = f"Create `README.md` for '# {d['name']}'.\n\n## Desc\n{d['purpose']}. Users:{d['target_users'] or 'N/A'}.\n\n## Features\n(List based on:\n{combined})\n\n## Stack\n{tech}\n\n## Setup\n(Provide setup steps **appropriate for '{d.get('deployment_target', 'simple server')}'** and {d['language']}/{d.get('web_framework','')}...).\n\n## Running\n(Basic run command **appropriate for '{d.get('deployment_target', 'simple server')}'**...)."
        if d['gen_gitignore']: prompts[".gitignore"] = f"Gen `.gitignore` for: {d['language']},{d.get('web_framework','')},{d.get('ui_lib','')}. Incl OS,IDE,deps,env,logs. RAW ONLY."
        return prompts
    def generate_blueprint(self):
        """Handles the main blueprint generation process."""
        print("--- DEBUG: generate_blueprint called ---")

        config_data = self.ambil_input_data()
        if not config_data:
            print("DEBUG: generate_blueprint exited - ambil_input_data failed")
            return

        # --- FIX: Initialize svc and key BEFORE try block ---
        svc = None
        key = None
        # ----------------------------------------------------
        try:
            service_obj, api_key_str = self._get_selected_ai_service()
            # Assign only if the call was successful
            if service_obj is not None: # Check the service object specifically
                svc = service_obj
                key = api_key_str # Key might be empty string "" if service exists but key wasn't entered yet
            print(f"DEBUG: _get_selected_ai_service -> svc type: {type(svc)}, key present: {'Yes' if key else 'No'}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get AI service/key: {e}")
            print(f"ERROR: Exception in _get_selected_ai_service: {e}")
            return

        prov = self.selected_ai_provider.get()
        mdl = self.combo_model.get()
        print(f"DEBUG: Variables before check -> svc type: {type(svc)}, key present: {'Yes' if key else 'No'}, prov: {prov}, mdl: {mdl}")

        # --- Checks using the initialized svc and key ---
        if svc is None: # Explicit check for None
            messagebox.showerror("Configuration Error", f"AI Provider '{prov}' is not available or service failed.")
            print(f"DEBUG: generate_blueprint exited - svc is None for provider '{prov}'")
            return
        if not key: # Check if key is empty string or None
            messagebox.showerror("Configuration Error", f"API Key for {prov} is missing.")
            print(f"DEBUG: generate_blueprint exited - key is empty for provider '{prov}'")
            return
        invalid_model_states = ["Loading...", "Fetch Failed", "No models", "No models found", "Enter API Key and Fetch", "Enter API Key & Fetch", "Fail", "None", ""]
        if not mdl or mdl in invalid_model_states:
            messagebox.showerror("Configuration Error", f"Please select a valid AI Model for {prov} first (Current: '{mdl}'). Fetch models if needed.")
            print(f"DEBUG: generate_blueprint exited - AI model '{mdl}' invalid or not selected for provider '{prov}'")
            return

        print(f"DEBUG: Pre-generation checks passed. Provider: {prov}, Model: {mdl}")

        folder = filedialog.askdirectory(title="Select Folder to Save Blueprint Files")
        if not folder:
            print("DEBUG: generate_blueprint exited - Folder selection cancelled")
            self.update_status("Generation cancelled.")
            return

        # --- Disable UI, Prepare Prompts, Start Thread ---
        self.update_status("Starting blueprint generation...")
        self._disable_ui_during_action()
        self.preview_output.config(state=tk.NORMAL); self.preview_output.delete("1.0", tk.END); self.preview_output.config(state=tk.DISABLED)

        try:
            print("DEBUG: Preparing prompts...")
            prompts_to_generate = self._prepare_prompts(config_data)
            print(f"DEBUG: Prompts prepared for: {list(prompts_to_generate.keys())}")
        except Exception as e:
            messagebox.showerror("Prompt Preparation Error", f"Failed to prepare AI prompts: {e}")
            print(f"ERROR: Prompt preparation failed: {e}")
            self._enable_ui_after_action()
            return

        print("DEBUG: Starting generation thread...")
        # --- Threaded Generation (do_generate function) ---
        def do_generate():
            # ... (Isi do_generate tetap sama seperti versi sebelumnya, pastikan menggunakan 'svc', 'key', 'mdl' yang diteruskan dari scope luar) ...
            print("DEBUG: Thread do_generate started")
            results = {}
            errors = []
            files_to_generate = list(prompts_to_generate.keys())

            for index, filename in enumerate(files_to_generate):
                prompt_content = prompts_to_generate[filename]
                progress_msg = f"Generating {filename} ({index + 1}/{len(files_to_generate)})..."
                self.root.after(0, self.update_status, progress_msg)
                print(f"DEBUG: Thread - Generating {filename} using {mdl}")

                try:
                    if filename == ".cursorrules":
                        text = prompt_content
                        try: json.loads(text)
                        except json.JSONDecodeError as json_e: errors.append(f"Internal JSON Error .cursorrules: {json_e}"); text = '{"error": "Internal JSON failed"}'
                    else:
                        # Gunakan svc, key, mdl dari scope luar (generate_blueprint)
                        text = svc.generate_text(key, mdl, prompt_content, temperature=0.35)

                    results[filename] = text
                    try:
                        filepath = os.path.join(folder, filename)
                        with open(filepath, "w", encoding="utf-8") as f: f.write(text)
                        print(f"DEBUG: Thread - Wrote {filename}")
                    except IOError as write_e:
                        errors.append(f"Write fail {filename}: {write_e}")
                        if filename in results: del results[filename]

                except (ValueError, ConnectionError, ImportError, RuntimeError) as e:
                    errors.append(f"Gen fail {filename}: {e}")
                    print(f"ERROR: Thread - Gen fail {filename}: {e}")
                    if isinstance(e, (ValueError, ConnectionError, ImportError)) or "quota" in str(e).lower():
                         print("DEBUG: Thread - Critical error, stopping.")
                         break
                except Exception as e:
                    errors.append(f"Unexpected gen fail {filename}: {e}")
                    print(f"ERROR: Thread - Unexpected gen fail {filename}: {e}", flush=True)

            print("DEBUG: Thread - Loop done. Git init check.")
            git_ok, git_err = None, None
            if config_data['git_init'] and not any(isinstance(e,(ValueError,ConnectionError,ImportError)) for e in errors):
                self.root.after(0, self.update_status, "Git init...");
                try: subprocess.run(['git','--version'],check=True,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0); git_ok = False if os.path.isdir(os.path.join(folder,'.git')) else (subprocess.run(['git','init'],cwd=folder,check=True,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0), True)[1]
                except Exception as ge: git_err=f"Git fail:{ge}"; errors.append(git_err)
                print(f"DEBUG: Thread - Git init: ok={git_ok}, err={git_err}")

            print(f"DEBUG: Thread - Calling complete. Errs:{len(errors)}, Res:{len(results)}")
            self.root.after(0, self._generation_complete, results, errors, folder, git_ok)
            print("DEBUG: Thread finished")

        threading.Thread(target=do_generate, daemon=True).start()
    def _disable_ui_during_action(self, fetching=False): widgets=[self.btn_generate,self.btn_save,self.btn_open,self.btn_clear]; widgets.extend([self.btn_fetch_models, self.combo_provider, self.entry_openai_apikey, self.entry_gemini_apikey, self.combo_model] if fetching else [self.btn_fetch_models]); [w.config(state=tk.DISABLED) for w in widgets if w.winfo_exists()]
    def _enable_ui_after_action(self, fetching=False): widgets=[self.btn_generate,self.btn_save,self.btn_open,self.btn_clear,self.btn_fetch_models, self.combo_provider, self.entry_openai_apikey, self.entry_gemini_apikey]; [w.config(state="readonly" if isinstance(w,ttk.Combobox) and w!=self.combo_model else tk.NORMAL) for w in widgets if w.winfo_exists() and w!=self.combo_model]; self.combo_model.config(state="readonly" if self.combo_model.winfo_exists() and self.combo_model['values'] else tk.DISABLED)
    def _generation_complete(self, results, errors, folder, git_ok):
        print("DEBUG: _generation_complete called"); print(f"DEBUG: Errors: {errors}"); self._enable_ui_after_action(); preview=""; success=sorted(list(results.keys())); req=[".cursorrules","architecture.md","project_plan.md"]+["README.md"]*self.generate_readme.get()+[".gitignore"]*self.generate_gitignore.get(); failed=sorted([f for f in req if f not in success])
        if results: [preview := preview+f"=== {fname} ===\n{results[fname]}\n\n" for fname in success]; self.preview_output.config(state=tk.NORMAL); self.preview_output.delete("1.0",tk.END); self.preview_output.insert("1.0", preview); self.preview_output.config(state=tk.DISABLED)
        msg,mtype,stat="","info","OK."; err_sum='\n- '.join(errors) if errors else "None.";
        if not results and errors: msg,mtype,stat=f"Failed.\nFolder:{folder}\nErrors:\n- {err_sum}","error","Failed."
        elif errors: msg,mtype,stat=f"Done w/ errors.\nFolder:{folder}\n"+(f"OK:{','.join(success)}\n"if success else "")+(f"Fail:{','.join(failed)}\n"if failed else "")+f"Errors:\n- {err_sum}","warning","Done w/ errors."
        else: msg,mtype,stat=f"OK!\nFolder:{folder}\nFiles:{','.join(success)}"+("\nGit init OK."if git_ok else("\n(Already Git repo)."if git_ok is False else"")),"info","OK."
        if failed and results: msg+=f"\n\nFailed:{','.join(failed)}"; mtype="warning" if mtype=="info" else mtype
        title="Complete" if mtype=="info" else("Warnings" if mtype=="warning" else "Failed"); box=messagebox.showinfo if mtype=="info" else(messagebox.showwarning if mtype=="warning" else messagebox.showerror); box(title,msg); self.update_status(stat)
        if results and messagebox.askyesno("Open?",f"Open folder?\n{folder}"):
            try: os.startfile(folder) if os.name=='nt' else subprocess.run(['open' if os.uname().sysname=='Darwin' else 'xdg-open',folder],check=True)
            except Exception as e: messagebox.showerror("Error",f"Cannot open:{e}")
    def run(self): self.root.mainloop()

# --- Entry Point ---
if __name__ == "__main__":
    if not openai_available and not gemini_available: print("ERROR: Install 'openai' and/or 'google-generativeai'.")
    else:
        if not openai_available: print("Warn: 'openai' not found.")
        if not gemini_available: print("Warn: 'google-generativeai' not found.")
        main_root = tk.Tk(); app = BlueprintGeneratorApp(main_root)
        if app.ai_services: app.run()

#   --- END OF FILE code2.py ---