"""
NovaRoma — Sistema de Gestão de Clientes
Desenvolvido por NovaRoma Soluções
"""

import sys
import os
import hashlib
import json
import html
import threading
import urllib.request
import urllib.error
import urllib.parse
import webbrowser
from datetime import datetime, date, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QStackedWidget, QTableWidget,
    QTableWidgetItem, QDialog, QFormLayout, QComboBox, QTextEdit,
    QFileDialog, QMessageBox, QFrame, QHeaderView, QListWidget,
    QListWidgetItem, QCheckBox, QAbstractItemView, QDateEdit,
    QSpinBox, QTimeEdit, QProgressBar, QScrollArea, QSizePolicy,
    QSplitter, QButtonGroup, QRadioButton, QGroupBox, QTabWidget,
    QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QTimer, QTime, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QTextDocument
from PyQt5.QtPrintSupport import QPrinter


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURAÇÕES
# ══════════════════════════════════════════════════════════════════════════════

SUPABASE_URL = "https://pjnzldzqoofgyvsxqbkc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBqbnpsZHpxb29mZ3l2c3hxYmtjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDE0ODE3MSwiZXhwIjoyMDg5NzI0MTcxfQ.nv9UhJ3BCpFZ7uCgZZ8LCDo-XI9CQyMU_tm4DFGiN4I"

WHATSMIAU_API_KEY  = "1d98c027-d224-476b-904c-883edca18542"
WHATSMIAU_INSTANCE = "69bf3b3737023c78f19c0671"
WHATSMIAU_BASE_URL = "https://api.whatsmiau.dev"

SERVER_URL     = "http://72.61.53.249:5000"
SERVER_TIMEOUT = 6

ADMIN_MASTER_PASS = "novaroma2025"
AGENTE_WHATSAPP   = "5541988718310"
GATEWAY_URL       = "https://novaroma.solutions"

TIPOS_CASO = ["Jurídico", "Contábil", "Imóveis", "Saúde", "Educação", "Consultoria", "Outro"]
SEXOS      = ["Masculino", "Feminino", "Outro"]


# ══════════════════════════════════════════════════════════════════════════════
#  TEMAS
# ══════════════════════════════════════════════════════════════════════════════

# ── Escuro: fundo profundo alaranjado — igual à landing page ─────────────────
DARK_THEME = {
    "BG":         "#0A0600",   # raiz ultra-escuro
    "BG2":        "#110800",   # sidebar / topbars
    "CARD":       "#160A00",   # cards
    "CARD2":      "#1C0E02",   # inputs / células
    "BORDER":     "#2A1500",
    "BORDER2":    "#3D2008",
    "TEXT":       "#F5E6D0",   # creme quente
    "TEXT_DIM":   "#3D2510",
    "TEXT_MID":   "#A07050",
    "ORANGE":     "#E07828",
    "ORANGE_DIM": "#A84E08",
    "ORANGE_GLO": "#FF9040",
    "SUCCESS":    "#2ECC71",
    "DANGER":     "#E74C3C",
    "WARNING":    "#F39C12",
    "CYAN":       "#00C2FF",
    "SIDEBAR_W":  "200px",
}

# ── Claro: creme suave com acentos laranja ────────────────────────────────────
LIGHT_THEME = {
    "BG":         "#FAF5EE",
    "BG2":        "#F0E8DC",
    "CARD":       "#FFFFFF",
    "CARD2":      "#F5EDE0",
    "BORDER":     "#E0D0BC",
    "BORDER2":    "#CDB898",
    "TEXT":       "#1A0C00",
    "TEXT_DIM":   "#B89878",
    "TEXT_MID":   "#7A4A28",
    "ORANGE":     "#C86010",
    "ORANGE_DIM": "#8A3C00",
    "ORANGE_GLO": "#E07828",
    "SUCCESS":    "#1E8A4A",
    "DANGER":     "#C0392B",
    "WARNING":    "#D68910",
    "CYAN":       "#0077AA",
    "SIDEBAR_W":  "200px",
}

_theme = DARK_THEME.copy()

def T(key): return _theme[key]

def set_theme(dark: bool):
    global _theme
    _theme = DARK_THEME.copy() if dark else LIGHT_THEME.copy()


# ══════════════════════════════════════════════════════════════════════════════
#  SUPABASE
# ══════════════════════════════════════════════════════════════════════════════

def _sh():
    return {
        "Content-Type":  "application/json",
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Prefer":        "return=representation",
    }

def _supa_get(table, params=None):
    qs = ""
    if params:
        qs = "?" + "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
    req = urllib.request.Request(f"{SUPABASE_URL}/rest/v1/{table}{qs}", headers=_sh(), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception:
        return []

def _supa_post(table, payload, extra_headers=None):
    hdrs = _sh()
    if extra_headers: hdrs.update(extra_headers)
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(f"{SUPABASE_URL}/rest/v1/{table}", data=data, headers=hdrs, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            result = json.loads(r.read())
            return result[0] if isinstance(result, list) and result else result
    except Exception:
        return None

def _supa_patch(table, filters, payload):
    qs  = "?" + "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in filters.items())
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(f"{SUPABASE_URL}/rest/v1/{table}{qs}", data=data, headers=_sh(), method="PATCH")
    try:
        with urllib.request.urlopen(req, timeout=10) as r: r.read(); return True
    except Exception: return False

def _supa_delete(table, filters):
    qs  = "?" + "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in filters.items())
    req = urllib.request.Request(f"{SUPABASE_URL}/rest/v1/{table}{qs}", headers=_sh(), method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=10) as r: r.read(); return True
    except Exception: return False

def _supa_upsert(table, payload):
    hdrs = _sh(); hdrs["Prefer"] = "resolution=merge-duplicates,return=representation"
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(f"{SUPABASE_URL}/rest/v1/{table}", data=data, headers=hdrs, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r: r.read()
    except Exception: pass


# ── DB helpers ────────────────────────────────────────────────────────────────

def hash_senha(s): return hashlib.sha256(s.encode()).hexdigest()

def db_get_user(username):
    rows = _supa_get("usuarios", {"username": f"eq.{username}"})
    return rows[0] if rows else None

def db_criar_user(username, senha_hash):
    return _supa_post("usuarios", {
        "username": username, "senha_hash": senha_hash,
        "is_admin": False, "ativo": True,
        "criado_em": datetime.now().isoformat(),
        "plano": "mensal", "validade_dias": 30,
    })

def db_atualizar_senha(uid, senha_hash):
    _supa_patch("usuarios", {"id": f"eq.{uid}"}, {"senha_hash": senha_hash})

def db_atualizar_email(uid, email):
    return _supa_patch("usuarios", {"id": f"eq.{uid}"}, {"email": email})

def db_toggle_ativo(uid, novo):
    _supa_patch("usuarios", {"id": f"eq.{uid}"}, {"ativo": novo})

def db_excluir_user(uid):
    clientes = _supa_get("clientes", {"usuario_id": f"eq.{uid}"})
    for c in clientes: _supa_delete("documentos", {"cliente_id": f"eq.{c['id']}"})
    _supa_delete("clientes", {"usuario_id": f"eq.{uid}"})
    _supa_delete("usuarios", {"id": f"eq.{uid}"})

def db_listar_users():
    return _supa_get("usuarios", {"order": "criado_em.desc"})

def db_count_clientes_user(uid):
    return len(_supa_get("clientes", {"usuario_id": f"eq.{uid}", "select": "id"}))

def db_count_total():
    return len(_supa_get("clientes", {"select": "id"}))

def db_listar_clientes(uid, filtro_tipo="todos", filtro_texto=""):
    params = {"usuario_id": f"eq.{uid}", "order": "nome.asc"}
    if filtro_tipo != "todos": params["tipo_caso"] = f"eq.{filtro_tipo}"
    rows = _supa_get("clientes", params)
    if filtro_texto:
        t = filtro_texto.lower()
        rows = [r for r in rows if t in (r.get("nome") or "").lower()
                or t in (r.get("cpf") or "").lower() or t in (r.get("telefone") or "").lower()]
    return rows

def db_get_cliente(cid):
    rows = _supa_get("clientes", {"id": f"eq.{cid}"}); return rows[0] if rows else None

def db_criar_cliente(p): return _supa_post("clientes", p)
def db_atualizar_cliente(cid, p): _supa_patch("clientes", {"id": f"eq.{cid}"}, p)
def db_excluir_cliente(cid):
    _supa_delete("documentos", {"cliente_id": f"eq.{cid}"}); _supa_delete("clientes", {"id": f"eq.{cid}"})

def db_listar_clientes_aniv(uid):
    rows = _supa_get("clientes", {"usuario_id": f"eq.{uid}", "data_nascimento": "not.is.null", "select": "id,nome,telefone,data_nascimento"})
    return [r for r in rows if r.get("data_nascimento")]

def db_listar_docs(cid): return _supa_get("documentos", {"cliente_id": f"eq.{cid}"})
def db_criar_doc(cid, nome, caminho):
    _supa_post("documentos", {"cliente_id": cid, "nome_arquivo": nome, "caminho": caminho, "enviado_em": datetime.now().isoformat()})

def get_config(chave, default=""):
    rows = _supa_get("configuracoes", {"chave": f"eq.{chave}"}); return rows[0]["valor"] if rows else default

def set_config(chave, valor): _supa_upsert("configuracoes", {"chave": chave, "valor": str(valor)})

def _client_tab_defaults():
    return [{"id": "clientes_default", "title": "Clientes", "integrada": True}]

def get_client_tabs():
    raw = get_config("clientes_abas", "")
    custom = []
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict):
                        tab_id = str(item.get("id") or "").strip()
                        if not tab_id:
                            continue
                        custom.append({
                            "id": tab_id,
                            "title": str(item.get("title") or "Clientes").strip() or "Clientes",
                            "integrada": bool(item.get("integrada", False)),
                        })
        except Exception:
            custom = []
    defaults = _client_tab_defaults()
    existing_ids = {t["id"] for t in custom}
    merged = [dict(t) for t in defaults]
    for tab in custom:
        if tab["id"] not in {d["id"] for d in defaults}:
            merged.append(tab)
    return merged

def salvar_client_tabs(tabs):
    payload = []
    for tab in tabs:
        payload.append({
            "id": str(tab.get("id") or "").strip(),
            "title": str(tab.get("title") or "Clientes").strip() or "Clientes",
            "integrada": bool(tab.get("integrada", False)),
        })
    set_config("clientes_abas", json.dumps(payload, ensure_ascii=False))

def _mensagens_auto_default():
    return [{
        "id": "aniversariantes",
        "title": "Aniversariantes",
        "message": "Feliz Aniversario, {nome}! A equipe da {empresa} deseja um dia incrivel para voce.",
        "integrada": True,
        "target_mode": "all",
        "target_client_ids": [],
        "send_date": "",
        "send_time": "",
        "last_sent_at": "",
    }]

def get_mensagens_automaticas():
    raw = get_config("mensagens_automaticas", "")
    custom = []
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                for m in parsed:
                    if isinstance(m, dict):
                        custom.append({
                            "id": str(m.get("id") or ""),
                            "title": str(m.get("title") or "").strip() or "Mensagem",
                            "message": str(m.get("message") or "").strip(),
                            "integrada": bool(m.get("integrada", False)),
                            "target_mode": "manual" if m.get("target_mode") == "manual" else "all",
                            "target_client_ids": [int(cid) for cid in m.get("target_client_ids", []) if str(cid).isdigit()],
                            "send_date": str(m.get("send_date") or ""),
                            "send_time": str(m.get("send_time") or ""),
                            "last_sent_at": str(m.get("last_sent_at") or ""),
                        })
        except Exception:
            custom = []

    defaults = _mensagens_auto_default()
    by_id = {m["id"]: m for m in custom if m.get("id")}
    merged = []
    for d in defaults:
        found = by_id.pop(d["id"], None)
        if found:
            d2 = dict(d)
            d2["title"] = found.get("title") or d["title"]
            d2["message"] = found.get("message") or d["message"]
            d2["target_mode"] = found.get("target_mode") or d["target_mode"]
            d2["target_client_ids"] = found.get("target_client_ids", [])
            d2["send_date"] = found.get("send_date") or ""
            d2["send_time"] = found.get("send_time") or ""
            d2["last_sent_at"] = found.get("last_sent_at") or ""
            merged.append(d2)
        else:
            merged.append(dict(d))

    for m in custom:
        mid = m.get("id", "")
        if mid and mid not in {d["id"] for d in defaults}:
            merged.append({
                "id": mid,
                "title": m.get("title") or "Mensagem",
                "message": m.get("message") or "",
                "integrada": False,
                "target_mode": m.get("target_mode") or "all",
                "target_client_ids": m.get("target_client_ids", []),
                "send_date": m.get("send_date") or "",
                "send_time": m.get("send_time") or "",
                "last_sent_at": m.get("last_sent_at") or "",
            })
    return merged

def salvar_mensagens_automaticas(msgs):
    payload = []
    for m in msgs:
        payload.append({
            "id": str(m.get("id") or ""),
            "title": str(m.get("title") or "").strip() or "Mensagem",
            "message": str(m.get("message") or "").strip(),
            "integrada": bool(m.get("integrada", False)),
            "target_mode": "manual" if m.get("target_mode") == "manual" else "all",
            "target_client_ids": [int(cid) for cid in m.get("target_client_ids", []) if str(cid).isdigit()],
            "send_date": str(m.get("send_date") or ""),
            "send_time": str(m.get("send_time") or ""),
            "last_sent_at": str(m.get("last_sent_at") or ""),
        })
    set_config("mensagens_automaticas", json.dumps(payload, ensure_ascii=False))

def _clientes_destino_mensagem(uid, msg_cfg):
    clientes = db_listar_clientes(uid)
    if msg_cfg.get("target_mode") == "manual":
        selected = set(int(cid) for cid in msg_cfg.get("target_client_ids", []) if str(cid).isdigit())
        return [c for c in clientes if c.get("id") in selected]
    return clientes

def _renderizar_template_mensagem(template, cliente, empresa, envio_dt=None):
    rendered = template
    rendered = rendered.replace("{nome}", str(cliente.get("nome") or "Cliente"))
    rendered = rendered.replace("{empresa}", empresa)
    rendered = rendered.replace("{telefone}", str(cliente.get("telefone") or ""))
    rendered = rendered.replace("{cpf}", str(cliente.get("cpf") or ""))
    rendered = rendered.replace("{data_envio}", envio_dt.strftime("%d/%m/%Y %H:%M") if envio_dt else datetime.now().strftime("%d/%m/%Y %H:%M"))
    return rendered

def enviar_mensagem_automatica(uid, msg_cfg, clientes=None):
    empresa = get_config("empresa_nome", "NovaRoma")
    target_clientes = clientes if clientes is not None else _clientes_destino_mensagem(uid, msg_cfg)
    enviados = []
    sem_tel = []
    erros = []
    for cliente in target_clientes:
        tel = "".join(x for x in (cliente.get("telefone") or "") if x.isdigit())
        if len(tel) < 10:
            sem_tel.append(cliente.get("nome") or "Cliente")
            continue
        texto = _renderizar_template_mensagem(msg_cfg.get("message") or "", cliente, empresa)
        ok, err = enviar_whatsapp(tel, texto)
        if ok:
            enviados.append(cliente.get("nome") or "Cliente")
        else:
            erros.append(f"{cliente.get('nome') or 'Cliente'} -> {err}")
    return {"enviados": enviados, "sem_tel": sem_tel, "erros": erros}

def processar_mensagens_agendadas(uid):
    agora = datetime.now()
    mensagens = get_mensagens_automaticas()
    alterado = False
    processadas = []
    for msg in mensagens:
        send_date = msg.get("send_date") or ""
        send_time = msg.get("send_time") or ""
        if not send_date or not send_time:
            continue
        try:
            agendado = datetime.strptime(f"{send_date} {send_time}", "%Y-%m-%d %H:%M")
        except Exception:
            continue
        if agora < agendado:
            continue
        resultado = enviar_mensagem_automatica(uid, msg)
        msg["last_sent_at"] = agora.isoformat()
        msg["send_date"] = ""
        msg["send_time"] = ""
        alterado = True
        processadas.append((msg.get("title") or "Mensagem", resultado))
    if alterado:
        salvar_mensagens_automaticas(mensagens)
    return processadas

def log_ja_enviado(cid, hoje):
    return bool(_supa_get("aniversarios_log", {"cliente_id": f"eq.{cid}", "enviado_em": f"eq.{hoje}"}))

def log_registrar(cid, hoje): _supa_post("aniversarios_log", {"cliente_id": cid, "enviado_em": hoje})


# ══════════════════════════════════════════════════════════════════════════════
#  VPS AUTH
# ══════════════════════════════════════════════════════════════════════════════

def verificar_vps(usuario, senha):
    try:
        payload = json.dumps({"usuario": usuario, "senha": senha}).encode()
        req = urllib.request.Request(f"{SERVER_URL}/login", data=payload,
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=SERVER_TIMEOUT) as r:
            d = json.loads(r.read())
            return (True, "") if d.get("ok") else (False, "Usuário ou senha incorretos.")
    except urllib.error.URLError: return False, "Servidor offline. Contate a NovaRoma."
    except Exception: return False, "Erro de conexão."


# ══════════════════════════════════════════════════════════════════════════════
#  WHATSMIAU
# ══════════════════════════════════════════════════════════════════════════════

def _wm_post(endpoint, payload):
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(f"{WHATSMIAU_BASE_URL}{endpoint}", data=data,
                                   headers={"Content-Type": "application/json", "apikey": WHATSMIAU_API_KEY}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read())
            return (True, "") if d.get("key") or d.get("status") == "success" else (False, str(d))
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}"
    except urllib.error.URLError as e: return False, f"Sem conexão: {e.reason}"
    except Exception as e: return False, str(e)

def enviar_whatsapp(numero, texto):
    d = "".join(c for c in numero if c.isdigit())
    if not d.startswith("55"): d = "55" + d
    return _wm_post(f"/message/sendText/{WHATSMIAU_INSTANCE}", {"number": d, "text": texto, "delay": 1200})


# ══════════════════════════════════════════════════════════════════════════════
#  ANIVERSÁRIOS
# ══════════════════════════════════════════════════════════════════════════════

def verificar_e_enviar_aniversarios(usuario_id=None):
    hoje = date.today(); hoje_str = hoje.strftime("%Y-%m-%d")
    aniv_ativo = get_config("aniversario_ativo", "1")
    if aniv_ativo != "1": return {"enviados": [], "sem_tel": [], "erros": [], "ja_enviados": []}

    clientes = db_listar_clientes_aniv(usuario_id) if usuario_id else \
               _supa_get("clientes", {"data_nascimento": "not.is.null", "select": "id,nome,telefone,data_nascimento"})

    empresa = get_config("empresa_nome", "NovaRoma")
    auto_msgs = get_mensagens_automaticas()
    aniv_msg = next((m for m in auto_msgs if m.get("id") == "aniversariantes"), None)
    template = (aniv_msg or {}).get("message") or "Feliz Aniversario, {nome}! A equipe da {empresa} deseja um dia incrivel para voce."
    enviados = []; sem_tel = []; erros = []; ja_enviados = []

    for c in clientes:
        try: dt = datetime.strptime(c["data_nascimento"], "%Y-%m-%d").date()
        except: continue
        if dt.month != hoje.month or dt.day != hoje.day: continue
        if log_ja_enviado(c["id"], hoje_str): ja_enviados.append(c["nome"]); continue
        tel = "".join(x for x in (c.get("telefone") or "") if x.isdigit())
        if len(tel) < 10: sem_tel.append(c["nome"]); continue
        msg = template.replace("{nome}", c["nome"]).replace("{empresa}", empresa)
        ok, err = enviar_whatsapp(tel, msg)
        if ok: log_registrar(c["id"], hoje_str); enviados.append(c["nome"])
        else: erros.append(f"{c['nome']} → {err}")

    return {"enviados": enviados, "sem_tel": sem_tel, "erros": erros, "ja_enviados": ja_enviados}


# ══════════════════════════════════════════════════════════════════════════════
#  STYLESHEET DINÂMICO
# ══════════════════════════════════════════════════════════════════════════════

def build_qss():
    return f"""
/* ── BASE ─────────────────────────────────────────────────────────────────── */
QWidget {{
    background-color: {T('BG')};
    color: {T('TEXT')};
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 12px;
    border: none;
    outline: none;
}}
QLabel {{ background: transparent; }}

/* ── INPUTS ──────────────────────────────────────────────────────────────── */
QLineEdit, QTextEdit, QComboBox, QSpinBox, QTimeEdit, QDateEdit {{
    background-color: {T('CARD2')};
    border: 1px solid {T('BORDER2')};
    border-radius: 7px;
    color: {T('TEXT')};
    padding: 8px 13px;
    font-size: 12px;
    selection-background-color: {T('ORANGE')};
    selection-color: #000;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus,
QSpinBox:focus, QTimeEdit:focus, QDateEdit:focus {{
    border-color: {T('ORANGE')};
    background-color: {T('CARD')};
}}
QComboBox::drop-down {{ border: none; padding-right: 10px; }}
QComboBox QAbstractItemView {{
    background-color: {T('CARD')};
    border: 1px solid {T('BORDER2')};
    color: {T('TEXT')};
    selection-background-color: {T('ORANGE')};
    selection-color: #000;
    outline: none;
    padding: 4px;
}}

/* ── BOTÕES PRINCIPAIS ──────────────────────────────────────────────────── */
QPushButton {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {T('ORANGE_DIM')}, stop:1 {T('ORANGE')});
    color: #fff5ec;
    border: none;
    border-radius: 7px;
    padding: 10px 22px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 2px;
}}
QPushButton:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {T('ORANGE')}, stop:1 {T('ORANGE_GLO')});
}}
QPushButton:pressed {{ background: {T('ORANGE_DIM')}; }}
QPushButton:disabled {{ background-color: {T('BORDER2')}; color: {T('TEXT_DIM')}; }}

QPushButton#btn_ghost {{
    background-color: transparent;
    border: 1px solid {T('BORDER2')};
    color: {T('TEXT_MID')};
    letter-spacing: 1px;
}}
QPushButton#btn_ghost:hover {{
    border-color: {T('ORANGE')};
    color: {T('ORANGE')};
    background-color: rgba(224,120,40,0.07);
}}

QPushButton#btn_link {{
    background-color: transparent;
    border: none;
    color: {T('TEXT_MID')};
    text-align: left;
    padding: 2px 0;
    font-size: 11px;
    letter-spacing: 1px;
}}
QPushButton#btn_link:hover {{ color: {T('ORANGE')}; }}

QPushButton#btn_danger {{
    background-color: transparent;
    border: 1px solid {T('DANGER')};
    color: {T('DANGER')};
    font-size: 11px;
    letter-spacing: 1px;
}}
QPushButton#btn_danger:hover {{ background-color: {T('DANGER')}; color: white; }}

QPushButton#btn_success {{
    background-color: transparent;
    border: 1px solid {T('SUCCESS')};
    color: {T('SUCCESS')};
    font-size: 11px;
    letter-spacing: 1px;
}}
QPushButton#btn_success:hover {{ background-color: {T('SUCCESS')}; color: #000; }}

/* ── SIDEBAR ─────────────────────────────────────────────────────────────── */
QPushButton#btn_sidebar {{
    background-color: transparent;
    border: none;
    border-radius: 7px;
    color: {T('TEXT_DIM')};
    text-align: left;
    padding: 10px 14px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
}}
QPushButton#btn_sidebar:hover {{
    background-color: rgba(224,120,40,0.08);
    color: {T('TEXT_MID')};
}}
QPushButton#btn_sidebar[active="true"] {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 rgba(224,120,40,0.20), stop:1 rgba(224,120,40,0.04));
    color: {T('ORANGE_GLO')};
    border-left: 3px solid {T('ORANGE')};
    padding-left: 11px;
}}

/* ── TABELA ──────────────────────────────────────────────────────────────── */
QTableWidget {{
    background-color: {T('BG')};
    border: 1px solid {T('BORDER')};
    border-radius: 8px;
    gridline-color: {T('BORDER')};
    color: {T('TEXT')};
    font-size: 12px;
}}
QTableWidget::item {{
    padding: 10px 14px;
    border-bottom: 1px solid {T('BORDER')};
}}
QTableWidget::item:selected {{
    background-color: rgba(224,120,40,0.12);
    color: {T('TEXT')};
}}
QHeaderView::section {{
    background-color: {T('CARD')};
    color: {T('ORANGE_DIM')};
    padding: 10px 14px;
    border: none;
    border-bottom: 1px solid {T('BORDER2')};
    font-size: 9px;
    letter-spacing: 3px;
    font-weight: bold;
}}

/* ── SCROLLBAR ───────────────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: {T('CARD')};
    width: 5px;
    border-radius: 3px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {T('BORDER2')};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {T('ORANGE')}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {T('CARD')};
    height: 5px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {T('BORDER2')};
    border-radius: 3px;
}}
QScrollBar::handle:horizontal:hover {{ background: {T('ORANGE')}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── FRAMES ──────────────────────────────────────────────────────────────── */
QFrame#sidebar {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {T('BG2')}, stop:1 {T('BG')});
    border-right: 1px solid {T('BORDER')};
}}
QFrame#card {{
    background-color: {T('CARD')};
    border: 1px solid {T('BORDER')};
    border-radius: 10px;
}}
QFrame#divider {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 transparent, stop:0.3 {T('BORDER2')},
        stop:0.7 {T('BORDER2')}, stop:1 transparent);
    max-height: 1px;
}}
QFrame#topbar {{
    background-color: {T('BG2')};
    border-bottom: 1px solid {T('BORDER')};
}}

/* ── PROGRESSBAR ─────────────────────────────────────────────────────────── */
QProgressBar {{
    background-color: {T('CARD2')};
    border: none;
    border-radius: 3px;
    height: 5px;
    text-align: center;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {T('ORANGE_DIM')}, stop:1 {T('ORANGE_GLO')});
    border-radius: 3px;
}}

/* ── CHECKBOX / RADIO ────────────────────────────────────────────────────── */
QCheckBox {{ color: {T('TEXT_MID')}; spacing: 8px; }}
QCheckBox::indicator {{
    width: 16px; height: 16px;
    border: 1px solid {T('BORDER2')};
    border-radius: 4px;
    background: {T('CARD2')};
}}
QCheckBox::indicator:checked {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 {T('ORANGE')}, stop:1 {T('ORANGE_DIM')});
    border-color: {T('ORANGE')};
}}

QRadioButton {{ color: {T('TEXT_MID')}; spacing: 8px; }}
QRadioButton::indicator {{
    width: 16px; height: 16px;
    border: 1px solid {T('BORDER2')};
    border-radius: 8px;
    background: {T('CARD2')};
}}
QRadioButton::indicator:checked {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 {T('ORANGE')}, stop:1 {T('ORANGE_DIM')});
    border-color: {T('ORANGE')};
}}

/* ── DIALOGS / GROUPS ────────────────────────────────────────────────────── */
QMessageBox {{ background-color: {T('CARD')}; }}
QMessageBox QPushButton {{ min-width: 80px; }}
QDialog {{ background-color: {T('BG2')}; }}

QGroupBox {{
    border: 1px solid {T('BORDER')};
    border-radius: 8px;
    margin-top: 14px;
    color: {T('TEXT_MID')};
    font-size: 10px;
    letter-spacing: 2px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {T('TEXT_DIM')};
}}

/* ── TABS ────────────────────────────────────────────────────────────────── */
QTabWidget::pane {{
    border-top: 1px solid {T('BORDER2')};
    margin-top: -1px;
    background: {T('BG')};
}}
QTabBar::tab {{
    background: {T('CARD2')};
    color: {T('TEXT_MID')};
    border: 1px solid {T('BORDER2')};
    border-bottom: none;
    padding: 8px 16px;
    margin-right: 3px;
    border-radius: 6px 6px 0 0;
    font-size: 10px;
    letter-spacing: 1px;
}}
QTabBar::tab:selected {{
    background: {T('BG')};
    color: {T('ORANGE')};
    border-color: {T('ORANGE')};
    border-bottom-color: {T('BG')};
}}
QTabBar::tab:hover {{ color: {T('TEXT')}; background: {T('CARD')}; }}

/* ── CALENDÁRIO ──────────────────────────────────────────────────────────── */
QCalendarWidget QWidget#qt_calendar_navigationbar {{
    background: {T('CARD')};
    border-bottom: 1px solid {T('BORDER2')};
}}
QCalendarWidget QToolButton {{
    color: {T('TEXT')};
    background: transparent;
    border: 1px solid transparent;
    padding: 4px 10px;
    font-size: 12px;
    min-width: 52px;
}}
QCalendarWidget QToolButton:hover {{
    border-color: {T('ORANGE')};
    color: {T('ORANGE')};
    background: rgba(224,120,40,0.08);
    border-radius: 5px;
}}
QCalendarWidget QSpinBox {{
    min-width: 90px;
    color: {T('TEXT')};
    background: {T('CARD2')};
    border: 1px solid {T('BORDER2')};
    border-radius: 4px;
    padding: 2px 6px;
}}
QCalendarWidget QAbstractItemView:enabled {{
    color: {T('TEXT')};
    background: {T('BG')};
    selection-background-color: rgba(224,120,40,0.22);
    selection-color: {T('TEXT')};
}}

/* ── TOOLTIP ─────────────────────────────────────────────────────────────── */
QToolTip {{
    background-color: {T('CARD')};
    color: {T('TEXT')};
    border: 1px solid {T('ORANGE')};
    border-radius: 5px;
    padding: 5px 10px;
    font-size: 11px;
}}

/* ── SPLITTER ────────────────────────────────────────────────────────────── */
QSplitter::handle {{
    background: {T('BORDER')};
    width: 1px;
    height: 1px;
}}
"""


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS UI
# ══════════════════════════════════════════════════════════════════════════════

def divider():
    f = QFrame(); f.setObjectName("divider"); f.setFrameShape(QFrame.HLine)
    f.setFixedHeight(1); return f

def card():
    f = QFrame(); f.setObjectName("card"); return f

def mono_label(txt, size=9, color=None):
    l = QLabel(txt); l.setFont(QFont("Segoe UI", size))
    if color: l.setStyleSheet(f"color: {color}; background: transparent;")
    return l

def section_label(txt):
    l = QLabel(txt.upper())
    l.setFont(QFont("Segoe UI", 9, QFont.Bold))
    l.setStyleSheet(f"color: {T('ORANGE')}; letter-spacing: 3px; background: transparent;")
    return l


# ══════════════════════════════════════════════════════════════════════════════
#  DIALOG BASE
# ══════════════════════════════════════════════════════════════════════════════

class BaseDialog(QDialog):
    def __init__(self, title, parent=None, w=460):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(w)
        self.setModal(True)
        self._lay = QVBoxLayout(self)
        self._lay.setSpacing(14)
        self._lay.setContentsMargins(28, 28, 28, 28)

    def add_title(self, txt):
        l = QLabel(txt); l.setFont(QFont("Segoe UI", 13, QFont.Bold))
        l.setStyleSheet(f"color: {T('ORANGE')}; letter-spacing: 3px; background: transparent;")
        l.setAlignment(Qt.AlignCenter); self._lay.addWidget(l); self._lay.addWidget(divider())

    def add_error(self):
        self._err = QLabel(""); self._err.setStyleSheet(f"color: {T('DANGER')}; font-size: 11px; background: transparent;")
        self._err.setAlignment(Qt.AlignCenter); self._lay.addWidget(self._err); return self._err

    def set_error(self, txt): self._err.setText(txt)


# ══════════════════════════════════════════════════════════════════════════════
#  DIALOG: CLIENTE
# ══════════════════════════════════════════════════════════════════════════════

class ClienteDialog(BaseDialog):
    def __init__(self, usuario_id, cliente_id=None, parent=None):
        super().__init__("Novo Cliente" if not cliente_id else "Editar Cliente", parent, 540)
        self.usuario_id = usuario_id; self.cliente_id = cliente_id
        self._docs_novos = []
        self.add_title("NOVO CLIENTE" if not cliente_id else "EDITAR CLIENTE")
        self._build()
        if cliente_id: self._carregar()

    def _build(self):
        form = QFormLayout(); form.setSpacing(10); form.setLabelAlignment(Qt.AlignRight)
        def lbl(t):
            l = QLabel(t); l.setStyleSheet(f"color: {T('TEXT_DIM')}; font-size: 11px; letter-spacing: 1px; background: transparent;"); return l

        self.inp_nome  = QLineEdit(); self.inp_nome.setFixedHeight(36)
        self.inp_idade = QLineEdit(); self.inp_idade.setFixedHeight(36)
        self.cmb_sexo  = QComboBox(); self.cmb_sexo.addItems(SEXOS); self.cmb_sexo.setFixedHeight(36)
        self.inp_tel   = QLineEdit(); self.inp_tel.setPlaceholderText("(00) 00000-0000"); self.inp_tel.setFixedHeight(36)
        self.inp_cpf   = QLineEdit(); self.inp_cpf.setPlaceholderText("000.000.000-00"); self.inp_cpf.setFixedHeight(36)
        self.cmb_tipo  = QComboBox(); self.cmb_tipo.addItems(TIPOS_CASO); self.cmb_tipo.setFixedHeight(36)
        self.txt_obs   = QTextEdit(); self.txt_obs.setPlaceholderText("Observações..."); self.txt_obs.setFixedHeight(72)
        self.chk_nasc  = QCheckBox("Informar data de nascimento (aniversário)"); self.chk_nasc.setStyleSheet(f"color: {T('TEXT_MID')};")
        self.dte_nasc  = QDateEdit(); self.dte_nasc.setDisplayFormat("dd/MM/yyyy")
        self.dte_nasc.setCalendarPopup(True); self.dte_nasc.setFixedHeight(36)
        self.dte_nasc.setDate(QDate(1990, 1, 1)); self.dte_nasc.setEnabled(False)
        self.chk_nasc.toggled.connect(self.dte_nasc.setEnabled)

        form.addRow(lbl("Nome *"),       self.inp_nome)
        form.addRow(lbl("Idade"),        self.inp_idade)
        form.addRow(lbl("Sexo"),         self.cmb_sexo)
        form.addRow(lbl("Telefone"),     self.inp_tel)
        form.addRow(lbl("CPF"),          self.inp_cpf)
        form.addRow(lbl("Tipo"),         self.cmb_tipo)
        form.addRow(lbl("Observações"),  self.txt_obs)
        form.addRow(lbl(""),             self.chk_nasc)
        form.addRow(lbl("Data Nasc."),   self.dte_nasc)
        self._lay.addLayout(form)

        dl = mono_label("DOCUMENTOS", 9, T("TEXT_DIM")); self._lay.addWidget(dl)
        self.lst_docs = QListWidget(); self.lst_docs.setFixedHeight(72); self._lay.addWidget(self.lst_docs)
        dr = QHBoxLayout()
        btn_add = QPushButton("+ Anexar"); btn_add.setObjectName("btn_ghost"); btn_add.clicked.connect(self._anexar)
        btn_rem = QPushButton("Remover"); btn_rem.setObjectName("btn_danger"); btn_rem.clicked.connect(self._remover_doc)
        dr.addWidget(btn_add); dr.addWidget(btn_rem); self._lay.addLayout(dr)
        self._lay.addWidget(divider())
        self.add_error()
        btns = QHBoxLayout()
        bc = QPushButton("Cancelar"); bc.setObjectName("btn_ghost"); bc.clicked.connect(self.reject)
        bs = QPushButton("Salvar Cliente"); bs.clicked.connect(self._salvar)
        btns.addWidget(bc); btns.addWidget(bs); self._lay.addLayout(btns)

    def _anexar(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Selecionar", "", "Docs (*.pdf *.doc *.docx *.jpg *.png *.txt);;Todos (*)")
        for p in paths:
            n = os.path.basename(p); self._docs_novos.append((n, p))
            self.lst_docs.addItem(QListWidgetItem(f"  {n}"))

    def _remover_doc(self):
        row = self.lst_docs.currentRow()
        if row >= 0: self.lst_docs.takeItem(row);
        if row < len(self._docs_novos): self._docs_novos.pop(row)

    def _carregar(self):
        r = db_get_cliente(self.cliente_id)
        if not r: return
        self.inp_nome.setText(r.get("nome") or "")
        self.inp_idade.setText(str(r["idade"]) if r.get("idade") else "")
        idx = self.cmb_sexo.findText(r.get("sexo") or "")
        if idx >= 0: self.cmb_sexo.setCurrentIndex(idx)
        self.inp_tel.setText(r.get("telefone") or ""); self.inp_cpf.setText(r.get("cpf") or "")
        idx2 = self.cmb_tipo.findText(r.get("tipo_caso") or "")
        if idx2 >= 0: self.cmb_tipo.setCurrentIndex(idx2)
        self.txt_obs.setPlainText(r.get("observacoes") or "")
        dn = r.get("data_nascimento")
        if dn:
            try:
                dt = datetime.strptime(dn, "%Y-%m-%d").date()
                self.chk_nasc.setChecked(True); self.dte_nasc.setEnabled(True)
                self.dte_nasc.setDate(QDate(dt.year, dt.month, dt.day))
            except: pass
        for d in db_listar_docs(self.cliente_id):
            self.lst_docs.addItem(QListWidgetItem(f"  {d['nome_arquivo']}"))

    def _salvar(self):
        nome = self.inp_nome.text().strip()
        if not nome: self.set_error("Nome é obrigatório."); return
        try: idade = int(self.inp_idade.text().strip()) if self.inp_idade.text().strip() else None
        except: self.set_error("Idade inválida."); return
        dn = None
        if self.chk_nasc.isChecked():
            q = self.dte_nasc.date()
            dn = f"{q.year():04d}-{q.month():02d}-{q.day():02d}"
        agora = datetime.now().isoformat()
        p = {"nome": nome, "idade": idade, "sexo": self.cmb_sexo.currentText(),
             "telefone": self.inp_tel.text().strip(), "cpf": self.inp_cpf.text().strip(),
             "tipo_caso": self.cmb_tipo.currentText(), "observacoes": self.txt_obs.toPlainText().strip(),
             "data_nascimento": dn, "atualizado_em": agora}
        if self.cliente_id:
            db_atualizar_cliente(self.cliente_id, p); cid = self.cliente_id
        else:
            p["usuario_id"] = self.usuario_id; p["criado_em"] = agora
            r = db_criar_cliente(p)
            if not r: self.set_error("Erro ao salvar."); return
            cid = r["id"]
        for n, path in self._docs_novos: db_criar_doc(cid, n, path)
        self.accept()


# ══════════════════════════════════════════════════════════════════════════════
#  DIALOG: ANIVERSÁRIOS
# ══════════════════════════════════════════════════════════════════════════════

class AniversariosDialog(BaseDialog):
    def __init__(self, usuario_id, parent=None):
        super().__init__("Aniversariantes", parent, 620)
        self.usuario_id = usuario_id; self._anivs = []; self._checks = []
        self.add_title("🎂 ANIVERSARIANTES HOJE")
        self._build(); self._carregar()

    def _build(self):
        sub = mono_label(date.today().strftime("%d/%m/%Y"), 9, T("TEXT_DIM"))
        sub.setAlignment(Qt.AlignCenter); self._lay.addWidget(sub)
        self._lay.addWidget(divider())

        self.tabela = QTableWidget(); self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["", "NOME", "TELEFONE", "STATUS"])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.setColumnWidth(0, 36); self.tabela.setColumnWidth(2, 140); self.tabela.setColumnWidth(3, 130)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setShowGrid(False); self.tabela.verticalHeader().setDefaultSectionSize(44)
        self._lay.addWidget(self.tabela)

        self.lbl_info = mono_label("", 9, T("TEXT_DIM"))
        self.lbl_info.setAlignment(Qt.AlignCenter); self._lay.addWidget(self.lbl_info)

        self.prog = QProgressBar(); self.prog.setFixedHeight(6); self.prog.setTextVisible(False); self.prog.hide()
        self._lay.addWidget(self.prog)

        btns = QHBoxLayout()
        self.btn_enviar = QPushButton("🎉  Enviar Parabéns"); self.btn_enviar.clicked.connect(self._enviar)
        btn_fechar = QPushButton("Fechar"); btn_fechar.setObjectName("btn_ghost"); btn_fechar.clicked.connect(self.accept)
        btns.addWidget(self.btn_enviar); btns.addWidget(btn_fechar); self._lay.addLayout(btns)

    def _carregar(self):
        hoje = date.today(); hoje_str = hoje.strftime("%Y-%m-%d")
        clientes = db_listar_clientes_aniv(self.usuario_id)
        self._anivs = [c for c in clientes if c.get("data_nascimento") and
                       datetime.strptime(c["data_nascimento"], "%Y-%m-%d").month == hoje.month and
                       datetime.strptime(c["data_nascimento"], "%Y-%m-%d").day == hoje.day]
        self._checks = []
        self.tabela.setRowCount(len(self._anivs))
        if not self._anivs:
            self.lbl_info.setText("Nenhum aniversariante hoje."); self.btn_enviar.setEnabled(False); return
        for i, c in enumerate(self._anivs):
            ja = log_ja_enviado(c["id"], hoje_str)
            chk = QCheckBox(); chk.setChecked(not ja)
            if ja: chk.setEnabled(False)
            self._checks.append(chk)
            cw = QWidget(); cl = QHBoxLayout(cw); cl.setContentsMargins(4,0,4,0); cl.setAlignment(Qt.AlignCenter)
            cl.addWidget(chk); self.tabela.setCellWidget(i, 0, cw)
            self.tabela.setItem(i, 1, QTableWidgetItem(c["nome"]))
            self.tabela.setItem(i, 2, QTableWidgetItem(c.get("telefone") or "(sem telefone)"))
            self._set_status(i, "enviado" if ja else "pendente")
        pendentes = sum(1 for c in self._anivs if not log_ja_enviado(c["id"], hoje_str))
        self.lbl_info.setText(f"{len(self._anivs)} aniversariante(s)  ·  {pendentes} pendente(s)")

    def _set_status(self, row, estado):
        txts = {"pendente":"⏳ Pendente","enviando":"⏳ Enviando...","enviado":"✅ Enviado","erro":"❌ Falhou","skip":"— Ignorado"}
        cores = {"pendente":T("WARNING"),"enviando":T("CYAN"),"enviado":T("SUCCESS"),"erro":T("DANGER"),"skip":T("TEXT_DIM")}
        st = QTableWidgetItem(txts.get(estado, "")); st.setForeground(QColor(cores.get(estado, T("TEXT_DIM"))))
        st.setTextAlignment(Qt.AlignCenter); self.tabela.setItem(row, 3, st)

    def _enviar(self):
        hoje_str = date.today().strftime("%Y-%m-%d")
        sel = [(i, c) for i, (c, chk) in enumerate(zip(self._anivs, self._checks))
               if chk.isChecked() and not log_ja_enviado(c["id"], hoje_str)]
        if not sel: QMessageBox.information(self, "Aviso", "Nenhum cliente selecionado."); return
        self.btn_enviar.setEnabled(False); self.prog.show(); self.prog.setMaximum(len(sel)); self.prog.setValue(0)
        empresa = get_config("empresa_nome", "NovaRoma"); msg_extra = get_config("aniversario_extra", "")

        def _worker():
            for prog, (ri, c) in enumerate(sel, 1):
                QTimer.singleShot(0, lambda r=ri: self._set_status(r, "enviando"))
                tel = "".join(x for x in (c.get("telefone") or "") if x.isdigit())
                if len(tel) < 10:
                    QTimer.singleShot(0, lambda r=ri: self._set_status(r, "erro"))
                    QTimer.singleShot(0, lambda v=prog: self.prog.setValue(v)); continue
                msg = f"Feliz Aniversário, {c['nome']}! 🎉🎂\nA equipe da {empresa} deseja tudo de melhor para você neste dia especial! 🥳"
                if msg_extra: msg += f"\n\n{msg_extra}"
                ok, _ = enviar_whatsapp(tel, msg)
                if ok:
                    log_registrar(c["id"], hoje_str)
                    QTimer.singleShot(0, lambda r=ri: self._set_status(r, "enviado"))
                    QTimer.singleShot(0, lambda r=ri: self._disable_chk(r))
                else:
                    QTimer.singleShot(0, lambda r=ri: self._set_status(r, "erro"))
                QTimer.singleShot(0, lambda v=prog: self.prog.setValue(v))
            QTimer.singleShot(0, self._pos_envio)

        threading.Thread(target=_worker, daemon=True).start()

    def _disable_chk(self, row):
        if row < len(self._checks): self._checks[row].setChecked(False); self._checks[row].setEnabled(False)

    def _pos_envio(self):
        self.btn_enviar.setEnabled(True)
        hoje_str = date.today().strftime("%Y-%m-%d")
        pendentes = sum(1 for c in self._anivs if not log_ja_enviado(c["id"], hoje_str))
        self.lbl_info.setText(f"{len(self._anivs)} aniversariante(s)  ·  {pendentes} pendente(s)")
        QTimer.singleShot(1200, self.prog.hide)


# ══════════════════════════════════════════════════════════════════════════════
#  DIALOG: DADOS PESSOAIS
# ══════════════════════════════════════════════════════════════════════════════

class DadosPessoaisDialog(BaseDialog):
    def __init__(self, usuario_id, username, parent=None):
        super().__init__("Dados Pessoais", parent)
        self.uid = usuario_id
        self.add_title("DADOS PESSOAIS")
        self._build(username)

    def _build(self, username):
        self._lay.addWidget(mono_label("USUÁRIO ATUAL", 9, T("TEXT_DIM")))
        lbl = QLabel(username); lbl.setStyleSheet(f"color: {T('TEXT')}; font-size: 14px; font-weight: bold; background: transparent;")
        self._lay.addWidget(lbl); self._lay.addWidget(divider())
        self._lay.addWidget(mono_label("NOVA SENHA", 9, T("TEXT_DIM")))
        self.inp_nova = QLineEdit(); self.inp_nova.setEchoMode(QLineEdit.Password); self.inp_nova.setFixedHeight(38)
        self._lay.addWidget(self.inp_nova)
        self._lay.addWidget(mono_label("CONFIRMAR SENHA", 9, T("TEXT_DIM")))
        self.inp_conf = QLineEdit(); self.inp_conf.setEchoMode(QLineEdit.Password); self.inp_conf.setFixedHeight(38)
        self._lay.addWidget(self.inp_conf)
        self.add_error()
        btns = QHBoxLayout()
        bc = QPushButton("Cancelar"); bc.setObjectName("btn_ghost"); bc.clicked.connect(self.reject)
        bs = QPushButton("Salvar"); bs.clicked.connect(self._salvar)
        btns.addWidget(bc); btns.addWidget(bs); self._lay.addLayout(btns)

    def _salvar(self):
        nova = self.inp_nova.text(); conf = self.inp_conf.text()
        if len(nova) < 4: self.set_error("Mínimo 4 caracteres."); return
        if nova != conf: self.set_error("Senhas não coincidem."); return
        db_atualizar_senha(self.uid, hash_senha(nova))
        QMessageBox.information(self, "Salvo", "Senha atualizada com sucesso!"); self.accept()


class AlterarEmailDialog(BaseDialog):
    def __init__(self, usuario_id, email_atual="", parent=None):
        super().__init__("Alterar E-mail", parent)
        self.uid = usuario_id
        self.add_title("ALTERAR E-MAIL")
        self._build(email_atual)

    def _build(self, email_atual):
        self._lay.addWidget(mono_label("E-MAIL ATUAL", 9, T("TEXT_DIM")))
        self.inp_email_atual = QLineEdit(); self.inp_email_atual.setFixedHeight(38)
        self.inp_email_atual.setReadOnly(True); self.inp_email_atual.setText(email_atual or "(não informado)")
        self._lay.addWidget(self.inp_email_atual)
        self._lay.addWidget(mono_label("NOVO E-MAIL", 9, T("TEXT_DIM")))
        self.inp_email_novo = QLineEdit(); self.inp_email_novo.setFixedHeight(38)
        self.inp_email_novo.setPlaceholderText("exemplo@dominio.com")
        self._lay.addWidget(self.inp_email_novo)
        self.add_error()
        btns = QHBoxLayout()
        bc = QPushButton("Cancelar"); bc.setObjectName("btn_ghost"); bc.clicked.connect(self.reject)
        bs = QPushButton("Salvar"); bs.clicked.connect(self._salvar)
        btns.addWidget(bc); btns.addWidget(bs); self._lay.addLayout(btns)

    def _salvar(self):
        novo = self.inp_email_novo.text().strip()
        if not novo or "@" not in novo or "." not in novo.split("@")[-1]:
            self.set_error("Informe um e-mail válido."); return
        ok = db_atualizar_email(self.uid, novo)
        if not ok:
            self.set_error("Não foi possível atualizar o e-mail."); return
        QMessageBox.information(self, "Salvo", "E-mail atualizado com sucesso!")
        self.accept()


class SelecionarClientesDialog(BaseDialog):
    def __init__(self, usuario_id, selecionados=None, parent=None):
        super().__init__("Selecionar Clientes", parent, 560)
        self.uid = usuario_id
        self._selecionados = set(int(cid) for cid in (selecionados or []) if str(cid).isdigit())
        self.resultado = list(self._selecionados)
        self.add_title("SELECIONAR CLIENTES")
        self._build()
        self._carregar()

    def _build(self):
        info = mono_label("Marque os clientes que receberão esta mensagem.", 9, T("TEXT_DIM"))
        self._lay.addWidget(info)
        top = QHBoxLayout()
        btn_todos = QPushButton("Selecionar Todos"); btn_todos.setObjectName("btn_ghost"); btn_todos.setFixedHeight(30)
        btn_limpar = QPushButton("Limpar"); btn_limpar.setObjectName("btn_ghost"); btn_limpar.setFixedHeight(30)
        btn_todos.clicked.connect(lambda: self._check_all(True))
        btn_limpar.clicked.connect(lambda: self._check_all(False))
        top.addWidget(btn_todos); top.addWidget(btn_limpar); top.addStretch()
        self._lay.addLayout(top)
        self.lista = QListWidget(); self.lista.setFixedHeight(260)
        self._lay.addWidget(self.lista)
        btns = QHBoxLayout()
        bc = QPushButton("Cancelar"); bc.setObjectName("btn_ghost"); bc.clicked.connect(self.reject)
        bs = QPushButton("Salvar Seleção"); bs.clicked.connect(self._salvar)
        btns.addWidget(bc); btns.addWidget(bs); self._lay.addLayout(btns)

    def _carregar(self):
        self.lista.clear()
        for cliente in db_listar_clientes(self.uid):
            nome = cliente.get("nome") or "Cliente"
            telefone = cliente.get("telefone") or "-"
            item = QListWidgetItem(f"{nome}  ·  {telefone}")
            item.setData(Qt.UserRole, cliente.get("id"))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if cliente.get("id") in self._selecionados else Qt.Unchecked)
            self.lista.addItem(item)

    def _check_all(self, checked):
        state = Qt.Checked if checked else Qt.Unchecked
        for idx in range(self.lista.count()):
            self.lista.item(idx).setCheckState(state)

    def _salvar(self):
        selecionados = []
        for idx in range(self.lista.count()):
            item = self.lista.item(idx)
            if item.checkState() == Qt.Checked:
                selecionados.append(item.data(Qt.UserRole))
        self.resultado = selecionados
        self.accept()


# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN DIALOGS
# ══════════════════════════════════════════════════════════════════════════════

class AdminLoginDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Admin", parent)
        self.add_title("🔐 PAINEL ADMIN")
        self._lay.addWidget(mono_label("SENHA MESTRA", 9, T("TEXT_DIM")))
        self.inp = QLineEdit(); self.inp.setEchoMode(QLineEdit.Password); self.inp.setFixedHeight(38)
        self.inp.returnPressed.connect(self._check); self._lay.addWidget(self.inp)
        self.add_error()
        btn = QPushButton("Acessar"); btn.clicked.connect(self._check); self._lay.addWidget(btn)

    def _check(self):
        if self.inp.text() == ADMIN_MASTER_PASS: self.accept()
        else: self.set_error("Senha incorreta."); self.inp.clear()


class AdminPanel(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Painel Admin", parent, 880)
        self.setMinimumHeight(560)
        self.add_title("PAINEL ADMINISTRATIVO")
        self._build(); self._carregar()

    def _build(self):
        stats = QHBoxLayout()
        card_users, self.lbl_users = self._stat("USUÁRIOS", "0")
        card_ativos, self.lbl_ativos = self._stat("ATIVOS", "0")
        card_clientes, self.lbl_clis = self._stat("CLIENTES TOTAL", "0")
        stats.addWidget(card_users); stats.addWidget(card_ativos); stats.addWidget(card_clientes)
        self._lay.addLayout(stats)
        row = QHBoxLayout()
        btn_add = QPushButton("+ Novo Usuário"); btn_add.clicked.connect(self._novo_user); btn_add.setFixedHeight(34)
        row.addWidget(btn_add); row.addStretch(); self._lay.addLayout(row)
        self.tabela = QTableWidget(); self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["USUÁRIO","CRIADO EM","CLIENTES","STATUS","AÇÕES"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela.setColumnWidth(1, 120); self.tabela.setColumnWidth(2, 80)
        self.tabela.setColumnWidth(3, 80); self.tabela.setColumnWidth(4, 220)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setShowGrid(False); self.tabela.verticalHeader().setDefaultSectionSize(46)
        self._lay.addWidget(self.tabela)
        btn_f = QPushButton("Fechar"); btn_f.setObjectName("btn_ghost"); btn_f.clicked.connect(self.accept)
        self._lay.addWidget(btn_f)

    def _stat(self, label, value):
        box = card(); bl = QVBoxLayout(box); bl.setContentsMargins(16,12,16,12); bl.setSpacing(2)
        lv = QLabel(value); lv.setFont(QFont("Segoe UI", 22, QFont.Bold))
        lv.setStyleSheet(f"color: {T('ORANGE')}; background: transparent;"); lv.setAlignment(Qt.AlignCenter)
        ll = mono_label(label, 8, T("TEXT_DIM")); ll.setAlignment(Qt.AlignCenter)
        bl.addWidget(lv); bl.addWidget(ll); return box, lv

    def _carregar(self):
        users = db_listar_users(); total = db_count_total(); ativos = sum(1 for u in users if u.get("ativo"))
        self.lbl_users.setText(str(len(users))); self.lbl_ativos.setText(str(ativos)); self.lbl_clis.setText(str(total))
        self.tabela.setRowCount(len(users))
        for i, u in enumerate(users):
            n_cli = db_count_clientes_user(u["id"])
            self.tabela.setItem(i, 0, QTableWidgetItem(u["username"]))
            self.tabela.setItem(i, 1, QTableWidgetItem((u.get("criado_em") or "")[:10]))
            ci = QTableWidgetItem(str(n_cli)); ci.setTextAlignment(Qt.AlignCenter); self.tabela.setItem(i, 2, ci)
            ativo = u.get("ativo", True)
            si = QTableWidgetItem("ATIVO" if ativo else "INATIVO")
            si.setForeground(QColor(T("SUCCESS") if ativo else T("DANGER"))); si.setTextAlignment(Qt.AlignCenter)
            self.tabela.setItem(i, 3, si)
            cell = QWidget(); cell.setStyleSheet("background: transparent;")
            cl = QHBoxLayout(cell); cl.setContentsMargins(4,4,4,4); cl.setSpacing(4)
            bs = QPushButton("Senha"); bs.setFixedHeight(28); bs.setObjectName("btn_ghost")
            bs.clicked.connect(lambda _, uid=u["id"], un=u["username"]: self._senha(uid, un))
            bt = QPushButton("Desativar" if ativo else "Ativar"); bt.setFixedHeight(28)
            bt.setObjectName("btn_danger" if ativo else "btn_success")
            bt.clicked.connect(lambda _, uid=u["id"], av=ativo: self._toggle(uid, av))
            bx = QPushButton("X"); bx.setFixedSize(28,28); bx.setObjectName("btn_danger")
            bx.clicked.connect(lambda _, uid=u["id"], un=u["username"]: self._excluir(uid, un))
            cl.addWidget(bs); cl.addWidget(bt); cl.addWidget(bx); cl.addStretch()
            self.tabela.setCellWidget(i, 4, cell)

    def _novo_user(self):
        user, ok = QInputDialog.getText(self, "Novo usuário", "Nome de usuário:")
        if not ok or not user.strip(): return
        senha, ok2 = QInputDialog.getText(self, "Senha", "Senha:", QLineEdit.Password)
        if not ok2 or len(senha) < 4: return
        db_criar_user(user.strip(), hash_senha(senha))
        self._carregar()

    def _senha(self, uid, username):
        dlg = BaseDialog(f"Senha — {username}", self)
        dlg.add_title(f"SENHA\n{username.upper()}")
        dlg._lay.addWidget(mono_label("NOVA SENHA", 9, T("TEXT_DIM")))
        inp = QLineEdit(); inp.setEchoMode(QLineEdit.Password); inp.setFixedHeight(36); dlg._lay.addWidget(inp)
        err = dlg.add_error()
        btn = QPushButton("Salvar")
        def _s():
            if len(inp.text()) < 4: err.setText("Mínimo 4 caracteres."); return
            db_atualizar_senha(uid, hash_senha(inp.text())); dlg.accept()
        btn.clicked.connect(_s); dlg._lay.addWidget(btn)
        dlg.exec_()

    def _toggle(self, uid, ativo):
        acao = "desativar" if ativo else "ativar"
        if QMessageBox.question(self, "Confirmar", f"Deseja {acao} este usuário?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            db_toggle_ativo(uid, not ativo); self._carregar()

    def _excluir(self, uid, username):
        n = db_count_clientes_user(uid)
        if QMessageBox.question(self, "Confirmar", f"Excluir '{username}'?\n{n} cliente(s) serão removidos.",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            db_excluir_user(uid); self._carregar()


# ══════════════════════════════════════════════════════════════════════════════
#  TELA DE LOGIN
# ══════════════════════════════════════════════════════════════════════════════

class LoginWidget(QWidget):
    login_ok = pyqtSignal(int, str, dict)

    def __init__(self):
        super().__init__(); self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setAlignment(Qt.AlignCenter); root.setContentsMargins(0,0,0,0)
        center = QWidget(); center.setFixedWidth(380)
        lay = QVBoxLayout(center); lay.setSpacing(0); lay.setContentsMargins(0,0,0,0)

        # Logo — estética da landing page
        logo_area = QVBoxLayout(); logo_area.setSpacing(8); logo_area.setAlignment(Qt.AlignCenter)
        mark = QLabel("N"); mark.setFont(QFont("Segoe UI", 14, QFont.Bold))
        mark.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {T('ORANGE_DIM')}, stop:1 {T('ORANGE')});"
            f"color: #fff5ec; border-radius: 12px; padding: 10px 14px;"
        )
        mark.setAlignment(Qt.AlignCenter); mark.setFixedSize(56, 56)

        title = QLabel("NOVAROMA"); title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {T('ORANGE')}; letter-spacing: 5px; background: transparent;")
        title.setAlignment(Qt.AlignCenter)

        sub = QLabel("Sistema de Gestão de Clientes"); sub.setFont(QFont("Segoe UI", 9))
        sub.setStyleSheet(f"color: {T('TEXT_DIM')}; letter-spacing: 2px; background: transparent;")
        sub.setAlignment(Qt.AlignCenter)

        # Glow label abaixo do logo
        glow_line = QFrame()
        glow_line.setFixedHeight(1)
        glow_line.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 transparent, stop:0.5 {T('ORANGE')}, stop:1 transparent);"
        )

        logo_area.addWidget(mark, alignment=Qt.AlignCenter)
        logo_area.addWidget(title)
        logo_area.addWidget(sub)
        lay.addLayout(logo_area)
        lay.addSpacing(8)
        lay.addWidget(glow_line)
        lay.addSpacing(24)

        # Card
        c = card()
        c.setStyleSheet(
            f"QFrame#card {{"
            f"  background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f"    stop:0 {T('CARD')}, stop:1 {T('CARD2')});"
            f"  border: 1px solid {T('BORDER2')};"
            f"  border-radius: 12px;"
            f"}}"
        )
        cl = QVBoxLayout(c); cl.setSpacing(12); cl.setContentsMargins(28,24,28,24)

        cl.addWidget(mono_label("USUÁRIO", 9, T("TEXT_DIM")))
        self.inp_user = QLineEdit(); self.inp_user.setPlaceholderText("Digite seu usuário"); self.inp_user.setFixedHeight(42)
        cl.addWidget(self.inp_user)

        cl.addWidget(mono_label("SENHA", 9, T("TEXT_DIM")))
        self.inp_pass = QLineEdit(); self.inp_pass.setEchoMode(QLineEdit.Password)
        self.inp_pass.setPlaceholderText("Digite sua senha"); self.inp_pass.setFixedHeight(42)
        self.inp_pass.returnPressed.connect(self._login); cl.addWidget(self.inp_pass)

        show_row = QHBoxLayout(); show_row.addStretch()
        chk = QCheckBox("Mostrar"); chk.toggled.connect(lambda c: self.inp_pass.setEchoMode(QLineEdit.Normal if c else QLineEdit.Password))
        show_row.addWidget(chk); cl.addLayout(show_row)

        self.lbl_err = QLabel(""); self.lbl_err.setStyleSheet(f"color: {T('DANGER')}; font-size: 11px; background: transparent;")
        self.lbl_err.setAlignment(Qt.AlignCenter); cl.addWidget(self.lbl_err)

        self.btn_login = QPushButton("ENTRAR"); self.btn_login.setFixedHeight(46)
        self.btn_login.setStyleSheet(
            f"QPushButton {{"
            f"  background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"    stop:0 {T('ORANGE_DIM')}, stop:1 {T('ORANGE')});"
            f"  color: #fff5ec; border-radius: 8px; font-size: 13px;"
            f"  font-weight: bold; letter-spacing: 4px;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"    stop:0 {T('ORANGE')}, stop:1 {T('ORANGE_GLO')});"
            f"}}"
        )
        self.btn_login.clicked.connect(self._login); cl.addWidget(self.btn_login)
        lay.addWidget(c)

        foot = QHBoxLayout(); foot.setAlignment(Qt.AlignCenter)
        foot.addWidget(mono_label("◆ NOVAROMA SOLUTIONS", 8, T("TEXT_DIM")))
        lay.addSpacing(16); lay.addLayout(foot)
        root.addWidget(center, alignment=Qt.AlignCenter)

    def _login(self):
        user = self.inp_user.text().strip(); senha = self.inp_pass.text()
        if not user or not senha: self.lbl_err.setText("Preencha usuário e senha."); return
        self.btn_login.setEnabled(False); self.btn_login.setText("VERIFICANDO..."); self.lbl_err.setText("")

        def _do():
            ok, msg = verificar_vps(user, senha)
            if not ok:
                self.btn_login.setEnabled(True); self.btn_login.setText("ENTRAR")
                self.lbl_err.setText(msg); return
            row = db_get_user(user)
            if row is None:
                row = db_criar_user(user, hash_senha(senha))
                if not row:
                    self.btn_login.setEnabled(True); self.btn_login.setText("ENTRAR")
                    self.lbl_err.setText("Erro ao criar conta."); return
            else:
                db_atualizar_senha(row["id"], hash_senha(senha))
            if not row.get("ativo", True):
                self.btn_login.setEnabled(True); self.btn_login.setText("ENTRAR")
                self.lbl_err.setText("Conta desativada. Contate a NovaRoma."); return
            validade = int(row.get("validade_dias", 30))
            if validade <= 0:
                self.btn_login.setEnabled(True); self.btn_login.setText("ENTRAR")
                self.lbl_err.setText("Plano expirado.")
                QTimer.singleShot(0, self._mostrar_renovar); return
            self.btn_login.setText("ENTRAR"); self.lbl_err.setText("")
            self.login_ok.emit(row["id"], row["username"], dict(row))

        threading.Thread(target=_do, daemon=True).start()

    def _mostrar_renovar(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Plano Expirado")
        msg.setText("Seu plano expirou.\nRenove para continuar usando o sistema.")
        btn_renovar = msg.addButton("Renovar Plano", QMessageBox.AcceptRole)
        msg.addButton("Fechar", QMessageBox.RejectRole)
        msg.exec_()
        if msg.clickedButton() == btn_renovar:
            webbrowser.open(GATEWAY_URL)


# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINAS DO SISTEMA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class PaginaClientes(QWidget):
    def __init__(self, usuario_id):
        super().__init__(); self.uid = usuario_id; self._filtro = "todos"; self._build(); self._carregar()

    def _build(self):
        lay = QVBoxLayout(self); lay.setSpacing(16); lay.setContentsMargins(28,24,28,24)
        top = QHBoxLayout()
        sf = QFrame()
        sf.setStyleSheet(
            f"background: {T('CARD2')}; border: 1px solid {T('BORDER2')}; border-radius: 8px;"
        )
        sl = QHBoxLayout(sf); sl.setContentsMargins(10,0,10,0)
        lupa = QLabel("🔍"); lupa.setStyleSheet("background: transparent; border: none;")
        self.inp_busca = QLineEdit(); self.inp_busca.setPlaceholderText("Pesquisar por nome, CPF, telefone...")
        self.inp_busca.setStyleSheet(f"border: none; background: transparent; color: {T('TEXT')}; font-size: 13px;")
        self.inp_busca.setFixedHeight(40); self.inp_busca.textChanged.connect(self._buscar)
        sl.addWidget(lupa); sl.addWidget(self.inp_busca)
        btn_novo = QPushButton("+ Novo Cliente"); btn_novo.setFixedHeight(40); btn_novo.clicked.connect(self._novo)
        top.addWidget(sf, 1); top.addSpacing(12); top.addWidget(btn_novo); lay.addLayout(top)
        fr = QHBoxLayout()
        for k, t in [("todos","Todos"),("Jurídico","Jurídico"),("Contábil","Contábil"),("Imóveis","Imóveis"),("Saúde","Saúde"),("Outro","Outro")]:
            b = QPushButton(t); b.setObjectName("btn_ghost"); b.setFixedHeight(28)
            b.setStyleSheet(b.styleSheet() + "font-size:10px; padding:0 12px;")
            b.clicked.connect(lambda _, kk=k: self._filtrar(kk)); fr.addWidget(b)
        fr.addStretch()
        self.lbl_total = mono_label("0 clientes", 9, T("TEXT_DIM")); fr.addWidget(self.lbl_total)
        lay.addLayout(fr)
        self.tabela = QTableWidget(); self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels(["NOME","🎂 ANIVERSÁRIO","IDADE","TELEFONE","CPF","TIPO","AÇÕES"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela.setColumnWidth(1,120); self.tabela.setColumnWidth(2,60)
        self.tabela.setColumnWidth(3,130); self.tabela.setColumnWidth(4,120)
        self.tabela.setColumnWidth(5,90); self.tabela.setColumnWidth(6,160)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setShowGrid(False); self.tabela.setFocusPolicy(Qt.NoFocus)
        self.tabela.verticalHeader().setDefaultSectionSize(46); lay.addWidget(self.tabela)

    def _carregar(self, txt=""):
        rows = db_listar_clientes(self.uid, self._filtro, txt)
        hoje = date.today()
        self.tabela.setRowCount(len(rows))
        self.lbl_total.setText(f"{len(rows)} cliente{'s' if len(rows)!=1 else ''}")
        for i, r in enumerate(rows):
            self.tabela.setItem(i, 0, QTableWidgetItem(r.get("nome") or ""))
            self.tabela.setItem(i, 2, QTableWidgetItem(str(r["idade"]) if r.get("idade") else "-"))
            self.tabela.setItem(i, 3, QTableWidgetItem(r.get("telefone") or "-"))
            self.tabela.setItem(i, 4, QTableWidgetItem(r.get("cpf") or "-"))
            ti = QTableWidgetItem(r.get("tipo_caso") or "-")
            ti.setForeground(QColor(T("ORANGE"))); self.tabela.setItem(i, 5, ti)
            dn = r.get("data_nascimento"); aniv = "-"; eh_hj = False
            if dn:
                try:
                    dt = datetime.strptime(dn, "%Y-%m-%d").date()
                    aniv = dt.strftime("%d/%m"); eh_hj = (dt.month == hoje.month and dt.day == hoje.day)
                except: pass
            ai = QTableWidgetItem(("🎂 " if eh_hj else "") + aniv)
            ai.setForeground(QColor("#CC8800" if eh_hj else T("TEXT_DIM")))
            ai.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft); self.tabela.setItem(i, 1, ai)
            cell = QWidget(); cell.setStyleSheet("background: transparent;")
            cl = QHBoxLayout(cell); cl.setContentsMargins(4,4,4,4); cl.setSpacing(4)
            be = QPushButton("Editar"); be.setFixedHeight(28); be.setObjectName("btn_ghost")
            be.clicked.connect(lambda _, rid=r["id"]: self._editar(rid))
            bx = QPushButton("X"); bx.setFixedSize(28,28); bx.setObjectName("btn_danger")
            bx.clicked.connect(lambda _, rid=r["id"], nm=r.get("nome",""): self._excluir(rid, nm))
            cl.addWidget(be); cl.addWidget(bx); cl.addStretch()
            self.tabela.setCellWidget(i, 6, cell)

    def _buscar(self, t): self._carregar(t)
    def _filtrar(self, k): self._filtro = k; self._carregar(self.inp_busca.text())
    def _novo(self):
        dlg = ClienteDialog(self.uid, parent=self.window())
        if dlg.exec_() == QDialog.Accepted:
            self._filtro = "todos"; self.inp_busca.clear(); self._carregar()
    def _editar(self, cid):
        dlg = ClienteDialog(self.uid, cid, parent=self.window())
        if dlg.exec_() == QDialog.Accepted: self._carregar()
    def _excluir(self, cid, nome):
        if QMessageBox.question(self.window(), "Confirmar", f"Excluir '{nome}'?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            db_excluir_cliente(cid); self._carregar()
    def atualizar(self): self._carregar(self.inp_busca.text())


class PaginaAniversarios(QWidget):
    def __init__(self, usuario_id):
        super().__init__(); self.uid = usuario_id; self._build(); self._carregar()

    def _build(self):
        lay = QVBoxLayout(self); lay.setSpacing(16); lay.setContentsMargins(28,24,28,24)
        h = QHBoxLayout()
        h.addWidget(section_label("Aniversariantes de Hoje"))
        h.addStretch()
        btn_enviar = QPushButton("🎉  Enviar Parabéns"); btn_enviar.clicked.connect(self._abrir_dialog)
        h.addWidget(btn_enviar); lay.addLayout(h)
        cfg = card(); cfg_lay = QHBoxLayout(cfg); cfg_lay.setContentsMargins(16,12,16,12)
        cfg_lay.addWidget(mono_label("Horário automático:", 9, T("TEXT_DIM")))
        self.lbl_horario = mono_label(get_config("horario_aniversario", "09:00"), 11, T("ORANGE"))
        cfg_lay.addWidget(self.lbl_horario); cfg_lay.addStretch()
        btn_cfg = QPushButton("Configurar"); btn_cfg.setObjectName("btn_ghost"); btn_cfg.setFixedHeight(28)
        btn_cfg.clicked.connect(self._config); cfg_lay.addWidget(btn_cfg)
        lay.addWidget(cfg)
        self.tabela = QTableWidget(); self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["NOME","TELEFONE","NASCIMENTO","STATUS"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela.setColumnWidth(1,140); self.tabela.setColumnWidth(2,110); self.tabela.setColumnWidth(3,120)
        self.tabela.verticalHeader().setVisible(False); self.tabela.setShowGrid(False)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.verticalHeader().setDefaultSectionSize(44); lay.addWidget(self.tabela)
        self.lbl_info = mono_label("", 9, T("TEXT_DIM")); self.lbl_info.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.lbl_info)

    def _carregar(self):
        hoje = date.today(); hoje_str = hoje.strftime("%Y-%m-%d")
        clientes = db_listar_clientes_aniv(self.uid)
        anivs = [c for c in clientes if c.get("data_nascimento") and
                 datetime.strptime(c["data_nascimento"], "%Y-%m-%d").month == hoje.month and
                 datetime.strptime(c["data_nascimento"], "%Y-%m-%d").day == hoje.day]
        self.tabela.setRowCount(len(anivs))
        for i, c in enumerate(anivs):
            self.tabela.setItem(i, 0, QTableWidgetItem(c["nome"]))
            self.tabela.setItem(i, 1, QTableWidgetItem(c.get("telefone") or "-"))
            try: dt = datetime.strptime(c["data_nascimento"], "%Y-%m-%d").date(); dn_txt = dt.strftime("%d/%m/%Y")
            except: dn_txt = c["data_nascimento"]
            self.tabela.setItem(i, 2, QTableWidgetItem(dn_txt))
            ja = log_ja_enviado(c["id"], hoje_str)
            st = QTableWidgetItem("✅ Enviado" if ja else "⏳ Pendente")
            st.setForeground(QColor(T("SUCCESS") if ja else T("WARNING"))); st.setTextAlignment(Qt.AlignCenter)
            self.tabela.setItem(i, 3, st)
        pendentes = sum(1 for c in anivs if not log_ja_enviado(c["id"], hoje_str))
        self.lbl_info.setText(f"{len(anivs)} aniversariante(s) hoje  ·  {pendentes} pendente(s)")
        self.lbl_horario.setText(get_config("horario_aniversario", "09:00"))

    def _abrir_dialog(self):
        dlg = AniversariosDialog(self.uid, self.window()); dlg.exec_(); self._carregar()

    def _config(self):
        dlg = BaseDialog("Config Aniversários", self.window(), 440)
        dlg.add_title("CONFIG ANIVERSÁRIOS")
        dlg._lay.addWidget(mono_label("NOME DA EMPRESA (na mensagem)", 9, T("TEXT_DIM")))
        inp_emp = QLineEdit(); inp_emp.setFixedHeight(36); inp_emp.setText(get_config("empresa_nome", "NovaRoma"))
        dlg._lay.addWidget(inp_emp)
        dlg._lay.addWidget(mono_label("HORÁRIO DO ENVIO AUTOMÁTICO", 9, T("TEXT_DIM")))
        te = QTimeEdit(); te.setDisplayFormat("HH:mm"); te.setFixedHeight(36)
        h = get_config("horario_aniversario", "09:00")
        try: hh, mm = h.split(":"); te.setTime(QTime(int(hh), int(mm)))
        except: te.setTime(QTime(9, 0))
        dlg._lay.addWidget(te)
        dlg._lay.addWidget(mono_label("TEXTO ADICIONAL (após mensagem padrão)", 9, T("TEXT_DIM")))
        txt_extra = QTextEdit(); txt_extra.setFixedHeight(80); txt_extra.setPlainText(get_config("aniversario_extra", ""))
        txt_extra.setPlaceholderText("Opcional: texto que aparece após a mensagem padrão de aniversário")
        dlg._lay.addWidget(txt_extra)
        prev = card(); prev_lay = QVBoxLayout(prev); prev_lay.setContentsMargins(12,10,12,10)
        prev_lay.addWidget(mono_label("PRÉVIA DA MENSAGEM:", 9, T("TEXT_DIM")))
        self._prev_lbl = QLabel(); self._prev_lbl.setWordWrap(True)
        self._prev_lbl.setStyleSheet(f"color: {T('TEXT_MID')}; font-size: 12px; background: transparent;")
        prev_lay.addWidget(self._prev_lbl); dlg._lay.addWidget(prev)
        def _update_prev():
            emp = inp_emp.text() or "NovaRoma"; extra = txt_extra.toPlainText()
            msg = f"Feliz Aniversário, [Nome]! 🎉🎂\nA equipe da {emp} deseja tudo de melhor para você neste dia especial! 🥳"
            if extra: msg += f"\n\n{extra}"
            self._prev_lbl.setText(msg)
        inp_emp.textChanged.connect(_update_prev); txt_extra.textChanged.connect(_update_prev); _update_prev()
        btns = QHBoxLayout()
        bc = QPushButton("Cancelar"); bc.setObjectName("btn_ghost"); bc.clicked.connect(dlg.reject)
        bs = QPushButton("Salvar")
        def _salvar():
            set_config("empresa_nome", inp_emp.text().strip() or "NovaRoma")
            t = te.time(); set_config("horario_aniversario", f"{t.hour():02d}:{t.minute():02d}")
            set_config("aniversario_extra", txt_extra.toPlainText().strip())
            dlg.accept(); self._carregar()
        bs.clicked.connect(_salvar); btns.addWidget(bc); btns.addWidget(bs); dlg._lay.addLayout(btns)
        dlg.exec_()

    def atualizar(self): self._carregar()


class PaginaMensagensAutomaticas(QWidget):
    def __init__(self, usuario_id):
        super().__init__()
        self.uid = usuario_id
        self._mensagens = []
        self._build()
        self._carregar()

    def _build(self):
        lay = QVBoxLayout(self); lay.setSpacing(16); lay.setContentsMargins(28,24,28,24)
        top = QHBoxLayout()
        top.addWidget(section_label("Mensagens Automáticas"))
        top.addStretch()
        btn_nova = QPushButton("+ Nova Mensagem Automática")
        btn_nova.setObjectName("btn_ghost"); btn_nova.setFixedHeight(34)
        btn_nova.clicked.connect(self._nova_mensagem)
        top.addWidget(btn_nova)
        lay.addLayout(top)
        lay.addWidget(mono_label("Crie e gerencie automações de mensagem por abas.", 10, T("TEXT_DIM")))
        self.tabs = QTabWidget(); self.tabs.setDocumentMode(True); self.tabs.setMovable(False)
        lay.addWidget(self.tabs)

    def _carregar(self):
        self._mensagens = get_mensagens_automaticas()
        self.tabs.clear()
        for msg in self._mensagens:
            self.tabs.addTab(self._criar_tab(msg), msg.get("title", "Mensagem"))

    def _resumo_destino(self, msg):
        if msg.get("target_mode") == "manual":
            qtd = len(msg.get("target_client_ids", []))
            return f"{qtd} cliente{'s' if qtd != 1 else ''} selecionado(s) manualmente"
        total = len(db_listar_clientes(self.uid))
        return f"Todos os clientes ({total})"

    def _selecionar_clientes(self, msg, lbl_destino):
        dlg = SelecionarClientesDialog(self.uid, msg.get("target_client_ids", []), self.window())
        if dlg.exec_() != QDialog.Accepted: return
        msg["target_client_ids"] = dlg.resultado
        msg["target_mode"] = "manual"
        lbl_destino.setText(self._resumo_destino(msg))

    def _enviar_agora(self, msg, titulo_widget=None, mensagem_widget=None, modo_manual=None, data_widget=None, hora_widget=None):
        conf = dict(msg)
        if titulo_widget is not None: conf["title"] = titulo_widget.text().strip() or conf.get("title") or "Mensagem"
        if mensagem_widget is not None: conf["message"] = mensagem_widget.toPlainText().strip() or conf.get("message") or ""
        if modo_manual is not None: conf["target_mode"] = "manual" if modo_manual.isChecked() else "all"
        if data_widget is not None:
            qd = data_widget.date(); conf["send_date"] = f"{qd.year():04d}-{qd.month():02d}-{qd.day():02d}"
        if hora_widget is not None:
            qt = hora_widget.time(); conf["send_time"] = f"{qt.hour():02d}:{qt.minute():02d}"
        if conf.get("target_mode") == "manual" and not conf.get("target_client_ids"):
            QMessageBox.warning(self.window(), "Aviso", "Selecione ao menos um cliente para envio manual."); return
        if not conf.get("message"):
            QMessageBox.warning(self.window(), "Aviso", "A mensagem não pode ficar vazia."); return
        resultado = enviar_mensagem_automatica(self.uid, conf)
        resumo = [f"Enviadas: {len(resultado['enviados'])}"]
        if resultado["sem_tel"]: resumo.append(f"Sem telefone: {len(resultado['sem_tel'])}")
        if resultado["erros"]: resumo.append(f"Erros: {len(resultado['erros'])}")
        QMessageBox.information(self.window(), "Envio concluído", "\n".join(resumo))

    def _criar_tab(self, msg):
        w = QWidget()
        lay = QVBoxLayout(w); lay.setSpacing(10); lay.setContentsMargins(12,12,12,12)

        lay.addWidget(mono_label("TÍTULO", 9, T("TEXT_DIM")))
        inp_titulo = QLineEdit(); inp_titulo.setFixedHeight(34)
        inp_titulo.setText(msg.get("title", "")); inp_titulo.setReadOnly(True)
        lay.addWidget(inp_titulo)

        lay.addWidget(mono_label("MENSAGEM", 9, T("TEXT_DIM")))
        txt_msg = QTextEdit(); txt_msg.setFixedHeight(140)
        txt_msg.setPlainText(msg.get("message", ""))
        txt_msg.setPlaceholderText("Use {nome} e {empresa} quando precisar de campos dinâmicos.")
        txt_msg.setReadOnly(True)
        lay.addWidget(txt_msg)

        card_destino = card(); dl = QVBoxLayout(card_destino); dl.setContentsMargins(12,10,12,10); dl.setSpacing(8)
        dl.addWidget(mono_label("DESTINATÁRIOS", 9, T("TEXT_DIM")))
        modo_row = QHBoxLayout()
        rb_todos = QRadioButton("Enviar para todos")
        rb_manual = QRadioButton("Selecionar clientes manualmente")
        group = QButtonGroup(card_destino); group.addButton(rb_todos); group.addButton(rb_manual)
        rb_manual.setChecked(msg.get("target_mode") == "manual")
        rb_todos.setChecked(msg.get("target_mode") != "manual")
        rb_todos.setEnabled(False); rb_manual.setEnabled(False)
        modo_row.addWidget(rb_todos); modo_row.addWidget(rb_manual); modo_row.addStretch()
        dl.addLayout(modo_row)
        row_sel = QHBoxLayout()
        lbl_destino = mono_label(self._resumo_destino(msg), 9, T("TEXT_MID"))
        btn_sel = QPushButton("Selecionar Clientes"); btn_sel.setObjectName("btn_ghost"); btn_sel.setFixedHeight(30)
        btn_sel.setEnabled(False)
        btn_sel.clicked.connect(lambda: self._selecionar_clientes(msg, lbl_destino))
        row_sel.addWidget(lbl_destino, 1); row_sel.addWidget(btn_sel)
        dl.addLayout(row_sel); lay.addWidget(card_destino)

        card_agenda = card(); al = QVBoxLayout(card_agenda); al.setContentsMargins(12,10,12,10); al.setSpacing(8)
        al.addWidget(mono_label("AGENDAMENTO", 9, T("TEXT_DIM")))
        agenda_row = QHBoxLayout()
        dte_envio = QDateEdit(); dte_envio.setCalendarPopup(True); dte_envio.setDisplayFormat("dd/MM/yyyy"); dte_envio.setFixedHeight(30)
        te_envio = QTimeEdit(); te_envio.setDisplayFormat("HH:mm"); te_envio.setFixedHeight(30)
        if msg.get("send_date"):
            try:
                dt_envio = datetime.strptime(msg.get("send_date"), "%Y-%m-%d")
                dte_envio.setDate(QDate(dt_envio.year, dt_envio.month, dt_envio.day))
            except: dte_envio.setDate(QDate.currentDate())
        else: dte_envio.setDate(QDate.currentDate())
        if msg.get("send_time"):
            try:
                hh, mm = msg.get("send_time").split(":")
                te_envio.setTime(QTime(int(hh), int(mm)))
            except: te_envio.setTime(QTime.currentTime())
        else: te_envio.setTime(QTime.currentTime())
        dte_envio.setEnabled(False); te_envio.setEnabled(False)
        btn_edit_data = QPushButton("Editar Data de Envio"); btn_edit_data.setObjectName("btn_ghost"); btn_edit_data.setFixedHeight(30)
        agenda_row.addWidget(dte_envio); agenda_row.addWidget(te_envio); agenda_row.addWidget(btn_edit_data)
        al.addLayout(agenda_row); lay.addWidget(card_agenda)

        if msg.get("id") == "aniversariantes":
            extra = card(); ex = QVBoxLayout(extra); ex.setContentsMargins(12,10,12,10); ex.setSpacing(8)
            ex.addWidget(mono_label("CONFIGURAÇÃO DE DISPARO", 9, T("TEXT_DIM")))
            linha = QHBoxLayout()
            chk_ativo = QCheckBox("Ativar envio automático")
            chk_ativo.setChecked(get_config("aniversario_ativo", "1") == "1"); chk_ativo.setEnabled(False)
            linha.addWidget(chk_ativo); linha.addStretch()
            linha.addWidget(mono_label("Horário", 9, T("TEXT_DIM")))
            te = QTimeEdit(); te.setDisplayFormat("HH:mm"); te.setFixedHeight(30)
            h = get_config("horario_aniversario", "09:00")
            try: hh, mm = h.split(":"); te.setTime(QTime(int(hh), int(mm)))
            except: te.setTime(QTime(9, 0))
            te.setEnabled(False); linha.addWidget(te)
            ex.addLayout(linha)
            ex.addWidget(mono_label("Esta aba já vem integrada por padrão.", 9, T("TEXT_DIM")))
            lay.addWidget(extra)
        else:
            chk_ativo = None; te = None

        btns = QHBoxLayout()
        btn_editar = QPushButton("Editar"); btn_editar.setObjectName("btn_ghost"); btn_editar.setFixedHeight(34)
        btns.addWidget(btn_editar)
        btn_salvar = QPushButton("Salvar"); btn_salvar.setFixedHeight(34); btn_salvar.setEnabled(False)
        btns.addWidget(btn_salvar)
        btn_enviar_agora = QPushButton("Enviar Agora"); btn_enviar_agora.setObjectName("btn_ghost"); btn_enviar_agora.setFixedHeight(34)
        btns.addWidget(btn_enviar_agora)
        btn_excluir = None
        if not msg.get("integrada"):
            btn_excluir = QPushButton("Excluir Aba"); btn_excluir.setObjectName("btn_danger"); btn_excluir.setFixedHeight(34)
            btns.addWidget(btn_excluir)
        btns.addStretch(); lay.addLayout(btns); lay.addStretch()

        def _set_edit_mode(editando):
            inp_titulo.setReadOnly(not editando); txt_msg.setReadOnly(not editando)
            rb_todos.setEnabled(editando); rb_manual.setEnabled(editando)
            btn_sel.setEnabled(editando and rb_manual.isChecked())
            dte_envio.setEnabled(editando); te_envio.setEnabled(editando); btn_edit_data.setEnabled(editando)
            if chk_ativo is not None: chk_ativo.setEnabled(editando)
            if te is not None: te.setEnabled(editando)
            btn_salvar.setEnabled(editando)
            btn_editar.setText("Cancelar" if editando else "Editar")

        rb_manual.toggled.connect(lambda checked: btn_sel.setEnabled(estado["editando"] and checked))
        estado = {"editando": False}

        def _toggle_edicao():
            if estado["editando"]:
                inp_titulo.setText(msg.get("title", "")); txt_msg.setPlainText(msg.get("message", ""))
                if chk_ativo is not None: chk_ativo.setChecked(get_config("aniversario_ativo", "1") == "1")
                if te is not None:
                    h2 = get_config("horario_aniversario", "09:00")
                    try: hh2, mm2 = h2.split(":"); te.setTime(QTime(int(hh2), int(mm2)))
                    except: te.setTime(QTime(9, 0))
                estado["editando"] = False; _set_edit_mode(False); return
            estado["editando"] = True; _set_edit_mode(True)

        def _salvar_tab():
            titulo = inp_titulo.text().strip() or "Mensagem"
            conteudo = txt_msg.toPlainText().strip()
            if not conteudo: QMessageBox.warning(self.window(), "Aviso", "A mensagem não pode ficar vazia."); return
            msg["title"] = titulo; msg["message"] = conteudo
            msg["target_mode"] = "manual" if rb_manual.isChecked() else "all"
            msg["target_client_ids"] = [int(cid) for cid in msg.get("target_client_ids", []) if str(cid).isdigit()]
            qd = dte_envio.date(); msg["send_date"] = f"{qd.year():04d}-{qd.month():02d}-{qd.day():02d}"
            qt = te_envio.time(); msg["send_time"] = f"{qt.hour():02d}:{qt.minute():02d}"
            if msg["target_mode"] == "manual" and not msg["target_client_ids"]:
                QMessageBox.warning(self.window(), "Aviso", "Selecione clientes para o envio manual."); return
            if chk_ativo is not None: set_config("aniversario_ativo", "1" if chk_ativo.isChecked() else "0")
            if te is not None:
                t2 = te.time(); set_config("horario_aniversario", f"{t2.hour():02d}:{t2.minute():02d}")
            salvar_mensagens_automaticas(self._mensagens)
            idx = self.tabs.indexOf(w)
            if idx >= 0: self.tabs.setTabText(idx, titulo)
            estado["editando"] = False; _set_edit_mode(False)
            QMessageBox.information(self.window(), "Salvo", "Mensagem automática salva com sucesso.")

        def _excluir_tab():
            if QMessageBox.question(self.window(), "Confirmar", "Excluir esta mensagem automática?",
                                    QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes: return
            self._mensagens = [m for m in self._mensagens if m.get("id") != msg.get("id")]
            salvar_mensagens_automaticas(self._mensagens); self._carregar()

        btn_editar.clicked.connect(_toggle_edicao)
        btn_salvar.clicked.connect(_salvar_tab)
        btn_enviar_agora.clicked.connect(lambda: self._enviar_agora(msg, inp_titulo, txt_msg, rb_manual, dte_envio, te_envio))
        if btn_excluir: btn_excluir.clicked.connect(_excluir_tab)
        return w

    def _nova_mensagem(self):
        base = "mensagem"; i = 1
        used = {m.get("id") for m in self._mensagens}
        while f"{base}_{i}" in used: i += 1
        self._mensagens.append({
            "id": f"{base}_{i}", "title": f"Mensagem {i}",
            "message": "Digite aqui sua mensagem automática.",
            "integrada": False, "target_mode": "all", "target_client_ids": [],
            "send_date": "", "send_time": "", "last_sent_at": "",
        })
        salvar_mensagens_automaticas(self._mensagens); self._carregar()
        self.tabs.setCurrentIndex(self.tabs.count() - 1)

    def atualizar(self): pass


class PaginaIAAssistente(QWidget):
    def __init__(self):
        super().__init__(); self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setSpacing(0); lay.setContentsMargins(0,0,0,0)
        h = QFrame(); h.setStyleSheet(f"background: {T('BG2')}; border-bottom: 1px solid {T('BORDER')};")
        hl = QHBoxLayout(h); hl.setContentsMargins(20,12,20,12)
        hl.addWidget(section_label("IA Assistente")); hl.addStretch()
        btn_wz = QPushButton("● Disponível no WhatsApp")
        btn_wz.setStyleSheet(f"""
            QPushButton {{
                background: rgba(46,204,113,0.10); border: 1px solid {T('SUCCESS')};
                color: {T('SUCCESS')}; border-radius: 100px; padding: 6px 14px;
                font-size: 11px; font-weight: bold;
            }}
            QPushButton:hover {{ background: rgba(46,204,113,0.20); }}
        """)
        btn_wz.clicked.connect(self._abrir_wz); hl.addWidget(btn_wz)
        lay.addWidget(h)
        self.chat_area = QScrollArea(); self.chat_area.setWidgetResizable(True)
        self.chat_area.setStyleSheet("border: none; background: transparent;")
        self.chat_container = QWidget()
        self.chat_lay = QVBoxLayout(self.chat_container)
        self.chat_lay.setSpacing(12); self.chat_lay.setContentsMargins(24,16,24,16)
        self.chat_lay.addStretch()
        self.chat_area.setWidget(self.chat_container); lay.addWidget(self.chat_area, 1)
        self._add_msg("IA", "Olá! Sou a IA da NovaRoma. Em breve estarei totalmente integrada para ajudar você a gerir seus clientes, gerar relatórios e muito mais. Fique ligado nas atualizações! 🤖")
        inp_frame = QFrame(); inp_frame.setStyleSheet(f"background: {T('BG2')}; border-top: 1px solid {T('BORDER')};")
        ifl = QHBoxLayout(inp_frame); ifl.setContentsMargins(20,12,20,12); ifl.setSpacing(10)
        self.inp_chat = QLineEdit(); self.inp_chat.setPlaceholderText("Digite uma mensagem para a IA...")
        self.inp_chat.setFixedHeight(40); self.inp_chat.returnPressed.connect(self._enviar)
        btn_send = QPushButton("Enviar"); btn_send.setFixedHeight(40); btn_send.setFixedWidth(90)
        btn_send.clicked.connect(self._enviar)
        ifl.addWidget(self.inp_chat); ifl.addWidget(btn_send); lay.addWidget(inp_frame)

    def _add_msg(self, role, txt):
        row = QHBoxLayout()
        bubble = QLabel(txt); bubble.setWordWrap(True); bubble.setMaximumWidth(520)
        if role == "IA":
            bubble.setStyleSheet(f"background: {T('CARD')}; border: 1px solid {T('BORDER2')}; border-radius: 10px; padding: 10px 14px; color: {T('TEXT_MID')}; font-size: 13px;")
            row.addWidget(bubble); row.addStretch()
        else:
            bubble.setStyleSheet(f"background: rgba(224,120,40,0.10); border: 1px solid rgba(224,120,40,0.22); border-radius: 10px; padding: 10px 14px; color: {T('TEXT')}; font-size: 13px; font-style: italic;")
            row.addStretch(); row.addWidget(bubble)
        self.chat_lay.insertLayout(self.chat_lay.count()-1, row)

    def _enviar(self):
        txt = self.inp_chat.text().strip()
        if not txt: return
        self._add_msg("USER", txt); self.inp_chat.clear()
        QTimer.singleShot(600, lambda: self._add_msg("IA", "🤖 IA em breve integrada! Por enquanto, estou em desenvolvimento."))
        QTimer.singleShot(100, lambda: self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum()))

    def _abrir_wz(self):
        msg = "Olá! Preciso de ajuda com meu sistema NovaRoma."
        url = f"https://wa.me/{AGENTE_WHATSAPP}?text={urllib.parse.quote(msg)}"
        webbrowser.open(url)

    def atualizar(self): pass


class PaginaRelatorios(QWidget):
    def __init__(self, usuario_id):
        super().__init__(); self.uid = usuario_id; self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setSpacing(16); lay.setContentsMargins(28,24,28,24)
        h = QHBoxLayout(); h.addWidget(section_label("Relatórios")); h.addStretch()
        btn_export_xlsx = QPushButton("📊  Exportar Excel")
        btn_export_pdf = QPushButton("🧾  Exportar PDF")
        btn_export_xlsx.clicked.connect(self._exportar_excel)
        btn_export_pdf.clicked.connect(self._exportar_pdf)
        h.addWidget(btn_export_xlsx); h.addWidget(btn_export_pdf); lay.addLayout(h)
        lay.addWidget(mono_label("Exporte sua base de clientes em Excel ou PDF.", 10, T("TEXT_DIM")))
        lay.addStretch()

    def atualizar(self): pass

    def _exportar_excel(self):
        path, _ = QFileDialog.getSaveFileName(self.window(), "Exportar Clientes", "clientes_novaroma.xlsx", "Excel (*.xlsx)")
        if not path: return
        try:
            import openpyxl
            wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Clientes"
            headers = ["Nome","Idade","Sexo","Telefone","CPF","Tipo de Caso","Observações","Data de Nascimento","Criado Em"]
            ws.append(headers)
            for r in db_listar_clientes(self.uid):
                ws.append([r.get("nome",""), r.get("idade",""), r.get("sexo",""), r.get("telefone",""),
                           r.get("cpf",""), r.get("tipo_caso",""), r.get("observacoes",""),
                           r.get("data_nascimento",""), r.get("criado_em","")[:10] if r.get("criado_em") else ""])
            wb.save(path)
            QMessageBox.information(self.window(), "Exportado", f"Planilha salva em:\n{path}")
        except ImportError:
            QMessageBox.warning(self.window(), "Dependência", "Instale openpyxl:\npip install openpyxl")
        except Exception as e:
            QMessageBox.critical(self.window(), "Erro", str(e))

    def _exportar_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self.window(), "Exportar Clientes (PDF)", "clientes_novaroma.pdf", "PDF (*.pdf)")
        if not path: return
        if not path.lower().endswith(".pdf"): path += ".pdf"
        rows = db_listar_clientes(self.uid)
        html_rows = []
        for r in rows:
            dn = r.get("data_nascimento") or "-"
            if dn != "-":
                try: dn = datetime.strptime(dn, "%Y-%m-%d").strftime("%d/%m/%Y")
                except: pass
            html_rows.append(
                "<tr>"
                f"<td>{html.escape(str(r.get('nome') or ''))}</td>"
                f"<td>{html.escape(str(r.get('idade') if r.get('idade') is not None else '-'))}</td>"
                f"<td>{html.escape(str(r.get('telefone') or '-'))}</td>"
                f"<td>{html.escape(str(r.get('cpf') or '-'))}</td>"
                f"<td>{html.escape(str(r.get('tipo_caso') or '-'))}</td>"
                f"<td>{html.escape(str(dn))}</td>"
                "</tr>"
            )
        doc = QTextDocument()
        doc.setHtml(f"""
            <html><head><meta charset='utf-8'>
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 11px; color: #111; }}
                h1 {{ font-size: 16px; margin-bottom: 4px; }}
                .meta {{ color: #666; margin-bottom: 14px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #d9d9d9; padding: 6px; text-align: left; }}
                th {{ background: #f3f3f3; }}
            </style></head>
            <body>
                <h1>NovaRoma - Relatorio de Clientes</h1>
                <div class='meta'>Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} | Total: {len(rows)}</div>
                <table><thead><tr>
                    <th>Nome</th><th>Idade</th><th>Telefone</th><th>CPF</th><th>Tipo</th><th>Aniversario</th>
                </tr></thead><tbody>{''.join(html_rows)}</tbody></table>
            </body></html>
        """)
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat); printer.setOutputFileName(path)
        doc.print_(printer)
        QMessageBox.information(self.window(), "Exportado", f"PDF salvo em:\n{path}")


class PaginaConfiguracoes(QWidget):
    tema_changed = pyqtSignal(bool)

    def __init__(self, usuario_id, username):
        super().__init__(); self.uid = usuario_id; self.username = username; self._build()

    def _build(self):
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("border: none;")
        inner = QWidget(); lay = QVBoxLayout(inner); lay.setSpacing(16); lay.setContentsMargins(28,24,28,24)
        lay.addWidget(section_label("Configurações"))

        c_tema = card(); ct = QVBoxLayout(c_tema); ct.setContentsMargins(20,16,20,16); ct.setSpacing(12)
        ct.addWidget(mono_label("TEMA", 10, T("TEXT")))
        tr = QHBoxLayout()
        self.btn_dark  = QPushButton("🌙  Escuro"); self.btn_dark.setObjectName("btn_ghost")
        self.btn_light = QPushButton("☀️  Claro"); self.btn_light.setObjectName("btn_ghost")
        for btn in [self.btn_dark, self.btn_light]: btn.setFixedHeight(36)
        tema_atual = get_config("tema", "dark")
        self._mark_tema(tema_atual == "dark")
        self.btn_dark.clicked.connect(lambda: self._set_tema(True))
        self.btn_light.clicked.connect(lambda: self._set_tema(False))
        tr.addWidget(self.btn_dark); tr.addWidget(self.btn_light); tr.addStretch()
        ct.addLayout(tr); lay.addWidget(c_tema)

        c_dp = card(); cdp = QVBoxLayout(c_dp); cdp.setContentsMargins(20,16,20,16); cdp.setSpacing(10)
        cdp.addWidget(mono_label("DADOS PESSOAIS", 10, T("TEXT")))
        cdp.addWidget(mono_label(f"Usuário: {self.username}", 10, T("TEXT_MID")))
        self._dp_stack = QStackedWidget(); self._dp_stack.setStyleSheet("background: transparent;")
        self._dp_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        dp_home = QWidget(); dp_home_l = QVBoxLayout(dp_home); dp_home_l.setContentsMargins(0,0,0,0); dp_home_l.setSpacing(8)
        dp_home.setStyleSheet("background: transparent;")
        btn_dados = QPushButton("Abrir Dados Pessoais"); btn_dados.setObjectName("btn_link"); btn_dados.setFixedHeight(26)
        btn_dados.clicked.connect(lambda: self._set_dp_tab(1)); dp_home_l.addWidget(btn_dados)
        dp_opts = QWidget(); dp_opts_l = QVBoxLayout(dp_opts); dp_opts_l.setContentsMargins(0,0,0,0); dp_opts_l.setSpacing(8)
        dp_opts.setStyleSheet("background: transparent;")
        dp_opts_l.addWidget(mono_label("Escolha uma ação:", 9, T("TEXT_DIM")))
        btn_senha = QPushButton("Trocar Senha"); btn_senha.setObjectName("btn_ghost"); btn_senha.setFixedHeight(30)
        btn_senha.clicked.connect(self._alterar_senha)
        btn_email = QPushButton("Alterar E-mail"); btn_email.setObjectName("btn_ghost"); btn_email.setFixedHeight(30)
        btn_email.clicked.connect(self._alterar_email)
        btn_voltar = QPushButton("Voltar"); btn_voltar.setObjectName("btn_ghost"); btn_voltar.setFixedHeight(30)
        btn_voltar.clicked.connect(lambda: self._set_dp_tab(0))
        dp_opts_l.addWidget(btn_senha); dp_opts_l.addWidget(btn_email); dp_opts_l.addWidget(btn_voltar)
        self._dp_stack.addWidget(dp_home); self._dp_stack.addWidget(dp_opts)
        self._set_dp_tab(0); cdp.addWidget(self._dp_stack); lay.addWidget(c_dp)

        c_plano = card(); cpl = QVBoxLayout(c_plano); cpl.setContentsMargins(20,16,20,16); cpl.setSpacing(12)
        cpl.addWidget(mono_label("PLANO", 10, T("TEXT")))
        plano_atual = get_config("plano_usuario", "mensal")
        nome_plano = "Quinzenal" if plano_atual == "quinzenal" else "Mensal"
        cpl.addWidget(mono_label(f"Plano atual: {nome_plano}", 10, T("SUCCESS")))
        btn_renovar = QPushButton("🔗  Renovar / Gerenciar Plano"); btn_renovar.setObjectName("btn_ghost")
        btn_renovar.setFixedHeight(34); btn_renovar.clicked.connect(lambda: webbrowser.open(GATEWAY_URL))
        cpl.addWidget(btn_renovar); lay.addWidget(c_plano)

        c_sair = card(); cs = QVBoxLayout(c_sair); cs.setContentsMargins(20,16,20,16)
        cs.addWidget(mono_label("SESSÃO", 10, T("TEXT")))
        btn_sair = QPushButton("Sair da Conta"); btn_sair.setObjectName("btn_danger"); btn_sair.setFixedHeight(36)
        btn_sair.clicked.connect(self._sair); cs.addWidget(btn_sair); lay.addWidget(c_sair)
        lay.addStretch(); scroll.setWidget(inner)
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.addWidget(scroll)

    def _mark_tema(self, dark):
        base_dark  = f"background: rgba(224,120,40,0.15); border: 1px solid {T('ORANGE')}; color: {T('ORANGE')};"
        base_ghost = f"background: transparent; border: 1px solid {T('BORDER2')}; color: {T('TEXT_MID')};"
        self.btn_dark.setStyleSheet(f"QPushButton {{ {base_dark if dark else base_ghost} border-radius: 6px; padding: 8px 16px; }}")
        self.btn_light.setStyleSheet(f"QPushButton {{ {base_ghost if dark else base_dark} border-radius: 6px; padding: 8px 16px; }}")

    def _set_tema(self, dark):
        set_config("tema", "dark" if dark else "light")
        self._mark_tema(dark); self.tema_changed.emit(dark)

    def _set_dp_tab(self, idx):
        self._dp_stack.setCurrentIndex(idx)
        self._dp_stack.setFixedHeight(34 if idx == 0 else 140)

    def _alterar_senha(self): DadosPessoaisDialog(self.uid, self.username, self.window()).exec_()
    def _alterar_email(self):
        user = db_get_user(self.username) or {}
        AlterarEmailDialog(self.uid, user.get("email", ""), self.window()).exec_()

    def _sair(self):
        if QMessageBox.question(self.window(), "Sair", "Deseja sair da conta?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.window().sair()

    def atualizar(self): pass


# ══════════════════════════════════════════════════════════════════════════════
#  JANELA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, usuario_id, username, user_row):
        super().__init__()
        self.uid = usuario_id; self.username = username; self.user_row = user_row
        self.setWindowTitle("NovaRoma — Sistema de Gestão")
        self.setMinimumSize(1060, 640)
        self._build()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check_horario)
        self._timer.start(60_000)

    def _build(self):
        root = QWidget(); self.setCentralWidget(root)
        main = QHBoxLayout(root); main.setSpacing(0); main.setContentsMargins(0,0,0,0)

        # ── SIDEBAR ──
        self.sidebar = QFrame(); self.sidebar.setObjectName("sidebar"); self.sidebar.setFixedWidth(230)
        sb = QVBoxLayout(self.sidebar); sb.setSpacing(2); sb.setContentsMargins(12,16,12,16)

        # Logo
        logo_row = QHBoxLayout()
        mark = QLabel("N"); mark.setFont(QFont("Segoe UI", 11, QFont.Bold))
        mark.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {T('ORANGE_DIM')}, stop:1 {T('ORANGE')});"
            f"color: #fff5ec; border-radius: 6px; padding: 4px 8px;"
        )
        mark.setFixedSize(28, 28); mark.setAlignment(Qt.AlignCenter)
        logo_txt = QLabel("NOVAROMA"); logo_txt.setFont(QFont("Segoe UI", 11, QFont.Bold))
        logo_txt.setStyleSheet(f"color: {T('ORANGE')}; letter-spacing: 2px; background: transparent;")
        logo_row.addWidget(mark); logo_row.addWidget(logo_txt); logo_row.addStretch()
        sb.addLayout(logo_row); sb.addSpacing(20); sb.addWidget(divider()); sb.addSpacing(8)

        # Nav items
        self._nav_btns = {}
        nav_items = [
            ("clientes",      "Clientes",        "👥"),
            ("msgs_auto",     "Mensagens Auto",  "⚡"),
            ("ia",            "IA Assistente",   "🤖"),
            ("relatorios",    "Relatórios",      "📊"),
            ("configuracoes", "Configurações",   "⚙"),
        ]
        for key, label, ico in nav_items:
            btn = QPushButton(f"{ico}  {label}"); btn.setObjectName("btn_sidebar")
            btn.setFixedHeight(38); btn.setProperty("active", "false")
            btn.clicked.connect(lambda _, k=key: self.ir_para(k))
            self._nav_btns[key] = btn; sb.addWidget(btn)

        sb.addStretch()
        self.lbl_aniv_badge = QLabel("")
        self.lbl_aniv_badge.setStyleSheet(f"color: {T('WARNING')}; font-size: 11px; background: transparent;")
        self.lbl_aniv_badge.setAlignment(Qt.AlignCenter); sb.addWidget(self.lbl_aniv_badge)
        sb.addWidget(divider())
        usr_lbl = mono_label(self.username.upper(), 9, T("TEXT_DIM"))
        usr_lbl.setAlignment(Qt.AlignCenter); sb.addWidget(usr_lbl)

        main.addWidget(self.sidebar)

        # ── STACK ──
        self.stack = QStackedWidget(); main.addWidget(self.stack, 1)
        self.pag_clientes   = PaginaClientes(self.uid)
        self.pag_msgs_auto  = PaginaMensagensAutomaticas(self.uid)
        self.pag_ia         = PaginaIAAssistente()
        self.pag_relatorios = PaginaRelatorios(self.uid)
        self.pag_config     = PaginaConfiguracoes(self.uid, self.username)
        self.pag_config.tema_changed.connect(self._aplicar_tema)

        for p in [self.pag_clientes, self.pag_msgs_auto, self.pag_ia, self.pag_relatorios, self.pag_config]:
            self.stack.addWidget(p)

        self._pages = {
            "clientes":      (self.pag_clientes,   0),
            "msgs_auto":     (self.pag_msgs_auto,  1),
            "ia":            (self.pag_ia,         2),
            "relatorios":    (self.pag_relatorios, 3),
            "configuracoes": (self.pag_config,     4),
        }
        self.ir_para("clientes")
        self._atualizar_badge()

    def ir_para(self, key):
        if key not in self._pages: return
        pag, idx = self._pages[key]
        self.stack.setCurrentIndex(idx)
        for k, btn in self._nav_btns.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn); btn.style().polish(btn)
        if hasattr(pag, "atualizar"): pag.atualizar()

    def _atualizar_badge(self):
        hoje = date.today()
        clientes = db_listar_clientes_aniv(self.uid)
        count = sum(1 for c in clientes if c.get("data_nascimento") and
                    datetime.strptime(c["data_nascimento"], "%Y-%m-%d").month == hoje.month and
                    datetime.strptime(c["data_nascimento"], "%Y-%m-%d").day == hoje.day)
        self.lbl_aniv_badge.setText(f"🎂 {count} aniversário(s) hoje" if count > 0 else "")

    def _check_horario(self):
        agora = datetime.now(); horario = get_config("horario_aniversario", "09:00")
        try:
            h, m = horario.split(":")
            if agora.hour == int(h) and agora.minute == int(m):
                threading.Thread(target=self._auto_aniv, daemon=True).start()
        except: pass
        threading.Thread(target=self._auto_msgs, daemon=True).start()
        self._atualizar_badge()

    def _auto_aniv(self):
        r = verificar_e_enviar_aniversarios(self.uid)
        if r.get("enviados"):
            nomes = ", ".join(r["enviados"]); orig = self.windowTitle()
            self.setWindowTitle(f"🎂 Parabéns enviados: {nomes}")
            QTimer.singleShot(8000, lambda: self.setWindowTitle(orig))

    def _auto_msgs(self): processar_mensagens_agendadas(self.uid)

    def _aplicar_tema(self, dark):
        set_theme(dark)
        QApplication.instance().setStyleSheet(build_qss())
        self._refresh_inline_theme_colors()
        for btn in self._nav_btns.values():
            btn.style().unpolish(btn); btn.style().polish(btn)
        if hasattr(self, "lbl_aniv_badge"):
            self.lbl_aniv_badge.setStyleSheet(f"color: {T('WARNING')}; font-size: 11px; background: transparent;")
        if hasattr(self, "pag_config") and hasattr(self.pag_config, "_mark_tema"):
            self.pag_config._mark_tema(dark)

    def _refresh_inline_theme_colors(self):
        keys = ["BG","BG2","CARD","CARD2","BORDER","BORDER2","TEXT","TEXT_DIM","TEXT_MID",
                "ORANGE","ORANGE_DIM","ORANGE_GLO","SUCCESS","DANGER","WARNING","CYAN"]
        replace_map = {}
        for k in keys:
            replace_map[DARK_THEME[k]] = T(k)
            replace_map[LIGHT_THEME[k]] = T(k)
        for w in self.findChildren(QWidget):
            ss = w.styleSheet()
            if not ss: continue
            new_ss = ss
            for old_color, new_color in replace_map.items():
                new_ss = new_ss.replace(old_color, new_color)
            if new_ss != ss: w.setStyleSheet(new_ss)

    def sair(self): self.logout_requested.emit()


# ══════════════════════════════════════════════════════════════════════════════
#  APP CONTROLLER
# ══════════════════════════════════════════════════════════════════════════════

class AppController(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NovaRoma"); self.resize(440, 600)
        self.stack = QStackedWidget()
        lay = QVBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.addWidget(self.stack)
        self.login = LoginWidget()
        self.login.login_ok.connect(self._ao_logar)
        self.stack.addWidget(self.login)
        self.main_win = None

    def _ao_logar(self, uid, username, user_row):
        if self.main_win is not None:
            try: self.main_win.close()
            except: pass
            self.main_win = None
        self.main_win = MainWindow(uid, username, user_row)
        self.main_win.logout_requested.connect(self._ao_deslogar)
        self.main_win.show(); self.hide()

    def _ao_deslogar(self):
        if self.main_win is not None:
            self.main_win.hide(); self.main_win.deleteLater(); self.main_win = None
        self.login.inp_user.clear(); self.login.inp_pass.clear()
        self.show(); self.resize(440, 600)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    tema_salvo = get_config("tema", "dark")
    set_theme(tema_salvo == "dark")
    app = QApplication(sys.argv)
    app.setStyleSheet(build_qss())
    app.setApplicationName("NovaRoma")
    ctrl = AppController()
    ctrl.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
