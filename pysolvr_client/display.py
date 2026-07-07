"""HTML rendering for notebook outputs - cards, tables, tabs, progress, errors."""
from IPython.display import HTML, display, clear_output


class Display:
    def __init__(self, primary_color: str = "#6366F1", accent_color: str = "#10B981"):
        self.primary = primary_color
        self.accent = accent_color
        self._styles = f"""
        <style>
        .pysolvr-card {{ background: #334155; border-radius: 8px; padding: 20px; margin: 8px 0; border: 1px solid #475569; font-family: Inter, system-ui, sans-serif; color: #f1f5f9; }}
        .pysolvr-card h3 {{ margin: 0 0 12px 0; font-size: 16px; font-weight: 500; }}
        .pysolvr-header {{ background: linear-gradient(135deg, {primary_color}22, {accent_color}22); border: 1px solid {primary_color}44; border-radius: 12px; padding: 24px; text-align: center; font-family: Inter, system-ui, sans-serif; color: #f1f5f9; }}
        .pysolvr-header h1 {{ margin: 0; font-size: 28px; font-weight: 300; }}
        .pysolvr-header p {{ margin: 8px 0 0; color: #94a3b8; font-size: 14px; }}
        .pysolvr-badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 500; }}
        .pysolvr-success {{ background: #10b98122; color: #10b981; }}
        .pysolvr-warning {{ background: #f59e0b22; color: #f59e0b; }}
        .pysolvr-error {{ background: #ef444422; color: #ef4444; }}
        .pysolvr-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        .pysolvr-table th {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid #475569; color: #94a3b8; font-weight: 500; }}
        .pysolvr-table td {{ padding: 8px 12px; border-bottom: 1px solid #47556944; }}
        .pysolvr-bar {{ height: 8px; border-radius: 4px; background: #1e293b; overflow: hidden; }}
        .pysolvr-bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s; }}
        .pysolvr-tabs {{ display: flex; gap: 0; border-bottom: 1px solid #475569; margin-bottom: 16px; }}
        .pysolvr-tab {{ padding: 8px 16px; cursor: pointer; color: #94a3b8; font-size: 13px; border-bottom: 2px solid transparent; }}
        .pysolvr-tab.active {{ color: #f1f5f9; border-bottom-color: {primary_color}; }}
        .pysolvr-tab-content {{ display: none; }}
        .pysolvr-tab-content.active {{ display: block; }}
        .pysolvr-cost {{ display: inline-flex; align-items: center; gap: 4px; font-size: 11px; color: #94a3b8; background: #1e293b; padding: 2px 8px; border-radius: 4px; }}
        </style>
        """

    def header(self, name: str, tagline: str, version: str):
        """Render business branding header."""
        html = f"""{self._styles}
        <div class="pysolvr-header">
            <h1>{name}</h1>
            <p>{tagline}</p>
            <p style="margin-top:12px"><span class="pysolvr-badge" style="background:{self.primary}22;color:{self.primary}">v{version}</span></p>
        </div>"""
        display(HTML(html))

    def card(self, title: str, content: str, status: str = None, actions: list = None):
        """Render a styled result card."""
        status_html = ""
        if status == "success":
            status_html = '<span class="pysolvr-badge pysolvr-success">Success</span>'
        elif status == "warning":
            status_html = '<span class="pysolvr-badge pysolvr-warning">Warning</span>'
        elif status == "error":
            status_html = '<span class="pysolvr-badge pysolvr-error">Error</span>'

        actions_html = ""
        if actions:
            actions_html = '<div style="margin-top:12px;display:flex;gap:8px">' + "".join(
                f'<span style="font-size:12px;color:{self.primary};cursor:pointer">{a}</span>' for a in actions
            ) + "</div>"

        html = f"""{self._styles}
        <div class="pysolvr-card">
            <h3>{title} {status_html}</h3>
            <div style="font-size:14px;line-height:1.6">{content}</div>
            {actions_html}
        </div>"""
        display(HTML(html))

    def table(self, data: list, columns: list = None):
        """Render a styled table from list of dicts."""
        if not data:
            self.card("No data", "Nothing to display yet.")
            return
        if not columns:
            columns = list(data[0].keys())
        header = "".join(f"<th>{c}</th>" for c in columns)
        rows = "".join(
            "<tr>" + "".join(f"<td>{row.get(c, '')}</td>" for c in columns) + "</tr>"
            for row in data
        )
        html = f"""{self._styles}
        <div class="pysolvr-card">
            <table class="pysolvr-table"><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table>
        </div>"""
        display(HTML(html))

    def progress(self, message: str = "Working..."):
        """Show a progress spinner (call clear_output() then result when done)."""
        html = f"""{self._styles}
        <div class="pysolvr-card" style="text-align:center">
            <div style="display:inline-block;width:20px;height:20px;border:2px solid #475569;border-top-color:{self.primary};border-radius:50%;animation:spin 0.8s linear infinite"></div>
            <p style="margin:8px 0 0;color:#94a3b8;font-size:13px">{message}</p>
        </div>
        <style>@keyframes spin{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}</style>"""
        display(HTML(html))

    def error(self, message: str, suggestion: str = None):
        """Render a friendly error card."""
        suggestion_html = f'<p style="margin-top:8px;font-size:12px;color:#94a3b8">Suggestion: {suggestion}</p>' if suggestion else ""
        html = f"""{self._styles}
        <div class="pysolvr-card" style="border-color:#ef444444">
            <h3><span class="pysolvr-badge pysolvr-error">Error</span></h3>
            <p style="font-size:14px">{message}</p>
            {suggestion_html}
        </div>"""
        display(HTML(html))

    def success(self, message: str, details: str = None):
        """Render a success card."""
        details_html = f'<p style="margin-top:8px;font-size:12px;color:#94a3b8">{details}</p>' if details else ""
        html = f"""{self._styles}
        <div class="pysolvr-card" style="border-color:#10b98144">
            <h3><span class="pysolvr-badge pysolvr-success">Done</span></h3>
            <p style="font-size:14px">{message}</p>
            {details_html}
        </div>"""
        display(HTML(html))

    def usage_bar(self, spent: float, limit: float, label: str = "Monthly usage"):
        """Render a usage progress bar."""
        pct = min((spent / limit) * 100, 100) if limit > 0 else 0
        color = self.accent if pct < 80 else ("#f59e0b" if pct < 95 else "#ef4444")
        html = f"""{self._styles}
        <div class="pysolvr-card">
            <h3>{label}</h3>
            <div style="display:flex;justify-content:space-between;font-size:12px;color:#94a3b8;margin-bottom:6px">
                <span>${spent:.2f} used</span><span>${limit:.2f} limit</span>
            </div>
            <div class="pysolvr-bar"><div class="pysolvr-bar-fill" style="width:{pct}%;background:{color}"></div></div>
            <p style="margin-top:6px;font-size:11px;color:#94a3b8">${limit-spent:.2f} remaining ({100-pct:.0f}%)</p>
        </div>"""
        display(HTML(html))

    def cost_badge(self, tokens: int, cost_usd: float):
        """Render an inline cost badge."""
        html = f'<span class="pysolvr-cost">{tokens:,} tokens | ${cost_usd:.4f}</span>'
        display(HTML(self._styles + html))

    def tabs(self, tab_dict: dict):
        """Render tabbed content. tab_dict = {label: html_content}."""
        import uuid
        uid = uuid.uuid4().hex[:8]
        tab_headers = ""
        tab_bodies = ""
        for i, (label, content) in enumerate(tab_dict.items()):
            active = " active" if i == 0 else ""
            tab_headers += f'<div class="pysolvr-tab{active}" onclick="document.querySelectorAll(\\'.pysolvr-tab-{uid}\\').forEach(e=>e.classList.remove(\\'active\\'));document.querySelectorAll(\\'.pysolvr-tc-{uid}\\').forEach(e=>e.classList.remove(\\'active\\'));this.classList.add(\\'active\\');document.getElementById(\\'tc-{uid}-{i}\\').classList.add(\\'active\\')">{label}</div>'
            tab_bodies += f'<div id="tc-{uid}-{i}" class="pysolvr-tc-{uid} pysolvr-tab-content{active}">{content}</div>'
        # Fix class on tabs for JS targeting
        tab_headers = tab_headers.replace('class="pysolvr-tab', f'class="pysolvr-tab pysolvr-tab-{uid}')
        html = f"""{self._styles}
        <div class="pysolvr-card">
            <div class="pysolvr-tabs">{tab_headers}</div>
            {tab_bodies}
        </div>"""
        display(HTML(html))
