from __future__ import annotations
import json, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
APP_NAME='AI Service Business Receptionist'
DB_FILE=Path(__file__).resolve().parent.parent/'data'/'app.sqlite'
DB_FILE.parent.mkdir(exist_ok=True)
app=FastAPI(title=APP_NAME, version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

def db() -> sqlite3.Connection:
    conn=sqlite3.connect(DB_FILE); conn.row_factory=sqlite3.Row; conn.execute('pragma journal_mode=wal'); return conn
def init_db() -> None:
    with db() as conn: conn.execute('create table if not exists records (id integer primary key autoincrement, kind text not null, title text not null, payload text not null, created_at text not null)')
init_db()
def save_record(kind: str, title: str, payload: str) -> int:
    with db() as conn:
        cur=conn.execute('insert into records(kind,title,payload,created_at) values (?,?,?,?)',(kind,title,payload,datetime.now(timezone.utc).isoformat())); return int(cur.lastrowid)
def rows(kind: str | None = None) -> list[dict[str, Any]]:
    with db() as conn:
        data=conn.execute('select * from records where kind=? order by id desc',(kind,)).fetchall() if kind else conn.execute('select * from records order by id desc').fetchall()
    return [dict(r) for r in data]
@app.get('/api/health')
def health(): return {'ok': True, 'app': APP_NAME, 'records': len(rows())}
@app.get('/', response_class=HTMLResponse)
def home(): return INDEX_HTML

class IntakeRequest(BaseModel):
    customer_name: str
    phone: str
    service_needed: str
    message: str
    preferred_time: str = "ASAP"
def urgency(text: str) -> str:
    t=text.lower()
    if any(w in t for w in ['emergency','urgent','leak','flood','no heat','broken','today']): return 'high'
    if any(w in t for w in ['soon','this week','estimate','quote']): return 'medium'
    return 'normal'
@app.post('/api/intake')
def intake(req: IntakeRequest):
    level=urgency(req.message + ' ' + req.service_needed)
    summary=f"{req.customer_name} needs {req.service_needed}. Urgency: {level}. Preferred time: {req.preferred_time}. Callback: {req.phone}."
    payload=req.model_dump(); payload.update({'urgency':level,'summary':summary,'next_action':'Call back and schedule estimate' if level!='high' else 'Escalate immediately and call now'})
    lead_id=save_record('lead', req.customer_name, json.dumps(payload)); return {'id':lead_id, **payload}
@app.get('/api/leads')
def leads():
    return {'leads':[json.loads(r['payload']) | {'id': r['id'], 'created_at': r['created_at']} for r in rows('lead')]}

INDEX_HTML='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Service Business Receptionist</title><style>body{font-family:Inter,Arial,sans-serif;background:#0f172a;color:#e5e7eb;margin:0}main{max-width:980px;margin:auto;padding:32px}.card{background:#111827;border:1px solid #334155;border-radius:18px;padding:24px;margin:18px 0}h1{font-size:42px}textarea,input{width:100%;box-sizing:border-box;border-radius:12px;border:1px solid #475569;background:#020617;color:#e5e7eb;padding:14px;margin:8px 0}button{background:#22c55e;color:#04130a;border:0;border-radius:12px;padding:12px 18px;font-weight:700}pre{white-space:pre-wrap;background:#020617;border-radius:12px;padding:16px}.pill{background:#1e293b;border:1px solid #475569;border-radius:999px;padding:6px 10px}</style></head><body><main><div class="card"><span class="pill">local business automation</span><h1>AI Service Business Receptionist</h1><p>Capture service-business leads, summarize urgency, and manage receptionist intake workflows.</p><ul><li>Lead intake form</li><li>Urgency classification</li><li>Receptionist summary</li><li>Callback task list</li><li>Local service vertical presets</li></ul></div><div class="card"><h2>Live API Demo</h2><textarea id="input" rows="7">Emergency leak under sink today</textarea><button onclick="runDemo()">Run Demo</button><pre id="out">Click Run Demo to call the FastAPI backend.</pre></div><div class="card"><h2>API</h2><p>Health: <code>/api/health</code> · Docs: <code>/docs</code></p></div><script>async function runDemo(){const res = await (fetch(\'/api/intake\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({customer_name:\'Demo Customer\',phone:\'555-0100\',service_needed:\'plumbing estimate\',message:document.getElementById(\'input\').value,preferred_time:\'tomorrow\'})})); const data = await res.json(); document.getElementById(\'out\').textContent = JSON.stringify(data,null,2);}</script></main></body></html>'
