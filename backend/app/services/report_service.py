from app.models import ListingResult

def html_report_bytes(title_text: str, inputs: dict, draft: ListingResult, final_: ListingResult) -> str:
    style = """
    <style>
      :root {
        --ink: #111827;
        --muted: #6b7280;
        --accent: #4c1d95;
        --accent-soft: #ede9fe;
        --bg: linear-gradient(135deg, #f8fafc 0%, #eef2ff 50%, #f4fce3 100%);
        --border: #e5e7eb;
      }
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body {
        margin: 0;
        font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.6;
        color: var(--ink);
        background: var(--bg);
        padding: 40px 20px;
        min-height: 100vh;
      }
      .report-shell {
        max-width: 1100px;
        margin: 0 auto;
        background: #fff;
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(15,23,42,0.1), 0 0 0 1px rgba(15,23,42,0.05);
        overflow: hidden;
      }
      header {
        padding: 40px 48px;
        background: radial-gradient(circle at top right, rgba(124,58,237,.08), transparent 60%), #fff;
        border-bottom: 2px solid #f3f4f6;
      }
      .brand-tag {
        display: inline-block;
        padding: 6px 16px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 16px;
        text-transform: uppercase;
      }
      .title { 
        font-size: 36px; 
        font-weight: 800; 
        margin: 0 0 12px; 
        color: var(--accent);
        letter-spacing: -0.5px;
      }
      .tagline { 
        margin: 0 0 20px; 
        color: var(--muted); 
        font-size: 17px;
        line-height: 1.5;
      }
      .badges { 
        display: flex; 
        flex-wrap: wrap; 
        gap: 12px; 
        margin-top: 20px;
      }
      .badge {
        padding: 8px 18px;
        border-radius: 999px;
        border: 1.5px solid rgba(76,29,149,0.2);
        background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
        color: var(--accent);
        font-weight: 600;
        font-size: 13px;
      }
      section { 
        padding: 40px 48px; 
        border-bottom: 2px solid #f9fafb; 
      }
      section:last-child { border-bottom: none; }
      .section-title { 
        font-size: 22px; 
        font-weight: 700; 
        margin-bottom: 24px; 
        color: var(--ink);
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .section-title::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        border-radius: 999px;
      }
      .content-table { 
        width: 100%; 
        border-collapse: separate; 
        border-spacing: 0;
      }
      .content-table td { 
        padding: 20px 24px; 
        border-bottom: 1px solid #f3f4f6; 
        vertical-align: top;
      }
      .content-table tr:last-child td { border-bottom: none; }
      .content-table td:first-child { 
        width: 240px; 
        font-weight: 700; 
        color: var(--muted);
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
      .content-table td:last-child {
        color: var(--ink);
        font-size: 15px;
        word-wrap: break-word;
        word-break: break-word;
        overflow-wrap: break-word;
      }
      .text-content {
        white-space: pre-wrap;
        word-wrap: break-word;
        word-break: break-word;
        overflow-wrap: break-word;
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        background: #f8fafc;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        font-size: 14px;
        line-height: 1.7;
        max-width: 100%;
        overflow-x: auto;
      }
      .code-content {
        white-space: pre-wrap;
        word-wrap: break-word;
        word-break: break-word;
        overflow-wrap: break-word;
        font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, monospace;
        background: #1e293b;
        color: #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        font-size: 13px;
        line-height: 1.8;
        max-width: 100%;
        overflow-x: auto;
      }
      .chip-group { 
        display: flex; 
        flex-wrap: wrap; 
        gap: 10px;
        margin: 4px 0;
      }
      .chip {
        padding: 8px 16px;
        border-radius: 999px;
        background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
        border: 1px solid #bae6fd;
        font-size: 13px;
        font-weight: 600;
        color: #0c4a6e;
        display: inline-block;
      }
      .link-content {
        color: #2563eb;
        text-decoration: none;
        word-break: break-all;
      }
      .link-content:hover {
        text-decoration: underline;
      }
      .empty-state {
        color: var(--muted);
        font-style: italic;
        padding: 12px;
        background: #f9fafb;
        border-radius: 8px;
        text-align: center;
      }
      @media print {
        body { padding: 0; background: white; }
        .report-shell { box-shadow: none; border-radius: 0; }
        section { page-break-inside: avoid; }
      }
      @media (max-width: 768px) {
        body { padding: 20px 12px; }
        header, section { padding: 28px 24px; }
        .title { font-size: 28px; }
        .section-title { font-size: 18px; }
        .content-table td:first-child { 
          width: 140px;
          font-size: 12px;
        }
        .content-table td { padding: 16px; }
        .text-content, .code-content { padding: 16px; font-size: 13px; }
      }
      @media (max-width: 480px) {
        .content-table td:first-child {
          display: block;
          width: 100%;
          padding-bottom: 8px;
          border-bottom: none;
        }
        .content-table td:last-child {
          display: block;
          width: 100%;
          padding-top: 8px;
        }
      }
    </style>
    """

    def kv(label, value):
        if not value or value == '—':
            value = "<div class='empty-state'>No data provided</div>"
        return f"<tr><td>{label}</td><td>{value}</td></tr>"

    def safe_text(text):
        """Safely escape and format text content"""
        if not text or text == '—':
            return "<div class='empty-state'>No data provided</div>"
        return f"<div class='text-content'>{text}</div>"
    
    def safe_code(text):
        """Safely escape and format code/HTML content"""
        if not text or text == '—':
            return "<div class='empty-state'>No data provided</div>"
        escaped = text.replace('<', '&lt;').replace('>', '&gt;')
        return f"<div class='code-content'>{escaped}</div>"
    
    def safe_link(url):
        """Format URL as clickable link"""
        if not url or url == '—':
            return "<div class='empty-state'>No link provided</div>"
        return f"<a href='{url}' target='_blank' class='link-content'>{url}</a>"

    draft_dict = draft.dict()
    final_dict = final_.dict()

    def chip_markup(values):
        if not values or len(values) == 0:
            return "<div class='empty-state'>No keywords available</div>"
        chips = ''.join(f"<span class='chip'>{v}</span>" for v in values)
        return f"<div class='chip-group'>{chips}</div>"

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title_text}</title>
  {style}
</head>
<body>
  <div class="report-shell">
    <header>
      <div class="brand-tag">Ikshan Intelligence</div>
      <h1 class="title">{title_text}</h1>
      <p class="tagline">Shakti — your new frontier to the next-gen optimization. Powered by advanced AI models and enterprise-grade SEO intelligence.</p>
      <div class="badges">
        <span class="badge">Shakti 1.2</span>
        <span class="badge">Next-gen AI Workflow</span>
        <span class="badge">Ikshan Intelligence Lab</span>
      </div>
    </header>

    <section>
      <div class="section-title">Inputs</div>
      <table class="content-table">
        {kv("Previous Title", safe_text(inputs.get('prev_title')))}
        {kv("Previous Description", safe_text(inputs.get('prev_desc')))}
        {kv("Product Link", safe_link(inputs.get('product_link')))}
      </table>
    </section>

    <section>
      <div class="section-title">Draft · Level 1 System Flow</div>
      <table class="content-table">
        {kv("Optimized Title", safe_text(draft_dict.get('new_title')))}
        {kv("Description (HTML)", safe_code(draft_dict.get('new_description')))}
        {kv("Short-tail Keywords", chip_markup(draft_dict.get('keywords_short')))}
        {kv("Mid-tail Keywords", chip_markup(draft_dict.get('keywords_mid')))}
        {kv("Long-tail Keywords", chip_markup(draft_dict.get('keywords_long')))}
      </table>
    </section>

    <section>
      <div class="section-title">Final · Level 2 QA+</div>
      <table class="content-table">
        {kv("Optimized Title", safe_text(final_dict.get('new_title')))}
        {kv("Description (HTML)", safe_code(final_dict.get('new_description')))}
        {kv("Short-tail Keywords", chip_markup(final_dict.get('keywords_short')))}
        {kv("Mid-tail Keywords", chip_markup(final_dict.get('keywords_mid')))}
        {kv("Long-tail Keywords", chip_markup(final_dict.get('keywords_long')))}
      </table>
    </section>
    
    <section style="background: #f9fafb; text-align: center; padding: 32px;">
      <p style="color: var(--muted); font-size: 13px; margin: 0;">
        Generated by <strong style="color: var(--accent);">Shakti 1.2</strong> • 
        Ikshan Intelligence Lab • 
        © {__import__('datetime').datetime.now().year}
      </p>
    </section>
  </div>
</body>
</html>"""
    return html
