# How to Load `radio_host_functions.py` in Google Colab

## Quick Reference: All Methods

### Method 1: Upload File Directly (Simplest) ⭐ Recommended for Quick Testing

**Step 1:** Add a new cell at the beginning of your notebook:

```python
from google.colab import files
import os

# Check if file already exists (to avoid re-uploading)
if not os.path.exists("/content/radio_host_functions.py"):
    uploaded = files.upload()  # This will show a file picker
    # Select radio_host_functions.py from your computer
    for filename in uploaded.keys():
        print(f"✅ Uploaded: {filename}")
else:
    print("✅ radio_host_functions.py already exists")
```

**Step 2:** After uploading, import the module:

```python
import sys
sys.path.append('/content')  # Add /content to Python path

from radio_host_functions import (
    CONFIG,
    fetch_wikipedia_article,
    generate_script_prompt,
    generate_script,
    clean_for_tts,
    generate_audio_segments,
    combine_and_export_audio
)
```

---

### Method 2: Mount Google Drive (Best for Persistent Storage) ⭐ Recommended for Regular Use

**Step 1:** Mount your Google Drive:

```python
from google.colab import drive
drive.mount('/content/drive')
```

**Step 2:** Copy the file to working directory (if it's in Drive):

```python
import os
if not os.path.exists("/content/radio_host_functions.py"):
    !cp /content/drive/MyDrive/path/to/radio_host_functions.py /content/
    print("✅ File copied from Drive")
else:
    print("✅ File already exists")
```

**Step 3:** Import the module:

```python
import sys
sys.path.append('/content')

from radio_host_functions import (
    CONFIG,
    fetch_wikipedia_article,
    generate_script_prompt,
    generate_script,
    clean_for_tts,
    generate_audio_segments,
    combine_and_export_audio
)
```

**Alternative:** Add Drive folder directly to path:

```python
import sys
sys.path.append('/content/drive/MyDrive/path/to/')

from radio_host_functions import (
    CONFIG,
    fetch_wikipedia_article,
    # ... etc
)
```

---

### Method 3: Clone from GitHub (Best for Version Control) ⭐ Recommended for Production

**Step 1:** Clone the repository:

```python
!git clone https://github.com/yourusername/synthetic_radio_host.git /content/synthetic_radio_host
```

**Step 2:** Add to Python path and import:

```python
import sys
sys.path.append('/content/synthetic_radio_host')

from radio_host_functions import (
    CONFIG,
    fetch_wikipedia_article,
    generate_script_prompt,
    generate_script,
    clean_for_tts,
    generate_audio_segments,
    combine_and_export_audio
)
```

---

### Method 4: Write File Directly (Paste Code)

**Not recommended for large files, but works:**

```python
%%writefile /content/radio_host_functions.py
"""
Synthetic Radio Host Generator - Core Functions
"""
import os
import re
import io
# ... paste entire file content here ...
```

Then import normally:

```python
import sys
sys.path.append('/content')
from radio_host_functions import *
```

---

## Complete Example: Updated Notebook Structure

After loading the module, your notebook should look like this:

```python
# Cell 1: Upload module (Method 1)
from google.colab import files
if not os.path.exists("/content/radio_host_functions.py"):
    files.upload()

# Cell 2: Import module
import sys
sys.path.append('/content')
from radio_host_functions import (
    CONFIG,
    fetch_wikipedia_article,
    generate_script_prompt,
    generate_script,
    generate_audio_segments,
    combine_and_export_audio
)

# Cell 3: Setup API clients
from openai import OpenAI
from elevenlabs import ElevenLabs
from google.colab import userdata, files

OPENAI_API_KEY = userdata.get("OPENAI_API_KEY")
ELEVENLABS_API_KEY = userdata.get("ELEVENLABS_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Cell 4: Use the functions (note: pass clients as parameters)
wiki_text = fetch_wikipedia_article("MS Dhoni")
prompt = generate_script_prompt(wiki_text)
script = generate_script(prompt, openai_client)  # ✅ Pass client
segments = generate_audio_segments(script, eleven_client)  # ✅ Pass client
combine_and_export_audio(segments, CONFIG["OUTPUT_FILENAME"], files_download=files.download)  # ✅ Pass download function
```

---

## Key Differences When Using Imported Module

### ❌ Old Way (Notebook with duplicated code):
```python
# Functions use global variables
script = generate_script(prompt)  # Uses global openai_client
segments = generate_audio_segments(script)  # Uses global eleven_client
```

### ✅ New Way (Using imported module):
```python
# Functions require explicit parameters
script = generate_script(prompt, openai_client)  # Pass client explicitly
segments = generate_audio_segments(script, eleven_client)  # Pass client explicitly
combine_and_export_audio(segments, filename, files_download=files.download)  # Pass download function
```

---

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'radio_host_functions'`

**Solution:**
1. Check file exists: `!ls /content/radio_host_functions.py`
2. Verify path: `import sys; print(sys.path)`
3. Try: `sys.path.insert(0, '/content')`

### Error: `ImportError: cannot import name 'CONFIG'`

**Solution:**
- Make sure the file uploaded completely
- Check file size: `!ls -lh /content/radio_host_functions.py`
- Re-upload the file

### Error: Functions don't work (missing global variables)

**Solution:**
- The imported functions require explicit parameters
- Pass `openai_client` and `eleven_client` as arguments
- Pass `files_download=files.download` for download functionality

---

## Recommended Workflow

1. **First time setup:** Use Method 1 (Upload file directly)
2. **Regular use:** Use Method 2 (Mount Google Drive)
3. **Team collaboration:** Use Method 3 (GitHub clone)
4. **Quick testing:** Use Method 4 (Write file directly)

---

## Benefits of Using Imported Module

✅ **Single source of truth** - Code lives in one place  
✅ **Test coverage** - All 92% tested code is used  
✅ **No duplication** - Changes only needed in one file  
✅ **Version control** - Module is tracked in Git  
✅ **Maintainability** - Easier to update and fix bugs  

