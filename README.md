Skip to content
Navigation Menu
brettgildner
TechnicianToolkit

Type / to search
Code
Issues
2
Pull requests
Actions
Projects
Security
Insights
Settings
Files
Go to file
t
assets
core
ui
.gitignore
LICENSE
README.md
TechnicalDocumentation.md
app.py
main.py
requirements.txt
TechnicianToolkit
/
README.md
in
master

Edit

Preview
Indent mode

Spaces
Indent size

2
Line wrap mode

Soft wrap
Editing README.md file contents
Selection deleted
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
143
144
145
146
147
148
149
150
151
152
153
154
155
156
157
158
159
160
161
162
163
164
165
166
167
168
169
170
171
172
173
174
175
176
177
178
179
180
181
182
183
184
185
186
187
188
189
190
191
192
193
194
195
196
197
198
199
200
201
202
203
204
205
206
207
208
209
210
211
212
213
214
215
216
217
218
219
220
221
222
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
---

## Running the App
```bash
python main.py
```
On first launch:
 - Database tables initialize automatically
 - Login window appears
 - Sidebar unlocks after authentication

---

## Project Structure
```css
TechnicianToolkit/
├── app.py
├── main.py
├── assets/
│   ├── Forms/
│   ├── icons/
│   └── images/
├── core/
│   ├── importers/
│   ├── models/
│   ├── logic.py
│   └── utils.py
├── data/
│   └── database.db
└── ui/
    ├── components/
    ├── forms/
    ├── pages/
    └── signals/
```
---

## Architecture
Technician Toolkit uses a hybrid MVC-style architecture with:
 - Models → SQLite-backed classes with CRUD methods
 - Views → PySide6 pages, dialogs, and widgets
 - Controllers → The `App` object, refresh orchestrator, and page router
 - Signal Bus → Centralized model signals to refresh UI automatically
 - Reusable Component Framework → Tables, delegates, popups, proxy models

---

## UI Framework
### Base Components
 - ```BaseTableModel``` — Data extraction, alignment, formatting
 - ```BaseTableView``` — Dark-themed, sortable table view
 - Action Buttons Delegates — Edit/Delete/Order in-table buttons
 - Filter Proxy Models — Custom filtering logic
 - Column Filter Popups — Column checkboxes & visibility
 - Dashboard Widgets — Aggregations + charts

### Forms
All CRUD dialogs use:
 - ```BaseDialogForm``` (except ```ExpenseEntryForm```)
 - Uniform layout
 - Validations
 - Model save + callback

### Pages
Each page wraps:
 - Toolbar | Table view | Filter logic | CRUD operations | Help dialog

---

## Database Models

Models include:
 - ```InventoryItem``` | ```ServiceActivity``` | ```EquipmentInfo``` | ```MileageEntry```
 - ```PartsOrder``` | ```ExpenseReportInfo``` | ```ExpenseLine``` | ```Category```

All models:
 - Auto-create tables
 - Validate columns on startup
 - Normalize string & numeric fields
 - Use user isolation where applicable

Automatic inventory sync occurs in the ServiceActivity model.

---

## Excel Import/Export
Importers

Located in `core/importers`
 - `equipment_importer.py`
 - `inventory_importer.py`
 - `sa_importer.py`

Exporters
 - Mileage export → Prestructured mileage form template
 - Expense report export → Excel form with line items

All use `openpyxl`.

---

## License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

Use Control + Shift + m to toggle the tab key moving focus. Alternatively, use esc then tab to move to the next interactive element on the page.
No file chosen
Attach files by dragging & dropping, selecting or pasting them.
