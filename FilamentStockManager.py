from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import importlib
import importlib.util
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import uuid

yaml = importlib.import_module("yaml") if importlib.util.find_spec("yaml") else None
barcode_lib = importlib.import_module("barcode") if importlib.util.find_spec("barcode") else None
ImageWriter = None
if barcode_lib:
	try:
		from barcode.writer import ImageWriter
	except Exception:
		ImageWriter = None


@dataclass
class FilamentSpool:
	id: str
	brand: str
	material: str
	name: str
	color: str
	original_weight: float
	is_opened: bool
	remaining_weight: float | None
	price: float
	buying_date: str
	created_at: str
	updated_at: str
	barcode: str
	actual_weight: float  # Total weight including spool holder
	spool_holder_weight: float  # Weight of empty spool holder (calculated from actual - original)

	def to_dict(self) -> dict:
		return {
			"id": self.id,
			"brand": self.brand,
			"material": self.material,
			"name": self.name,
			"color": self.color,
			"original_weight": self.original_weight,
			"is_opened": self.is_opened,
			"remaining_weight": self.remaining_weight,
			"price": self.price,
			"buying_date": self.buying_date,
			"created_at": self.created_at,
			"updated_at": self.updated_at,
			"barcode": self.barcode,
			"actual_weight": self.actual_weight,
			"spool_holder_weight": self.spool_holder_weight,
		}

	@classmethod
	def from_dict(cls, data: dict) -> "FilamentSpool":
		# Generate ID if missing (for backward compatibility with old UUID-based files)
		spool_id = data.get("id")
		if not spool_id:
			# Generate human-readable ID from material and color
			material = str(data.get("material", "UNKNOWN")).upper().replace(" ", "-")
			color = str(data.get("color", "UNKNOWN")).upper().replace(" ", "-")
			spool_id = f"{material}-{color}-001"
		
		return cls(
			id=spool_id,
			brand=str(data.get("brand", "")).strip(),
			material=str(data.get("material", "")).strip(),
			name=str(data.get("name", "")).strip(),
			color=str(data.get("color", "")).strip(),
			original_weight=float(data.get("original_weight", data.get("estimated_weight", 0))),
			is_opened=bool(data.get("is_opened", False)),
			remaining_weight=(
				None
				if data.get("remaining_weight", None) in (None, "")
				else float(data.get("remaining_weight"))
			),
			price=float(data.get("price", 0)),
			buying_date=str(data.get("buying_date", "")),
			created_at=data.get("created_at", datetime.now().isoformat()),
			updated_at=data.get("updated_at", datetime.now().isoformat()),
			barcode=data.get("barcode", spool_id),
			actual_weight=float(data.get("actual_weight", 0)),
			spool_holder_weight=float(data.get("spool_holder_weight", 0)),
		)


class FilamentStockApp:
	def __init__(self, root: tk.Tk):
		self.root = root
		self.root.title("Filament Stock Manager")
		self.root.geometry("1280x600")

		self.spools: list[FilamentSpool] = []
		self.current_file: Path | None = None
		self.selected_index: int | None = None

		# Default values for dropdowns
		self.default_materials = ["PLA", "PLA Silk", "PETG", "TPU", "ABS", "ASA", "Nylon", "PETG Carbon", "PC"]
		self.default_colors = ["Black", "White", "Red", "Blue", "Green", "Yellow", "Orange", "Purple", "Gray", "Natural"]
		self.default_brands = ["Prusa", "Sunlu", "Bambu Lab", "Polymaker"]
		self.default_weights = ["1000", "250"]  # 1kg and 250g in grams

		self.brand_var = tk.StringVar()
		self.material_var = tk.StringVar()
		self.name_var = tk.StringVar()
		self.color_var = tk.StringVar()
		self.original_weight_var = tk.StringVar()
		self.actual_weight_var = tk.StringVar()
		self.remaining_weight_var = tk.StringVar()
		self.status_var = tk.StringVar(value="new")
		self.price_var = tk.StringVar()
		self.buying_date_var = tk.StringVar()
		self.current_id: str | None = None

		self._build_menu()
		self._build_layout()
		
		# Add trace to auto-calculate remaining weight when actual weight changes
		self.actual_weight_var.trace_add("write", self._on_actual_weight_changed)

	def _build_menu(self) -> None:
		menu_bar = tk.Menu(self.root)
		file_menu = tk.Menu(menu_bar, tearoff=0)
		file_menu.add_command(label="New", command=self.new_stock)
		file_menu.add_command(label="Open...", command=self.open_stock)
		file_menu.add_command(label="Save", command=self.save_stock)
		file_menu.add_command(label="Save As...", command=self.save_stock_as)
		file_menu.add_separator()
		file_menu.add_command(label="Exit", command=self.root.quit)
		menu_bar.add_cascade(label="File", menu=file_menu)
		self.root.config(menu=menu_bar)

	def _build_layout(self) -> None:
		container = ttk.Frame(self.root, padding=10)
		container.pack(fill=tk.BOTH, expand=True)

		table_frame = ttk.Frame(container)
		table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		columns = (
			"id",
			"brand",
			"material",
			"name",
			"color",
			"price",
			"buying_date",
			"original_weight",
			"status",
			"remaining_weight",
		)
		self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
		self.tree.heading("id", text="ID")
		self.tree.heading("brand", text="Brand")
		self.tree.heading("material", text="Material")
		self.tree.heading("name", text="Name")
		self.tree.heading("color", text="Color")
		self.tree.heading("price", text="Price")
		self.tree.heading("buying_date", text="Buying Date")
		self.tree.heading("original_weight", text="Original Weight (g)")
		self.tree.heading("status", text="Status")
		self.tree.heading("remaining_weight", text="Remaining Weight (g)")

		self.tree.column("id", width=80, anchor=tk.W)
		self.tree.column("brand", width=100, anchor=tk.W)
		self.tree.column("material", width=80, anchor=tk.W)
		self.tree.column("name", width=120, anchor=tk.W)
		self.tree.column("color", width=80, anchor=tk.W)
		self.tree.column("price", width=70, anchor=tk.E)
		self.tree.column("buying_date", width=100, anchor=tk.CENTER)
		self.tree.column("original_weight", width=130, anchor=tk.E)
		self.tree.column("status", width=70, anchor=tk.CENTER)
		self.tree.column("remaining_weight", width=130, anchor=tk.E)

		scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
		self.tree.configure(yscroll=scrollbar.set)
		self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

		form = ttk.LabelFrame(container, text="Spool", padding=10)
		form.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

		# Brand combobox
		ttk.Label(form, text="Brand").grid(row=0, column=0, sticky=tk.W, pady=4)
		self.brand_combo = ttk.Combobox(form, textvariable=self.brand_var, width=22)
		self.brand_combo.grid(row=0, column=1, sticky=tk.W, pady=4)
		self.brand_combo.bind("<<ComboboxSelected>>", self._on_combo_changed)

		# Material combobox
		ttk.Label(form, text="Material").grid(row=1, column=0, sticky=tk.W, pady=4)
		self.material_combo = ttk.Combobox(form, textvariable=self.material_var, width=22)
		self.material_combo.grid(row=1, column=1, sticky=tk.W, pady=4)
		self.material_combo.bind("<<ComboboxSelected>>", self._on_combo_changed)

		self._add_labeled_entry(form, "Name", self.name_var, 2)

		# Color combobox
		ttk.Label(form, text="Color").grid(row=3, column=0, sticky=tk.W, pady=4)
		self.color_combo = ttk.Combobox(form, textvariable=self.color_var, width=22)
		self.color_combo.grid(row=3, column=1, sticky=tk.W, pady=4)
		self.color_combo.bind("<<ComboboxSelected>>", self._on_combo_changed)

		self._add_labeled_entry(form, "Price", self.price_var, 4)
		self._add_labeled_entry(form, "Buying date (YYYY-MM-DD)", self.buying_date_var, 5)

		# Original weight combobox (250g or 1kg)
		ttk.Label(form, text="Original weight (g)").grid(row=6, column=0, sticky=tk.W, pady=4)
		self.weight_combo = ttk.Combobox(form, textvariable=self.original_weight_var, width=22, values=["1000", "250"])
		self.weight_combo.grid(row=6, column=1, sticky=tk.W, pady=4)
		self.weight_combo.bind("<<ComboboxSelected>>", self._on_combo_changed)

		# Actual weight (total including spool holder)
		self._add_labeled_entry(form, "Actual weight (g)", self.actual_weight_var, 7)

		# Initialize combobox values and prefill with first values
		self._update_combobox_values()
		self._prefill_dropdowns()

		status_label = ttk.Label(form, text="Status")
		status_label.grid(row=8, column=0, sticky=tk.W, pady=(8, 4))
		status_frame = ttk.Frame(form)
		status_frame.grid(row=8, column=1, sticky=tk.W)
		ttk.Radiobutton(
			status_frame,
			text="New",
			variable=self.status_var,
			value="new",
			command=self._toggle_remaining_field,
		).pack(side=tk.LEFT)
		ttk.Radiobutton(
			status_frame,
			text="Opened",
			variable=self.status_var,
			value="opened",
			command=self._toggle_remaining_field,
		).pack(side=tk.LEFT, padx=(10, 0))

		remaining_label = ttk.Label(form, text="Remaining weight (g)")
		remaining_label.grid(row=9, column=0, sticky=tk.W, pady=4)
		self.remaining_entry = ttk.Entry(form, textvariable=self.remaining_weight_var, width=24)
		self.remaining_entry.grid(row=9, column=1, sticky=tk.W, pady=4)

		button_frame = ttk.Frame(form)
		button_frame.grid(row=10, column=0, columnspan=2, sticky=tk.EW, pady=(12, 0))
		ttk.Button(button_frame, text="Add", command=self.add_spool).pack(fill=tk.X)
		ttk.Button(button_frame, text="Update", command=self.update_spool).pack(fill=tk.X, pady=6)
		ttk.Button(button_frame, text="Delete", command=self.delete_spool).pack(fill=tk.X)
		ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(fill=tk.X, pady=(6, 0))

		self._toggle_remaining_field()

	def _add_labeled_entry(self, parent: ttk.Frame, label: str, variable: tk.StringVar, row: int) -> None:
		ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, pady=4)
		ttk.Entry(parent, textvariable=variable, width=24).grid(row=row, column=1, sticky=tk.W, pady=4)

	def _get_sorted_values_by_occurrence(self, field_name: str, defaults: list[str]) -> list[str]:
		"""Get sorted list of values by occurrence in stock, with defaults at the end if not present."""
		from collections import Counter

		# Count occurrences in existing spools
		if field_name == "brand":
			values = [spool.brand for spool in self.spools if spool.brand]
		elif field_name == "material":
			values = [spool.material for spool in self.spools if spool.material]
		elif field_name == "color":
			values = [spool.color for spool in self.spools if spool.color]
		else:
			return defaults

		counter = Counter(values)

		# Get unique values sorted by occurrence (most common first)
		sorted_values = [value for value, count in counter.most_common()]

		# Add defaults that are not already in the list
		for default in defaults:
			if default not in sorted_values:
				sorted_values.append(default)

		return sorted_values

	def _update_combobox_values(self) -> None:
		"""Update combobox dropdown values based on current stock and defaults."""
		# Update brand combobox
		brand_values = self._get_sorted_values_by_occurrence("brand", self.default_brands)
		self.brand_combo['values'] = brand_values

		# Update material combobox
		material_values = self._get_sorted_values_by_occurrence("material", self.default_materials)
		self.material_combo['values'] = material_values

		# Update color combobox
		color_values = self._get_sorted_values_by_occurrence("color", self.default_colors)
		self.color_combo['values'] = color_values

	def _prefill_dropdowns(self) -> None:
		"""Prefill dropdown menus with first values from their lists."""
		if self.brand_combo['values'] and not self.brand_var.get():
			self.brand_var.set(self.brand_combo['values'][0])

		if self.material_combo['values'] and not self.material_var.get():
			self.material_var.set(self.material_combo['values'][0])

		if self.color_combo['values'] and not self.color_var.get():
			self.color_var.set(self.color_combo['values'][0])

		if not self.original_weight_var.get():
			self.original_weight_var.set("1000")  # Default to 1kg

	def _on_combo_changed(self, event=None) -> None:
		"""Called when a combobox selection changes. Check for matching price."""
		brand = self.brand_var.get().strip()
		material = self.material_var.get().strip()
		color = self.color_var.get().strip()
		weight_str = self.original_weight_var.get().strip()

		if not all([brand, material, color, weight_str]):
			return  # Not all fields filled yet

		try:
			weight = float(weight_str)
		except ValueError:
			return

		# Find the last spool with matching brand/material/color/weight
		matching_spools = [
			spool for spool in reversed(self.spools)
			if (spool.brand == brand and 
			    spool.material == material and 
			    spool.color == color and 
			    spool.original_weight == weight)
		]

		if matching_spools:
			last_spool = matching_spools[0]
			# Only update price if it's empty or different
			current_price = self.price_var.get().strip()
			if not current_price or current_price != str(last_spool.price):
				self.price_var.set(str(last_spool.price))

	def _toggle_remaining_field(self) -> None:
		is_opened = self.status_var.get() == "opened"
		if is_opened:
			self.remaining_entry.configure(state="normal")
		else:
			self.remaining_weight_var.set("")
			self.remaining_entry.configure(state="disabled")

	def _on_actual_weight_changed(self, *args) -> None:
		"""Auto-calculate remaining weight when actual weight changes for opened spools."""
		# Only auto-calculate if we're editing an existing spool and it's opened
		if not self.current_id or self.status_var.get() != "opened":
			return
		
		actual_weight_str = self.actual_weight_var.get().strip()
		if not actual_weight_str:
			return
		
		try:
			actual_weight = float(actual_weight_str)
		except ValueError:
			return
		
		# Get the spool holder weight from the currently selected spool
		if self.selected_index is not None and self.selected_index < len(self.spools):
			spool = self.spools[self.selected_index]
			if spool.spool_holder_weight > 0:
				# Calculate remaining = actual_weight - spool_holder_weight
				remaining = actual_weight - spool.spool_holder_weight
				if remaining >= 0:
					self.remaining_weight_var.set(f"{remaining:.1f}")

	def _generate_human_readable_id(self, material: str, color: str) -> str:
		"""Generate a human-readable ID in format MATERIAL-COLOR-NNN."""
		material_clean = material.upper().replace(" ", "-")
		color_clean = color.upper().replace(" ", "-")
		prefix = f"{material_clean}-{color_clean}-"
		
		# Find highest number for this material-color combination in existing spools
		max_num = 0
		for spool in self.spools:
			if spool.id.startswith(prefix):
				try:
					num_str = spool.id[len(prefix):]
					num = int(num_str)
					max_num = max(max_num, num)
				except ValueError:
					continue
		
		next_num = max_num + 1
		return f"{prefix}{next_num:03d}"

	def _generate_barcode(self, spool: FilamentSpool) -> None:
		"""Generate barcode PNG for a spool in the barcodes subfolder."""
		if barcode_lib is None or ImageWriter is None:
			return  # Silently skip if barcode library not available

		try:
			# Get the directory where the current file is located, or workspace root
			if self.current_file:
				base_dir = self.current_file.parent
			else:
				base_dir = Path.cwd()

			barcode_dir = base_dir / "barcodes"
			barcode_dir.mkdir(exist_ok=True)

			# Use the ID directly as the filename (it's already human-readable)
			# Generate CODE128 barcode (content is the human-readable ID)
			code128 = barcode_lib.get_barcode_class("code128")
			barcode_instance = code128(spool.id, writer=ImageWriter())
			
			# Save as PNG (extension added automatically by library)
			output_path = barcode_dir / spool.id
			barcode_instance.save(str(output_path))
		except Exception as e:
			# Don't stop execution if barcode generation fails
			print(f"Warning: Could not generate barcode for {spool.id}: {e}")

	def _read_form(self) -> FilamentSpool | None:
		brand = self.brand_var.get().strip()
		material = self.material_var.get().strip()
		name = self.name_var.get().strip()
		color = self.color_var.get().strip()
		original_raw = self.original_weight_var.get().strip()
		actual_raw = self.actual_weight_var.get().strip()
		is_opened = self.status_var.get() == "opened"
		remaining_raw = self.remaining_weight_var.get().strip()
		price_raw = self.price_var.get().strip()
		buying_date = self.buying_date_var.get().strip()

		if not all([brand, material, name, color, original_raw, price_raw, buying_date]):
			messagebox.showerror("Invalid data", "Please fill all fields except remaining weight for new spools.")
			return None

		try:
			original_weight = float(original_raw)
		except ValueError:
			messagebox.showerror("Invalid data", "Original weight must be a number.")
			return None

		if original_weight < 0:
			messagebox.showerror("Invalid data", "Original weight must be zero or positive.")
			return None

		try:
			price = float(price_raw)
		except ValueError:
			messagebox.showerror("Invalid data", "Price must be a number.")
			return None

		if price < 0:
			messagebox.showerror("Invalid data", "Price must be zero or positive.")
			return None

		# Parse actual weight
		actual_weight = 0.0
		if actual_raw:
			try:
				actual_weight = float(actual_raw)
			except ValueError:
				messagebox.showerror("Invalid data", "Actual weight must be a number.")
				return None

			if actual_weight < 0:
				messagebox.showerror("Invalid data", "Actual weight must be zero or positive.")
				return None

		remaining_weight: float | None = None
		if is_opened:
			if not remaining_raw:
				messagebox.showerror("Invalid data", "Remaining weight is required for opened spools.")
				return None
			try:
				remaining_weight = float(remaining_raw)
			except ValueError:
				messagebox.showerror("Invalid data", "Remaining weight must be a number.")
				return None

			if remaining_weight < 0:
				messagebox.showerror("Invalid data", "Remaining weight must be zero or positive.")
				return None

			if remaining_weight > original_weight:
				messagebox.showerror(
					"Invalid data",
					"Remaining weight cannot be greater than original weight.",
				)
				return None
		else:
			# For new spools, set remaining weight equal to original weight (full spool)
			remaining_weight = original_weight

		# Use existing ID if in edit mode, or generate new human-readable one
		spool_id = self.current_id if self.current_id else self._generate_human_readable_id(material, color)

		# Calculate spool holder weight
		spool_holder_weight = 0.0
		if self.current_id:
			# Editing existing spool - preserve or recalculate
			existing_spool = self.spools[self.selected_index] if self.selected_index is not None else None
			if existing_spool:
				spool_holder_weight = existing_spool.spool_holder_weight
				# If updating with remaining weight, recalculate original_weight
				if is_opened and remaining_weight is not None and actual_weight > 0:
					# original_weight = actual_weight - spool_holder_weight
					original_weight = actual_weight - spool_holder_weight
		else:
			# New spool - calculate from actual and original/remaining
			if actual_weight > 0:
				if is_opened and remaining_weight is not None:
					# For new opened spools, calculate holder from actual - remaining
					spool_holder_weight = actual_weight - remaining_weight
				else:
					# For new unopened spools, calculate holder from actual - original
					spool_holder_weight = actual_weight - original_weight
				
				if spool_holder_weight < 0:
					messagebox.showerror(
						"Invalid data",
						"Actual weight cannot be less than filament weight.",
					)
					return None

		return FilamentSpool(
			id=spool_id,
			brand=brand,
			material=material,
			name=name,
			color=color,
			original_weight=original_weight,
			is_opened=is_opened,
			remaining_weight=remaining_weight,
			price=price,
			buying_date=buying_date,
			created_at=datetime.now().isoformat() if not self.current_id else "",
			updated_at=datetime.now().isoformat(),
			barcode=spool_id,
			actual_weight=actual_weight,
			spool_holder_weight=spool_holder_weight,
		)

	def _render_tree(self) -> None:
		for item in self.tree.get_children():
			self.tree.delete(item)

		for index, spool in enumerate(self.spools):
			status_text = "Opened" if spool.is_opened else "New"
			remaining_text = (
				f"{spool.remaining_weight:.1f}" if spool.remaining_weight is not None else "-"
			)
			short_id = spool.id[:8] if len(spool.id) > 8 else spool.id
			self.tree.insert(
				"",
				tk.END,
				iid=str(index),
				values=(
					short_id,
					spool.brand,
					spool.material,
					spool.name,
					spool.color,
					f"{spool.price:.2f}",
					spool.buying_date,
				f"{spool.original_weight:.1f}",
					status_text,
					remaining_text,
				),
			)

	def add_spool(self) -> None:
		spool = self._read_form()
		if spool is None:
			return
		# Set creation timestamp for new spools
		if not spool.created_at:
			spool.created_at = datetime.now().isoformat()
		self.spools.append(spool)
		self._generate_barcode(spool)
		self._update_combobox_values()
		self._render_tree()
		self.clear_form()

	def update_spool(self) -> None:
		if self.selected_index is None:
			messagebox.showinfo("No selection", "Please select a spool to update.")
			return

		spool = self._read_form()
		if spool is None:
			return
		# Preserve creation timestamp from original spool
		original_spool = self.spools[self.selected_index]
		spool.created_at = original_spool.created_at
		self.spools[self.selected_index] = spool
		self._generate_barcode(spool)
		self._update_combobox_values()
		self._render_tree()
		self.tree.selection_set(str(self.selected_index))

	def delete_spool(self) -> None:
		if self.selected_index is None:
			messagebox.showinfo("No selection", "Please select a spool to delete.")
			return
		del self.spools[self.selected_index]
		self.selected_index = None
		self._update_combobox_values()
		self._render_tree()
		self.clear_form()

	def clear_form(self) -> None:
		self.brand_var.set("")
		self.material_var.set("")
		self.name_var.set("")
		self.color_var.set("")
		self.original_weight_var.set("")
		self.actual_weight_var.set("")
		self.remaining_weight_var.set("")
		self.status_var.set("new")
		self.price_var.set("")
		# Set buying date to today by default
		self.buying_date_var.set(datetime.now().strftime("%Y-%m-%d"))
		self.selected_index = None
		self.current_id = None
		self.tree.selection_remove(*self.tree.selection())
		self._toggle_remaining_field()
		self._prefill_dropdowns()  # Refill with defaults

	def on_tree_select(self, _: tk.Event) -> None:
		selected_items = self.tree.selection()
		if not selected_items:
			return

		index = int(selected_items[0])
		if index < 0 or index >= len(self.spools):
			return

		spool = self.spools[index]
		self.selected_index = index
		self.current_id = spool.id

		self.brand_var.set(spool.brand)
		self.material_var.set(spool.material)
		self.name_var.set(spool.name)
		self.color_var.set(spool.color)
		self.original_weight_var.set(str(spool.original_weight))
		self.actual_weight_var.set(str(spool.actual_weight) if spool.actual_weight else "")
		# Auto-set to "opened" when selecting for update
		self.status_var.set("opened")
		self.remaining_weight_var.set(
			"" if spool.remaining_weight is None else str(spool.remaining_weight)
		)
		self.price_var.set(str(spool.price))
		self.buying_date_var.set(spool.buying_date)
		self._toggle_remaining_field()

	def _serialize(self) -> list[dict]:
		return [spool.to_dict() for spool in self.spools]

	def _deserialize(self, payload: list[dict]) -> None:
		spools: list[FilamentSpool] = []
		for item in payload:
			if not isinstance(item, dict):
				continue
			spools.append(FilamentSpool.from_dict(item))
		self.spools = spools
		self.selected_index = None
		# Regenerate all barcodes after loading
		for spool in self.spools:
			self._generate_barcode(spool)
		self._update_combobox_values()
		self._render_tree()
		self.clear_form()

	def _load_from_path(self, file_path: Path) -> None:
		suffix = file_path.suffix.lower()
		if suffix == ".json":
			with file_path.open("r", encoding="utf-8") as file:
				payload = json.load(file)
		elif suffix in {".yaml", ".yml"}:
			if yaml is None:
				messagebox.showerror(
					"YAML unavailable",
					"PyYAML is not installed. Install it with: pip install pyyaml",
				)
				return
			with file_path.open("r", encoding="utf-8") as file:
				payload = yaml.safe_load(file) or []
		else:
			messagebox.showerror("Unsupported file", "Use .json, .yaml or .yml files.")
			return

		if not isinstance(payload, list):
			messagebox.showerror("Invalid file", "Data must be a list of spools.")
			return

		self._deserialize(payload)
		self.current_file = file_path
		self.root.title(f"Filament Stock Manager - {file_path.name}")

	def _save_to_path(self, file_path: Path) -> bool:
		suffix = file_path.suffix.lower()
		data = self._serialize()

		try:
			if suffix == ".json":
				with file_path.open("w", encoding="utf-8") as file:
					json.dump(data, file, indent=2)
			elif suffix in {".yaml", ".yml"}:
				if yaml is None:
					messagebox.showerror(
						"YAML unavailable",
						"PyYAML is not installed. Install it with: pip install pyyaml",
					)
					return False
				with file_path.open("w", encoding="utf-8") as file:
					yaml.safe_dump(data, file, sort_keys=False)
			else:
				messagebox.showerror("Unsupported file", "Use .json, .yaml or .yml files.")
				return False
		except Exception as exc:
			messagebox.showerror("Save error", f"Unable to save file: {exc}")
			return False

		self.current_file = file_path
		self.root.title(f"Filament Stock Manager - {file_path.name}")
		return True

	def new_stock(self) -> None:
		self.spools = []
		self.current_file = None
		self.selected_index = None
		self._update_combobox_values()
		self._render_tree()
		self.clear_form()
		self.root.title("Filament Stock Manager")

	def open_stock(self) -> None:
		file_name = filedialog.askopenfilename(
			title="Open stock file",
			filetypes=[
				("Stock Files", "*.json *.yaml *.yml"),
				("JSON Files", "*.json"),
				("YAML Files", "*.yaml *.yml"),
				("All Files", "*.*"),
			],
		)
		if not file_name:
			return

		try:
			self._load_from_path(Path(file_name))
		except Exception as exc:
			messagebox.showerror("Open error", f"Unable to open file: {exc}")

	def save_stock(self) -> None:
		if self.current_file is None:
			self.save_stock_as()
			return
		self._save_to_path(self.current_file)

	def save_stock_as(self) -> None:
		file_name = filedialog.asksaveasfilename(
			title="Save stock file",
			defaultextension=".json",
			filetypes=[
				("JSON Files", "*.json"),
				("YAML Files", "*.yaml"),
				("YAML Files", "*.yml"),
				("All Files", "*.*"),
			],
		)
		if not file_name:
			return
		self._save_to_path(Path(file_name))


def main() -> None:
	root = tk.Tk()
	FilamentStockApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()
