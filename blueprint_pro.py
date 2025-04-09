# Blueprint Generator (HKS)
# Left: Tabs (Setup, Modules, Preview/Gen) | Right: Options (Design, AI, Gen)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import threading
import importlib.util
import subprocess
from abc import ABC, abstractmethod
import uuid # Lebih baik untuk ID unik, tapi kita pakai integer dulu

# --- AI Library Imports & Checks ---
# ... (Sama seperti sebelumnya) ...
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
PROGRAMMING_LANGUAGES = sorted(list(set([
    "Python", "JavaScript", "TypeScript", "Java", "C#", "C++", "PHP",
    "Go", "Ruby", "Swift", "Kotlin", "Rust", "HTML", "CSS",
    "SQL", "Bash/Shell", "PowerShell", "Dart", "Scala", "Perl", "R",
    "Objective-C", "Lua", "Groovy", "MATLAB", "Assembly", "C", "GDScript",
    "Julia", "Zig"
])))
LANGUAGE_MAP = { "Web": sorted(["HTML", "CSS", "JavaScript", "TypeScript", "Python", "PHP", "Ruby", "Java", "C#", "Go", "Rust", "Kotlin", "Swift", "SQL", "Bash/Shell"]), "Desktop App (EXE/DMG)": sorted(["Python", "C#", "Java", "C++", "Swift", "Objective-C", "Rust", "JavaScript", "Dart", "C", "Kotlin"]), "Mobile App": sorted(["Kotlin", "Java", "Swift", "Objective-C", "Dart", "JavaScript", "TypeScript", "C#", "C++", "Rust"]), "API Only": sorted(["Python", "Go", "Java", "C#", "Ruby", "PHP", "JavaScript", "TypeScript", "Rust", "Kotlin", "Swift", "Scala", "SQL", "Bash/Shell"]), "CLI Tool": sorted(["Python", "Go", "Rust", "Bash/Shell", "PowerShell", "C++", "C", "C#", "Java", "Ruby", "Perl", "JavaScript", "Swift", "Zig"]), "Library/SDK": sorted(["Python", "Java", "C#", "C++", "C", "JavaScript", "TypeScript", "Go", "Rust", "Swift", "Kotlin", "PHP", "Ruby", "Objective-C", "Zig"]), "Data Science": sorted(["Python", "R", "SQL", "Scala", "Java", "MATLAB", "Julia"]), "Game": sorted(["C++", "C#", "Java", "Python", "Lua", "JavaScript", "Rust", "GDScript", "Swift"]), "IoT": sorted(["C", "C++", "Python", "Java", "JavaScript", "Lua", "Rust", "Bash/Shell", "Go"]), "__fallback__": sorted(PROGRAMMING_LANGUAGES)}
all_langs_in_map = set(lang for sublist in LANGUAGE_MAP.values() for lang in sublist if lang != "__fallback__"); PROGRAMMING_LANGUAGES = sorted(list(set(PROGRAMMING_LANGUAGES) | all_langs_in_map)); LANGUAGE_MAP["__fallback__"] = sorted(PROGRAMMING_LANGUAGES)
WEB_FRAMEWORKS = { "python": ["Django", "Flask", "FastAPI", "Pyramid", "None"], "javascript": ["Express", "Koa", "NestJS", "Next.js (React)", "Nuxt.js (Vue)", "SvelteKit", "None"], "typescript": ["Express", "Koa", "NestJS", "Next.js (React)", "Nuxt.js (Vue)", "Angular", "SvelteKit", "None"], "java": ["Spring Boot", "Quarkus", "Jakarta EE", "Micronaut", "None"], "c#": ["ASP.NET Core", "None"], "ruby": ["Ruby on Rails", "Sinatra", "None"], "php": ["Laravel", "Symfony", "CodeIgniter", "None"], "go": ["Gin", "Echo", "Fiber", "net/http", "None"], "rust": ["Actix Web", "Rocket", "Axum", "Warp", "None"], "kotlin": ["Spring Boot", "Ktor", "None"], "swift": ["Vapor", "Hummingbird", "None"],}
UI_LIBS = { "javascript": ["React", "Vue", "Angular", "Svelte", "SolidJS", "Preact", "Alpine.js", "HTMX", "None"], "typescript": ["React", "Vue", "Angular", "Svelte", "SolidJS", "Preact", "None"], "python": ["HTMX (with backend)", "Streamlit", "Dash", "NiceGUI", "None"], "dart": ["Flutter", "None"], "c#": ["Blazor", "MAUI", "WinForms", "WPF", "Uno Platform", "Avalonia UI", "None"], "swift": ["SwiftUI", "UIKit", "None"], "kotlin": ["Jetpack Compose (Android/Desktop)", "None"], "java": ["JavaFX", "Swing", "None"], "rust": ["Leptos", "Dioxus", "Yew", "Iced", "None"]}
STATE_MANAGEMENT = { "javascript": ["Redux", "Zustand", "Jotai", "Valtio", "Recoil", "Pinia (Vue)", "NgRx (Angular)", "Context API (React)", "None"], "typescript": ["Redux", "Zustand", "Jotai", "Valtio", "Recoil", "Pinia (Vue)", "NgRx (Angular)", "Context API (React)", "None"], "dart": ["Provider", "Riverpod", "Bloc/Cubit", "GetX", "None"], "rust": ["Sycamore Signals", "Leptos Signals", "Dioxus Signals", "Shared State Libs", "None"]}
DATABASES = sorted(["PostgreSQL", "MySQL", "SQLite", "SQL Server", "Oracle", "MongoDB", "Redis", "Cassandra", "Elasticsearch", "DynamoDB", "Firebase Realtime/Firestore", "Supabase (Postgres)", "None"])


# --- AI Service Abstraction & Implementations ---
# ... (Kelas AIService, OpenAIService, GeminiService tetap sama persis) ...
class AIService(ABC):
    @abstractmethod
    def list_models(self, api_key: str) -> list[str]: pass
    @abstractmethod
    def generate_text(self, api_key: str, model: str, prompt: str, temperature: float = 0.3) -> str: pass

class OpenAIService(AIService):
    def list_models(self, api_key: str) -> list[str]:
        if not openai_available: raise ImportError("OpenAI package not installed.")
        if not api_key: raise ValueError("OpenAI API Key is required.")
        try:
            client = OpenAI(api_key=api_key); models = client.models.list()
            gpt_models = sorted([m.id for m in models.data if 'gpt' in m.id and m.id.find('instruct')==-1 and m.id.find('vision')==-1 and m.id.find('embedding')==-1 and m.id.find('audio')==-1 and m.id.find('tts')==-1 and m.id.find('whisper')==-1 and m.id.find('dall-e')==-1 and not m.id.endswith('-0301') and not m.id.endswith('-0314') and not m.id.endswith('-0613')])
            priority = ['gpt-4o', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo']; ordered = [p for p in priority if p in gpt_models]; ordered.extend([m for m in gpt_models if m not in priority]); return ordered
        except AuthenticationError: raise ValueError("Invalid OpenAI API Key.")
        except APIConnectionError as e: raise ConnectionError(f"Failed to connect to OpenAI: {e}")
        except Exception as e: raise RuntimeError(f"Failed to retrieve OpenAI models: {e}")

    def generate_text(self, api_key: str, model: str, prompt: str, temperature: float = 0.3) -> str:
        if not openai_available: raise ImportError("OpenAI package not installed.")
        if not api_key or not model: raise ValueError("OpenAI API Key and Model are required.")
        try:
            client = OpenAI(api_key=api_key); response = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], temperature=temperature)
            if response.choices and response.choices[0].message: return response.choices[0].message.content.strip()
            else: raise RuntimeError("Invalid response structure from OpenAI.")
        except AuthenticationError: raise ValueError("Invalid OpenAI API Key.")
        except APIConnectionError as e: raise ConnectionError(f"Failed to connect to OpenAI: {e}")
        except NotFoundError: raise ValueError(f"OpenAI Model '{model}' not found.")
        except Exception as e:
            if "does not exist" in str(e): raise ValueError(f"OpenAI Model '{model}' not found.")
            raise RuntimeError(f"Error during OpenAI text generation: {e}")

class GeminiService(AIService):
    def list_models(self, api_key: str) -> list[str]:
        if not gemini_available: raise ImportError("Google GenerativeAI package not installed.")
        if not api_key: raise ValueError("Gemini API Key is required.")
        try:
            genai.configure(api_key=api_key)
            models_list = [m.name.replace("models/", "") for m in genai.list_models() if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name]
            common = ['gemini-1.5-pro-latest', 'gemini-1.5-flash-latest', 'gemini-pro']; [models_list.append(cm) for cm in common if not any(m.startswith(cm.split('-latest')[0]) for m in models_list)]
            priority = ['gemini-1.5-pro-latest', 'gemini-1.5-flash-latest', 'gemini-pro']; ordered = [p for p in priority if p in models_list]; ordered.extend(sorted([m for m in models_list if m not in priority])); return list(dict.fromkeys(ordered))
        except (google_exceptions.PermissionDenied, google_exceptions.Unauthenticated): raise ValueError("Invalid Gemini API Key/permission.")
        except Exception as e:
            if "API key not valid" in str(e): raise ValueError("Invalid Gemini API Key.")
            raise RuntimeError(f"Failed to retrieve Gemini models: {e}")

    def generate_text(self, api_key: str, model: str, prompt: str, temperature: float = 0.3) -> str:
        if not gemini_available: raise ImportError("Google GenerativeAI package not installed.")
        if not api_key or not model: raise ValueError("Gemini API Key and Model required.")
        try:
            genai.configure(api_key=api_key); model_id = f"models/{model}" if not model.startswith("models/") else model
            config = genai.types.GenerationConfig(temperature=temperature)
            safety = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
            gemini = genai.GenerativeModel(model_id); response = gemini.generate_content(prompt, generation_config=config, safety_settings=safety)
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
        except Exception as e:
            if "API key not valid" in str(e): raise ValueError("Invalid Gemini API Key.")
            if "404" in str(e) or "not found" in str(e).lower() or ("model" in str(e).lower() and "does not exist" in str(e).lower()): raise ValueError(f"Gemini Model '{model}' not found.")
            if "model" in str(e).lower() and "cannot be accessed" in str(e).lower(): raise ValueError(f"Gemini Model '{model}' cannot be accessed.")
            if "429" in str(e) or "resource exhausted" in str(e).lower(): raise ConnectionError("Gemini quota/rate limit reached.")
            if "SAFETY" in str(e).upper(): raise ValueError(f"Gemini blocked by safety: {e}")
            raise RuntimeError(f"Gemini text gen error: {e}")


# --- Main Application Class ---
class BlueprintGeneratorApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Blueprint Generator Pro (Sub-Modules Enabled)")
        self.root.geometry("1250x850")

        # --- State Variables ---
        self.modul_list = [] # List of {'id': int, 'parent_id': int|None, 'nama': str, 'deskripsi': str}
        self._next_module_id = 1 # Counter for unique module IDs
        # Mapping Treeview item ID (string returned by insert) to our internal module ID (int)
        self.treeview_iid_to_module_id = {}

        self.tests_enabled = tk.BooleanVar(value=False)
        self.generate_readme = tk.BooleanVar(value=True)
        self.generate_gitignore = tk.BooleanVar(value=True)
        self.git_init_enabled = tk.BooleanVar(value=False)
        self.selected_ai_provider = tk.StringVar(value="OpenAI")

        # --- AI Services ---
        self.ai_services: dict[str, AIService] = {}
        if openai_available: self.ai_services["OpenAI"] = OpenAIService()
        if gemini_available: self.ai_services["Gemini"] = GeminiService()
        if not self.ai_services: messagebox.showerror("AI Error", "No AI libs. Exiting."); self.root.quit(); return

        # --- GUI ---
        self._create_widgets()
        self._update_language_list(); self._update_dynamic_combos(); self._update_api_key_entry()
        self._update_parent_module_combo() # Initial population for parent combo
        self.update_status("Ready")

    def _create_widgets(self):
        # --- Paned Window Layout ---
        main_paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=6)
        main_paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        left_pane = ttk.Frame(main_paned_window, width=750); main_paned_window.add(left_pane, stretch="always")
        right_pane = ttk.Frame(main_paned_window, width=450); main_paned_window.add(right_pane, stretch="never")
        # Left Pane Notebook
        self.notebook = ttk.Notebook(left_pane); self.notebook.pack(fill=tk.BOTH, expand=True)
        # Right Pane Scrollable Setup
        right_canvas = tk.Canvas(right_pane, borderwidth=0, highlightthickness=0); right_scrollbar = ttk.Scrollbar(right_pane, orient="vertical", command=right_canvas.yview)
        self.right_scrollable_frame = ttk.Frame(right_canvas); self.right_scrollable_frame.bind("<Configure>", lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all"), width=e.width))
        right_canvas.bind_all("<MouseWheel>", lambda e: right_canvas.yview_scroll(-1 * int(e.delta / 60), "units"))
        right_canvas_window = right_canvas.create_window((0, 0), window=self.right_scrollable_frame, anchor="nw"); right_canvas.configure(yscrollcommand=right_scrollbar.set)
        right_canvas.pack(side="left", fill="both", expand=True); right_scrollbar.pack(side="right", fill="y")
        def frame_width(event): right_canvas.itemconfig(right_canvas_window, width=event.width)
        right_canvas.bind('<Configure>', frame_width)

        # --- Tab 1: Project Setup ---
        tab_setup = ttk.Frame(self.notebook, padding=10); self.notebook.add(tab_setup, text="1. Project Setup")
        setup_canvas = tk.Canvas(tab_setup, borderwidth=0, highlightthickness=0); setup_scrollbar = ttk.Scrollbar(tab_setup, orient="vertical", command=setup_canvas.yview)
        setup_scrollable_frame = ttk.Frame(setup_canvas); setup_scrollable_frame.bind("<Configure>", lambda e: setup_canvas.configure(scrollregion=setup_canvas.bbox("all"), width=e.width))
        setup_canvas.bind_all("<MouseWheel>", lambda e: setup_canvas.yview_scroll(-1 * int(e.delta / 60), "units"))
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
        ttk.Label(tech_stack_frame, text="Languages:").grid(row=0, column=2, sticky="nw", padx=(15, 5), pady=3); lang_list_frame = ttk.Frame(tech_stack_frame); lang_list_frame.grid(row=0, column=3, rowspan=4, sticky="nsew", padx=5, pady=3); lang_list_frame.rowconfigure(0, weight=1); lang_list_frame.columnconfigure(0, weight=1); self.listbox_language = tk.Listbox(lang_list_frame, height=8, selectmode=tk.EXTENDED, exportselection=False); lang_scrollbar = ttk.Scrollbar(lang_list_frame, orient="vertical", command=self.listbox_language.yview); self.listbox_language.config(yscrollcommand=lang_scrollbar.set); self.listbox_language.grid(row=0, column=0, sticky="nsew"); lang_scrollbar.grid(row=0, column=1, sticky="ns"); self.listbox_language.bind("<<ListboxSelect>>", self._on_app_type_or_language_change)
        ttk.Label(tech_stack_frame, text="Web Fw:").grid(row=1, column=0, sticky="w", padx=5, pady=3); self.combo_web_framework = ttk.Combobox(tech_stack_frame, values=["Select Lang"], width=30, state="readonly"); self.combo_web_framework.grid(row=1, column=1, sticky="ew", padx=5, pady=3); self.combo_web_framework.set("None")
        ttk.Label(tech_stack_frame, text="UI Lib/Fw:").grid(row=2, column=0, sticky="w", padx=5, pady=3); self.combo_ui_lib = ttk.Combobox(tech_stack_frame, values=["Select Lang"], width=30, state="readonly"); self.combo_ui_lib.grid(row=2, column=1, sticky="ew", padx=5, pady=3); self.combo_ui_lib.set("None")
        ttk.Label(tech_stack_frame, text="State Mgmt:").grid(row=3, column=0, sticky="w", padx=5, pady=3); self.combo_state_mgmt = ttk.Combobox(tech_stack_frame, values=["Select UI Lib"], width=30, state="readonly"); self.combo_state_mgmt.grid(row=3, column=1, sticky="ew", padx=5, pady=3); self.combo_state_mgmt.set("None")
        ttk.Label(tech_stack_frame, text="Database:").grid(row=4, column=0, sticky="w", padx=5, pady=3); self.combo_database = ttk.Combobox(tech_stack_frame, values=DATABASES, width=30, state="readonly"); self.combo_database.grid(row=4, column=1, sticky="ew", padx=5, pady=3); self.combo_database.set("None")
        ttk.Label(tech_stack_frame, text="Key Libs:").grid(row=5, column=0, sticky="nw", padx=5, pady=3); self.text_key_libs = tk.Text(tech_stack_frame, height=3, width=60, wrap=tk.WORD); self.text_key_libs.grid(row=5, column=1, columnspan=3, sticky="ew", padx=5, pady=3); ttk.Label(tech_stack_frame, text="(Comma-separated)").grid(row=6, column=1, columnspan=3, sticky="w", padx=5, pady=0)

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
        tab_modul = ttk.Frame(self.notebook, padding=10); self.notebook.add(tab_modul, text="2. Modules")
        # Input Frame
        modul_entry_frame = ttk.LabelFrame(tab_modul, text="Add/Edit Module", padding=10); modul_entry_frame.pack(fill="x", pady=5, anchor='n'); modul_entry_frame.columnconfigure(1, weight=1)
        ttk.Label(modul_entry_frame, text="Parent Module:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.combo_parent_module = ttk.Combobox(modul_entry_frame, values=["(Top Level)"], width=38, state="readonly"); self.combo_parent_module.grid(row=0, column=1, sticky="ew", padx=5, pady=3); self.combo_parent_module.set("(Top Level)")
        ttk.Label(modul_entry_frame, text="Module Name:").grid(row=1, column=0, sticky="w", padx=5, pady=3); self.entry_modul_nama = ttk.Entry(modul_entry_frame, width=40); self.entry_modul_nama.grid(row=1, column=1, sticky="ew", padx=5, pady=3)
        ttk.Label(modul_entry_frame, text="Description:").grid(row=2, column=0, sticky="nw", padx=5, pady=3); self.entry_modul_deskripsi = tk.Text(modul_entry_frame, height=4, width=50, wrap=tk.WORD); self.entry_modul_deskripsi.grid(row=2, column=1, sticky="ew", padx=5, pady=3)
        ttk.Button(modul_entry_frame, text="+ Add Module", command=self.tambah_modul).grid(row=3, column=1, sticky="e", pady=5, padx=5)
        # Treeview Frame
        modul_list_frame = ttk.LabelFrame(tab_modul, text="Module Hierarchy", padding=10); modul_list_frame.pack(fill="both", expand=True, pady=5); modul_list_frame.rowconfigure(0, weight=1); modul_list_frame.columnconfigure(0, weight=1)
        self.module_tree = ttk.Treeview(modul_list_frame, columns=("Description",), selectmode="browse")
        self.module_tree.heading("#0", text="Module Name") # #0 is the special tree column
        self.module_tree.heading("Description", text="Description")
        self.module_tree.column("#0", width=250, stretch=tk.YES)
        self.module_tree.column("Description", width=400, stretch=tk.YES)
        # Scrollbars for Treeview
        tree_scrollbar_y = ttk.Scrollbar(modul_list_frame, orient="vertical", command=self.module_tree.yview)
        tree_scrollbar_x = ttk.Scrollbar(modul_list_frame, orient="horizontal", command=self.module_tree.xview)
        self.module_tree.configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)
        self.module_tree.grid(row=0, column=0, sticky="nsew"); tree_scrollbar_y.grid(row=0, column=1, sticky="ns"); tree_scrollbar_x.grid(row=1, column=0, sticky="ew")
        # Action Buttons for Treeview
        tree_button_frame = ttk.Frame(tab_modul); tree_button_frame.pack(fill="x", pady=5)
        btn_delete_modul = ttk.Button(tree_button_frame, text="- Remove Selected Module (and children)", command=self.hapus_modul); btn_delete_modul.pack(side=tk.RIGHT, padx=10)
        # Maybe add Edit button later?

        # --- Tab 3: Preview & Generate ---
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
        try:
            style = ttk.Style(self.root); available = style.theme_names()
            for t in ['clam', 'alt', 'default']:
                 if t in available: style.theme_use(t); break
            style.configure("Accent.TButton", foreground="white", background="#0078D4", padding=5)
            style.map("Accent.TButton", background=[('active', '#005a9e')])
        except Exception as e: print(f"Info: Style err: {e}")


    # --- METHODS ---

    def _get_module_by_id(self, module_id: int) -> dict | None:
        """Helper to find a module dictionary by its ID."""
        for module in self.modul_list:
            if module['id'] == module_id:
                return module
        return None

    def _get_module_children_ids(self, parent_id: int | None) -> list[int]:
        """Helper to get IDs of direct children of a module."""
        return [m['id'] for m in self.modul_list if m['parent_id'] == parent_id]

    def _get_all_descendant_ids(self, module_id: int) -> list[int]:
        """Recursively finds all descendant IDs of a module."""
        descendants = []
        children = self._get_module_children_ids(module_id)
        for child_id in children:
            descendants.append(child_id)
            descendants.extend(self._get_all_descendant_ids(child_id))
        return descendants

    def _get_module_display_name(self, module_id: int, include_parents=True) -> str:
        """Generates a display name, optionally including parent path."""
        module = self._get_module_by_id(module_id)
        if not module: return "Unknown"
        if not include_parents or module['parent_id'] is None:
            return module['nama']
        else:
            parent_name = self._get_module_display_name(module['parent_id'], include_parents=True)
            return f"{parent_name} :: {module['nama']}"

    def _update_parent_module_combo(self):
        """Updates the Parent Module combobox with current modules."""
        # Store current selection
        current_selection_text = self.combo_parent_module.get()

        parents = ["(Top Level)"]
        # Add modules in a somewhat logical order (e.g., top-level first)
        top_level_ids = self._get_module_children_ids(None)
        processed_ids = set()

        def add_to_parents(mod_id, indent=0):
            if mod_id in processed_ids: return
            module = self._get_module_by_id(mod_id)
            if not module: return
            display_name = ("  " * indent) + module['nama']
            # Store full path or just name? Use full path for uniqueness potential
            # Let's store the ID internally and show a user-friendly name
            parents.append(self._get_module_display_name(mod_id)) # Show full path for clarity
            processed_ids.add(mod_id)
            children = self._get_module_children_ids(mod_id)
            for child_id in children:
                add_to_parents(child_id, indent + 1)

        for top_id in top_level_ids:
            add_to_parents(top_id)

        self.combo_parent_module['values'] = parents

        # Try to restore selection
        if current_selection_text in parents:
             self.combo_parent_module.set(current_selection_text)
        else:
            self.combo_parent_module.set("(Top Level)") # Default


    def tambah_modul(self):
        """Adds a new module or sub-module."""
        nama = self.entry_modul_nama.get().strip()
        deskripsi = self.entry_modul_deskripsi.get("1.0", tk.END).strip()
        parent_display_name = self.combo_parent_module.get()

        if not nama or not deskripsi:
            messagebox.showwarning("Input Missing", "Enter module name and description."); return

        parent_id = None
        if parent_display_name != "(Top Level)":
            # Find the module ID corresponding to the display name
            found = False
            for mod in self.modul_list:
                if self._get_module_display_name(mod['id']) == parent_display_name:
                    parent_id = mod['id']
                    found = True
                    break
            if not found:
                 messagebox.showerror("Error", f"Selected parent '{parent_display_name}' not found internally."); return

        # Check for duplicate name *under the same parent*
        sibling_ids = self._get_module_children_ids(parent_id)
        for sibling_id in sibling_ids:
             sibling = self._get_module_by_id(sibling_id)
             if sibling and sibling['nama'].lower() == nama.lower():
                 parent_name_for_msg = parent_display_name if parent_id is not None else "Top Level"
                 messagebox.showwarning("Duplicate Name", f"Module '{nama}' already exists under '{parent_name_for_msg}'.")
                 return


        new_id = self._next_module_id
        self._next_module_id += 1

        new_module = {'id': new_id, 'parent_id': parent_id, 'nama': nama, 'deskripsi': deskripsi}
        self.modul_list.append(new_module)

        # Insert into Treeview
        parent_iid = '' # Default for top-level
        if parent_id is not None:
            # Find the Treeview iid for the parent module ID
            for iid, mod_id in self.treeview_iid_to_module_id.items():
                if mod_id == parent_id:
                    parent_iid = iid
                    break

        try:
            # Insert the new item, using its internal ID as the Treeview iid for easy mapping
            new_iid = self.module_tree.insert(parent_iid, tk.END, iid=str(new_id), text=nama, values=(deskripsi,))
            self.treeview_iid_to_module_id[new_iid] = new_id # Map Treeview iid to our module id
        except tk.TclError as e:
            print(f"Error inserting into Treeview: {e}. Maybe duplicate iid?")
            # Handle potential duplicate iid error if logic is flawed
            # Rollback addition?
            self.modul_list.pop() # Remove the module we just added
            messagebox.showerror("Treeview Error", "Failed to add module to the tree.")
            return


        # Clear input and update parent combo
        self.entry_modul_nama.delete(0, tk.END)
        self.entry_modul_deskripsi.delete("1.0", tk.END)
        self._update_parent_module_combo()
        self.update_status(f"Module '{nama}' added.")
        # Open the parent node in the tree
        if parent_iid:
             self.module_tree.item(parent_iid, open=True)


    def hapus_modul(self):
        """Removes the selected module and all its descendants."""
        selected_iids = self.module_tree.selection() # Get selected Treeview item IDs
        if not selected_iids:
            messagebox.showwarning("No Selection", "Select a module to remove."); return

        selected_iid = selected_iids[0] # Only handle single selection for simplicity now
        module_id_to_remove = self.treeview_iid_to_module_id.get(selected_iid)

        if module_id_to_remove is None:
             messagebox.showerror("Error", "Could not find internal ID for selected module.")
             return

        module_to_remove = self._get_module_by_id(module_id_to_remove)
        if not module_to_remove:
             messagebox.showerror("Error", "Selected module data not found.")
             return

        confirm_msg = f"Remove '{module_to_remove['nama']}'?"
        descendant_ids = self._get_all_descendant_ids(module_id_to_remove)
        if descendant_ids:
            confirm_msg += f"\nThis will also remove {len(descendant_ids)} sub-module(s)."

        if not messagebox.askyesno("Confirm Removal", confirm_msg):
            return

        # --- Perform Deletion ---
        ids_to_delete = [module_id_to_remove] + descendant_ids

        # 1. Remove from Treeview (must do before removing from list for mapping)
        items_to_delete_in_tree = [str(mid) for mid in ids_to_delete if str(mid) in self.treeview_iid_to_module_id]
        for item_iid in items_to_delete_in_tree:
             if self.module_tree.exists(item_iid): # Check existence before delete
                  self.module_tree.delete(item_iid)
             # Remove from mapping
             if item_iid in self.treeview_iid_to_module_id:
                  del self.treeview_iid_to_module_id[item_iid]


        # 2. Remove from self.modul_list
        self.modul_list = [mod for mod in self.modul_list if mod['id'] not in ids_to_delete]

        # 3. Update parent combo
        self._update_parent_module_combo()
        self.update_status(f"Module '{module_to_remove['nama']}' and descendants removed.")

    def _populate_module_treeview(self):
        """Clears and refills the module Treeview from self.modul_list."""
        # Clear existing tree and mapping
        for iid in self.module_tree.get_children():
            self.module_tree.delete(iid)
        self.treeview_iid_to_module_id.clear()

        # Build a dictionary for faster parent lookup during population
        modules_by_id = {mod['id']: mod for mod in self.modul_list}
        # Use a dictionary to track which treeview items have been created
        treeview_items_created = {} # Maps module_id to treeview_iid

        # Recursive function to add items
        def add_items_recursively(parent_module_id=None):
            child_ids = self._get_module_children_ids(parent_module_id)
            parent_iid_str = str(parent_module_id) if parent_module_id else ''

            # Ensure parent exists in treeview before adding children (should exist if logic is correct)
            if parent_module_id and parent_iid_str not in treeview_items_created:
                print(f"Warning: Parent {parent_module_id} not found in treeview items created when trying to add children.")
                # Maybe try to add the parent first? Requires careful handling.
                return # Avoid errors for now

            for child_id in child_ids:
                module = modules_by_id.get(child_id)
                if module:
                    child_iid_str = str(child_id)
                    # Check if already added (safety)
                    if child_iid_str in treeview_items_created: continue

                    tree_parent_iid = treeview_items_created.get(parent_module_id, '') # Get Treeview iid of parent

                    try:
                        new_iid = self.module_tree.insert(tree_parent_iid, tk.END, iid=child_iid_str, text=module['nama'], values=(module['deskripsi'],))
                        treeview_items_created[child_id] = new_iid # Record creation
                        self.treeview_iid_to_module_id[new_iid] = child_id # Update mapping
                        # Recursively add children of this new item
                        add_items_recursively(child_id)
                    except tk.TclError as e:
                         print(f"Error populating treeview for module {child_id}: {e}")


        # Start adding from top-level modules
        add_items_recursively(None)


    def _format_modules_hierarchical(self, parent_id=None, indent=0) -> str:
        """Recursively formats modules into a hierarchical markdown list."""
        markdown = ""
        children_ids = self._get_module_children_ids(parent_id)
        indent_str = "    " * indent # 4 spaces per indent level

        for module_id in children_ids:
            module = self._get_module_by_id(module_id)
            if module:
                markdown += f"{indent_str}- **{module['nama']}:** {module['deskripsi']}\n"
                # Recursively add children
                markdown += self._format_modules_hierarchical(module_id, indent + 1)
        return markdown


    # --- Methods unchanged by Sub-Module Logic ---
    def _on_app_type_or_language_change(self, event=None): self._update_language_list(); self._update_dynamic_combos()
    def _update_language_list(self):
        # ... (Implementation remains the same) ...
        selected_app_type = self.combo_type.get()
        relevant_languages = LANGUAGE_MAP.get(selected_app_type, LANGUAGE_MAP["__fallback__"])
        old_selection_indices = self.listbox_language.curselection()
        old_selected_langs = {self.listbox_language.get(i) for i in old_selection_indices}
        self.listbox_language.config(state=tk.NORMAL)
        self.listbox_language.delete(0, tk.END)
        if relevant_languages:
            for lang in relevant_languages: self.listbox_language.insert(tk.END, lang)
            for i, lang in enumerate(relevant_languages):
                if lang in old_selected_langs: self.listbox_language.selection_set(i)
        else:
            self.listbox_language.insert(tk.END, "No relevant languages"); self.listbox_language.config(state=tk.DISABLED)

    def _update_dynamic_combos(self):
        # ... (Implementation remains the same) ...
        selected_lang_indices = self.listbox_language.curselection()
        selected_langs = [self.listbox_language.get(i).lower() for i in selected_lang_indices]
        # Web Framework
        web_options = {"None"}; [web_options.update(WEB_FRAMEWORKS.get(lang, [])) for lang in selected_langs]
        valid_web_options = sorted(list(web_options)); current_web_fw = self.combo_web_framework.get()
        self.combo_web_framework['values'] = valid_web_options
        if current_web_fw in valid_web_options: self.combo_web_framework.set(current_web_fw)
        elif "None" in valid_web_options: self.combo_web_framework.set("None")
        elif valid_web_options: self.combo_web_framework.set(valid_web_options[0])
        else: self.combo_web_framework.set("")
        self.combo_web_framework.config(state="readonly" if valid_web_options else tk.DISABLED)
        # UI Lib
        ui_options = {"None"}; [ui_options.update(UI_LIBS.get(lang, [])) for lang in selected_langs]
        valid_ui_options = sorted(list(ui_options)); current_ui_lib = self.combo_ui_lib.get()
        self.combo_ui_lib['values'] = valid_ui_options
        if current_ui_lib in valid_ui_options: self.combo_ui_lib.set(current_ui_lib)
        elif "None" in valid_ui_options: self.combo_ui_lib.set("None")
        elif valid_ui_options: self.combo_ui_lib.set(valid_ui_options[0])
        else: self.combo_ui_lib.set("")
        self.combo_ui_lib.config(state="readonly" if valid_ui_options else tk.DISABLED)
        # State Management
        state_options = {"None"}; current_ui_lib_lower = self.combo_ui_lib.get().lower()
        for lang in selected_langs:
            is_relevant_ui = any(ui_lib.lower() == current_ui_lib_lower for ui_lib in UI_LIBS.get(lang, []))
            if is_relevant_ui or current_ui_lib_lower == "none" or not selected_langs : state_options.update(STATE_MANAGEMENT.get(lang, []))
        valid_state_options = sorted(list(state_options)); current_state_mgmt = self.combo_state_mgmt.get()
        self.combo_state_mgmt['values'] = valid_state_options
        if current_state_mgmt in valid_state_options: self.combo_state_mgmt.set(current_state_mgmt)
        elif "None" in valid_state_options: self.combo_state_mgmt.set("None")
        elif valid_state_options: self.combo_state_mgmt.set(valid_state_options[0])
        else: self.combo_state_mgmt.set("")
        self.combo_state_mgmt.config(state="readonly" if valid_state_options else tk.DISABLED)


    def update_status(self, message): self.status_label.config(text=message); self.root.update_idletasks()
    def _update_api_key_entry(self, event=None):
        provider = self.selected_ai_provider.get(); self.combo_model.set(''); self.combo_model['values'] = []; self.combo_model.config(state=tk.DISABLED)
        openai_key = self.entry_openai_apikey.get(); gemini_key = self.entry_gemini_apikey.get()
        self.openai_api_key_frame.pack_forget(); self.gemini_api_key_frame.pack_forget()
        current_key = ""; api_entry_widget = None
        if provider == "OpenAI": self.openai_api_key_frame.pack(fill=tk.X, expand=True); self.entry_openai_apikey.delete(0, tk.END); self.entry_openai_apikey.insert(0, openai_key); current_key = openai_key.strip(); api_entry_widget = self.entry_openai_apikey
        elif provider == "Gemini": self.gemini_api_key_frame.pack(fill=tk.X, expand=True); self.entry_gemini_apikey.delete(0, tk.END); self.entry_gemini_apikey.insert(0, gemini_key); current_key = gemini_key.strip(); api_entry_widget = self.entry_gemini_apikey
        if current_key: self.fetch_models()
        else: self.combo_model.set("Enter API Key and Fetch")
    def _get_selected_ai_service(self) -> tuple[AIService | None, str | None]:
        provider = self.selected_ai_provider.get(); service = self.ai_services.get(provider); key = ""
        if not service: return None, None
        if provider == "OpenAI": key = self.entry_openai_apikey.get().strip()
        elif provider == "Gemini": key = self.entry_gemini_apikey.get().strip()
        return service, key
    def fetch_models(self):
        service, key = self._get_selected_ai_service(); provider = self.selected_ai_provider.get()
        if not service: messagebox.showerror("Service Error", f"AI Provider unavailable."); return
        if not key: messagebox.showerror("API Key Missing", f"Enter API Key for {provider}."); return
        self.update_status(f"Fetching {provider} models..."); self._disable_ui_during_action(fetching=True)
        def load():
            models, err = [], None
            try: models = service.list_models(key)
            except (ValueError, ConnectionError, ImportError, RuntimeError) as e: err = f"Error: {e}"
            except Exception as e: err = f"Unexpected error: {e}"
            finally:
                def update_gui():
                    self._enable_ui_after_action(fetching=True)
                    if err: messagebox.showerror(f"Fetch Error ({provider})", err); self.combo_model.set('Fetch Failed'); self.combo_model.config(state=tk.DISABLED); self.update_status(f"Failed fetch.")
                    elif not models: messagebox.showwarning(f"No Models ({provider})", "No models found."); self.combo_model.set('No models'); self.combo_model.config(state=tk.DISABLED); self.update_status(f"No models found.")
                    else: self._update_model_combo(models); self.update_status(f"{provider} models fetched.")
                self.root.after(0, update_gui)
        threading.Thread(target=load, daemon=True).start()
    def _update_model_combo(self, models):
         self.combo_model["values"] = models
         if models: self.combo_model.set(models[0]); self.combo_model.config(state="readonly")
         else: self.combo_model.set(""); self.combo_model.config(state=tk.DISABLED)
    def clear_form(self):
        if not messagebox.askyesno("Confirm Clear", "Clear all inputs?"): return
        for w in [self.entry_name, self.entry_openai_apikey, self.entry_gemini_apikey, self.entry_modul_nama]: w.delete(0, tk.END)
        for w in [self.text_purpose, self.text_target_users, self.text_main_workflow, self.text_data_entities, self.text_features, self.text_key_libs, self.text_design_principles, self.text_nfrs, self.text_notes, self.entry_modul_deskripsi]: w.delete("1.0", tk.END)
        self.preview_output.config(state=tk.NORMAL); self.preview_output.delete("1.0", tk.END); self.preview_output.config(state=tk.DISABLED)
        app_type = "Web" if "Web" in self.combo_type['values'] else (self.combo_type['values'][0] if self.combo_type['values'] else ""); self.combo_type.set(app_type)
        self._update_language_list(); self.listbox_language.selection_clear(0, tk.END); self._update_dynamic_combos()
        self.combo_database.set("None"); self.selected_ai_provider.set("OpenAI"); self.combo_model.set(""); self.combo_model['values'] = []
        # Clear Modules Data & Tree
        self.modul_list.clear(); self._next_module_id = 1; self.treeview_iid_to_module_id.clear()
        for i in self.module_tree.get_children(): self.module_tree.delete(i)
        self._update_parent_module_combo()
        self.tests_enabled.set(False); self.generate_readme.set(True); self.generate_gitignore.set(True); self.git_init_enabled.set(False)
        self.update_status("Form cleared.")
    def ambil_input_data(self) -> dict | None:
        pd = {};
        pd["name"]=self.entry_name.get().strip(); pd["purpose"]=self.text_purpose.get("1.0", tk.END).strip(); pd["target_users"]=self.text_target_users.get("1.0", tk.END).strip()
        pd["main_workflow"]=self.text_main_workflow.get("1.0", tk.END).strip(); pd["data_entities"]=self.text_data_entities.get("1.0", tk.END).strip(); pd["features_manual"]=self.text_features.get("1.0", tk.END).strip()
        pd["modules"]=self.modul_list # Save the hierarchical list
        pd["project_type"]=self.combo_type.get()
        lang_idx=self.listbox_language.curselection(); pd["language_list"]=[self.listbox_language.get(i) for i in lang_idx]; pd["language"]=", ".join(pd["language_list"])
        pd["web_framework"]=self.combo_web_framework.get(); pd["ui_lib"]=self.combo_ui_lib.get(); pd["state_mgmt"]=self.combo_state_mgmt.get(); pd["database"]=self.combo_database.get()
        pd["key_libs"]=self.text_key_libs.get("1.0", tk.END).strip(); pd["design_principles"]=self.text_design_principles.get("1.0", tk.END).strip(); pd["nfrs"]=self.text_nfrs.get("1.0", tk.END).strip(); pd["notes"]=self.text_notes.get("1.0", tk.END).strip()
        pd["tests_enabled"]=self.tests_enabled.get(); pd["gen_readme"]=self.generate_readme.get(); pd["gen_gitignore"]=self.generate_gitignore.get(); pd["git_init"]=self.git_init_enabled.get()
        ai_provider=self.selected_ai_provider.get(); _, api_key_val = self._get_selected_ai_service()
        if not pd["features_manual"] and not pd["modules"]: messagebox.showerror("Input Missing", "Provide Features or Modules."); return None
        required={"Name":pd["name"], "Purpose":pd["purpose"], "Type":pd["project_type"], "Lang":pd["language"], "Provider":ai_provider, f"API Key":api_key_val}
        missing=[name for name, val in required.items() if not val]
        if missing: messagebox.showerror("Input Missing", f"Required:\n- {', '.join(missing)}"); return None
        for key in ["web_framework", "ui_lib", "state_mgmt", "database"]: pd[key] = "" if pd[key].lower() == "none" else pd[key]
        # Include next_module_id for saving state correctly
        pd["_next_module_id"] = self._next_module_id
        return pd
    def isi_form_data(self, data: dict):
        self.clear_form()
        self.entry_name.insert(0, data.get("name", "")); self.text_purpose.insert("1.0", data.get("purpose", "")); self.text_target_users.insert("1.0", data.get("target_users", "")); self.text_main_workflow.insert("1.0", data.get("main_workflow", ""))
        self.text_data_entities.insert("1.0", data.get("data_entities", "")); self.text_features.insert("1.0", data.get("features_manual", ""))
        app_type = data.get("project_type", "Web"); default_type = "Web" if "Web" in self.combo_type['values'] else (self.combo_type['values'][0] if self.combo_type['values'] else ""); self.combo_type.set(app_type if app_type in self.combo_type['values'] else default_type)
        # Load Modules and Rebuild Tree
        self.modul_list = data.get("modules", [])
        self._next_module_id = data.get("_next_module_id", 1) # Restore next ID
        self._populate_module_treeview() # Rebuild tree from loaded list
        self._update_parent_module_combo() # Update combo based on rebuilt tree
        # Update Lang List AFTER modules potentially set type
        self._update_language_list(); self.listbox_language.selection_clear(0, tk.END); langs = data.get("language_list", [])
        if langs:
            items = self.listbox_language.get(0, tk.END); not_found = []
            for lang in langs:
                try: idx=items.index(lang); self.listbox_language.selection_set(idx); self.listbox_language.see(idx)
                except ValueError: not_found.append(lang)
            if not_found: messagebox.showwarning("Lang Mismatch", f"Saved langs incompatible: {', '.join(not_found)}")
        self._update_dynamic_combos()
        for key, combo in [("web_framework", self.combo_web_framework), ("ui_lib", self.combo_ui_lib), ("state_mgmt", self.combo_state_mgmt), ("database", self.combo_database)]: combo.set(data.get(key, "None"))
        self.text_key_libs.insert("1.0", data.get("key_libs", "")); self.text_design_principles.insert("1.0", data.get("design_principles", "")); self.text_nfrs.insert("1.0", data.get("nfrs", "")); self.text_notes.insert("1.0", data.get("notes", ""))
        self.entry_openai_apikey.insert(0, data.get("openai_api_key", "")); self.entry_gemini_apikey.insert(0, data.get("gemini_api_key", ""))
        provider = data.get("ai_provider", "OpenAI"); self.selected_ai_provider.set(provider if provider in self.ai_services else (list(self.ai_services.keys())[0] if self.ai_services else ""))
        self.root.after(500, lambda: self.combo_model.set(data.get("model", ""))) # Delay model set
        self.tests_enabled.set(data.get("tests_enabled", False)); self.generate_readme.set(data.get("gen_readme", True)); self.generate_gitignore.set(data.get("gen_gitignore", True)); self.git_init_enabled.set(data.get("git_init", False))
        self.update_status("Project loaded."); self.notebook.select(0)
    def simpan_project(self):
        data = self.ambil_input_data();
        if not data: return
        data['ai_provider'] = self.selected_ai_provider.get(); data['model'] = self.combo_model.get()
        data['openai_api_key'] = self.entry_openai_apikey.get(); data['gemini_api_key'] = self.entry_gemini_apikey.get() # WARNING: Plain text
        fp = filedialog.asksaveasfilename(defaultextension=".bpgproj", filetypes=[("BPG Proj", "*.bpgproj"), ("JSON", "*.json"), ("All", "*.*")], title="Save")
        if fp:
            try: open(fp, 'w', encoding='utf-8').write(json.dumps(data, indent=2, ensure_ascii=False)); self.update_status(f"Saved: {os.path.basename(fp)}"); messagebox.showinfo("Save OK", "Project saved.")
            except Exception as e: messagebox.showerror("Save Error", f"Could not save:\n{e}"); self.update_status("Save error.")
    def buka_project(self):
        fp = filedialog.askopenfilename(filetypes=[("BPG Proj", "*.bpgproj"), ("JSON", "*.json"), ("All", "*.*")], title="Load")
        if fp:
            try: data = json.load(open(fp, 'r', encoding='utf-8')); self.isi_form_data(data); self.update_status(f"Loaded: {os.path.basename(fp)}")
            except Exception as e: messagebox.showerror("Load Error", f"Failed to load:\n{e}"); self.update_status("Load error.")

    def _prepare_prompts(self, config_data: dict) -> dict:
        prompts = {}; d = config_data
        # --- HIERARCHICAL MODULE FORMATTING ---
        formatted_modules = self._format_modules_hierarchical()
        # --------------------------------------
        features_combined = d.get('features_manual', '');
        if formatted_modules: features_combined += "\n\n## Application Modules (Hierarchy):\n" + formatted_modules
        elif d.get('modules'): # Fallback for old format potentially? Or just use flat list if hierarchical fails? Let's assume hierarchical worked.
             pass # formatted_modules handles it
        test_ctx, test_md, test_rules = ("\n- Testing: Include `tests/`.", "**Testing:** Include tests.", "MUST have unit tests.") if d['tests_enabled'] else ("\n- Testing: Disabled.", "**Testing:** Disabled.", "IMPORTANT: NO tests.")
        safety = """Before generating... [full safety rule text] ... MANDATORY FINAL STEP CHECK.""" # Keep full text
        tech = f"- Langs: {d['language']}" + (f"\n- WebFw: {d['web_framework']}" if d.get('web_framework') else "") + (f"\n- UI Lib: {d['ui_lib']}" if d.get('ui_lib') else "") + (f"\n- State: {d['state_mgmt']}" if d.get('state_mgmt') else "") + (f"\n- DB: {d['database']}" if d.get('database') else "") + (f"\n- Libs: {d['key_libs']}" if d.get('key_libs') else "")
        sys_prompt = f"AI architect for '{d['name']}'. Goal: {d['purpose']}. Users: {d['target_users'] or 'N/A'}. WF: {d['main_workflow'] or 'N/A'}. Data: {d['data_entities'] or 'N/A'}. Type: {d['project_type']}. Stack:\n{tech}\nPrinciples: {d['design_principles'] or 'Best practices'}. NFRs: {d['nfrs'] or 'Standard'}. Notes: {d['notes'] or 'None'}{test_ctx}\nAdhere STRICTLY to docs & rules. Clean, modular code."
        rules = [safety.strip(), test_rules, f"Langs: {d['language']}.", f"Type: '{d['project_type']}'.",]
        if d.get('web_framework'): rules.append(f"Use '{d['web_framework']}'.")
        if d.get('ui_lib'): rules.append(f"Use '{d['ui_lib']}'.")
        if d.get('state_mgmt'): rules.append(f"Use '{d['state_mgmt']}'.")
        if d.get('database'): rules.append(f"Use '{d['database']}'.")
        if d.get('design_principles'): rules.append(f"Apply: {d['design_principles']}.")
        prompts[".cursorrules"] = json.dumps({"system": sys_prompt.strip(), "rules": rules}, indent=2)
        prompts["architecture.md"] = f"Create `architecture.md` for '{d['name']}'. Goal:{d['purpose']}. Type:{d['project_type']}. Stack:\n{tech}\nFeatures:\n{features_combined}\nContext: Users:{d['target_users'] or 'N/A'}, WF:{d['main_workflow'] or 'N/A'}, Data:{d['data_entities'] or 'N/A'}, Principles:{d['design_principles'] or 'N/A'}, NFRs:{d['nfrs'] or 'N/A'}, Notes:{d['notes'] or 'N/A'}.\n\nTASK: Detail: 1.Arch Style(justify). 2.Components Diagram/Desc. 3.Folder Structure(explain, list config files). 4.Component Responsibilities (reflect hierarchy). 5.Data Model(conceptual). 6.API Contract(if needed). 7.Tech Justification. 8.{test_md} 9.Deployment(conceptual)."
        prompts["project_plan.md"] = f"Create `project_plan.md` for '{d['name']}'. Goal:{d['purpose']}. Type:{d['project_type']}. Stack:\n{tech}\nFeatures:\n{features_combined}\nContext: Users:{d['target_users'] or 'N/A'}, WF:{d['main_workflow'] or 'N/A'}, Data:{d['data_entities'] or 'N/A'}, NFRs:{d['nfrs'] or 'N/A'}, Notes:{d['notes'] or 'N/A'}.\n\nTASK: Generate plan: 1.Summary. 2.Scope/Features. 3.Phases/Milestones. 4.Detailed Task Checklist (`- [ ]`) per phase (realistic, full scope, logical order, incl. setup, link tasks to features/modules reflecting hierarchy, {test_md}). 5.Tech Summary."
        if d['gen_readme']: prompts["README.md"] = f"Create `README.md` for '# {d['name']}'.\n\n## Desc\n{d['purpose']}. Users: {d['target_users'] or 'N/A'}.\n\n## Features\n(List based on:\n{features_combined})\n\n## Stack\n{tech}\n\n## Setup\n(Generic steps for {d['language']}/{d.get('web_framework','')}...).\n\n## Running\n(Basic command...)."
        if d['gen_gitignore']: prompts[".gitignore"] = f"Generate standard `.gitignore` for: {d['language']}, {d.get('web_framework', '')}, {d.get('ui_lib', '')}. Incl OS, IDE, deps, .env, logs. Raw content ONLY."
        return prompts

    def generate_blueprint(self):
        config = self.ambil_input_data();
        if not config: return
        service, api_key = self._get_selected_ai_service(); provider = self.selected_ai_provider.get(); model = self.combo_model.get()
        if not service or not api_key or not model or model in ["Loading...", "Fetch Failed", "No models", "Enter API Key"]: messagebox.showerror("Config Error", "Check AI Provider, API Key, Model."); return
        folder = filedialog.askdirectory(title="Select Output Folder");
        if not folder: return
        self.update_status("Starting generation..."); self._disable_ui_during_action()
        self.preview_output.config(state=tk.NORMAL); self.preview_output.delete("1.0", tk.END); self.preview_output.config(state=tk.DISABLED)
        try: prompts = self._prepare_prompts(config)
        except Exception as e: messagebox.showerror("Prompt Error", f"Prompt prep failed: {e}"); self._enable_ui_after_action(); return
        def do_generate():
            results, errors, files = {}, [], list(prompts.keys())
            for idx, fname in enumerate(files):
                prompt = prompts[fname]; self.update_status(f"Generating {fname} ({idx+1}/{len(files)})...")
                try:
                    text = prompt if fname == ".cursorrules" else service.generate_text(api_key, model, prompt, temperature=0.35)
                    results[fname] = text
                    try: filepath = os.path.join(folder, fname); open(filepath, "w", encoding="utf-8").write(text)
                    except IOError as we: errors.append(f"Write fail {fname}: {we}"); del results[fname]
                except (ValueError, ConnectionError, ImportError, RuntimeError) as e: errors.append(f"Gen fail {fname}: {e}"); break
                except Exception as e: errors.append(f"Unexpected gen fail {fname}: {e}")
            git_ok, git_err = None, None
            if config['git_init'] and not any(isinstance(e, (ValueError, ConnectionError, ImportError)) for e in errors):
                self.update_status("Initializing Git...");
                try:
                    subprocess.run(['git', '--version'], check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                    if not os.path.isdir(os.path.join(folder, '.git')): subprocess.run(['git', 'init'], cwd=folder, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0); git_ok = True
                    else: git_ok = False
                except Exception as ge: git_err = f"Git init error: {ge}"
                if git_err: errors.append(f"Git Fail: {git_err}")
            self.root.after(0, self._generation_complete, results, errors, folder, git_ok)
        threading.Thread(target=do_generate, daemon=True).start()

    def _disable_ui_during_action(self, fetching=False):
        widgets = [self.btn_generate, self.btn_save, self.btn_open, self.btn_clear, self.btn_fetch_models]
        if fetching: widgets.extend([self.combo_provider, self.entry_openai_apikey, self.entry_gemini_apikey, self.combo_model])
        else: widgets.append(self.btn_fetch_models)
        for w in widgets:
            try: w.config(state=tk.DISABLED)
            except tk.TclError: pass

    def _enable_ui_after_action(self, fetching=False):
        widgets = [self.btn_generate, self.btn_save, self.btn_open, self.btn_clear, self.btn_fetch_models, self.combo_provider, self.entry_openai_apikey, self.entry_gemini_apikey]
        for w in widgets:
             if isinstance(w, ttk.Combobox) and w != self.combo_model: w.config(state="readonly")
             elif w != self.combo_model: w.config(state=tk.NORMAL)
        self.combo_model.config(state="readonly" if self.combo_model['values'] else tk.DISABLED)

    def _generation_complete(self, results: dict, errors: list, folder: str, git_init_success: bool | None):
        # ... (Implementation remains the same) ...
        self._enable_ui_after_action(); preview = ""; success = sorted(list(results.keys()))
        requested = [".cursorrules", "architecture.md", "project_plan.md"] + (["README.md"] if self.generate_readme.get() else []) + ([".gitignore"] if self.generate_gitignore.get() else [])
        failed = sorted([f for f in requested if f not in success])
        if results:
            for fname in success: preview += f"=== {fname} ===\n{results[fname]}\n\n"
            self.preview_output.config(state=tk.NORMAL); self.preview_output.delete("1.0", tk.END); self.preview_output.insert("1.0", preview); self.preview_output.config(state=tk.DISABLED)
        msg, type, status = "", "info", "OK."
        err_sum = '\n- '.join(errors) if errors else "None."
        if not results and errors: msg, type, status = f"Failed.\nFolder: {folder}\nErrors:\n- {err_sum}", "error", "Failed."
        elif errors: msg, type, status = f"Completed w/ errors.\nFolder: {folder}\n" + (f"OK: {', '.join(success)}\n" if success else "") + (f"Fail: {', '.join(failed)}\n" if failed else "") + f"Errors:\n- {err_sum}", "warning", "Completed w/ errors."
        else: msg, type, status = f"OK!\nFolder: {folder}\nFiles: {', '.join(success)}" + ("\nGit repo initialized." if git_init_success else ("\n(Already Git repo)." if git_init_success is False else "")), "info", "OK."
        if failed and results: msg += f"\n\nFailed: {', '.join(failed)}"
        title = "Complete" if type=="info" else ("Warnings" if type=="warning" else "Failed")
        box = messagebox.showinfo if type=="info" else (messagebox.showwarning if type=="warning" else messagebox.showerror)
        box(title, msg); self.update_status(status)
        if results and messagebox.askyesno("Open?", f"Open folder?\n{folder}"):
            try:
                if os.name == 'nt': os.startfile(folder)
                elif os.uname().sysname == 'Darwin': subprocess.run(['open', folder], check=True)
                else: subprocess.run(['xdg-open', folder], check=True)
            except Exception as e: messagebox.showerror("Error", f"Could not open: {e}")


    def run(self): self.root.mainloop()


# --- Entry Point ---
if __name__ == "__main__":
    # ... (Entry point code remains the same) ...
    if not openai_available and not gemini_available: print("ERROR: Install 'openai' and/or 'google-generativeai'.")
    else:
        if not openai_available: print("Warn: 'openai' not found.")
        if not gemini_available: print("Warn: 'google-generativeai' not found.")
        main_root = tk.Tk(); app = BlueprintGeneratorApp(main_root)
        if app.ai_services: app.run()