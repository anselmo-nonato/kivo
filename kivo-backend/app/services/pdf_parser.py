import io
import re
import hashlib
from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
import pdfplumber

SICOOB_CATEGORY_RULES = [
    (r"(?i)(deb\.iof|iof|tarifa|tar conta|tarifa bancaria|custas)", "Tarifas & Impostos", "essential"),
    (r"(?i)(juros cheque plus|juros adiant|juros|multa|mora|encargos)", "Juros & Multas", "waste"),
    (r"(?i)(deb\.pgto\.boleto|pagamento de cartao|cartao de credito|cartão de crédito)", "Fatura de Cartão", "essential"),
    (r"(?i)(deb\.conv|convenio|valem adm|dbauto)", "Moradia", "essential"),
    (r"(?i)(pix rec|ted rec|recebimento pix)", "Receitas", "essential"),
    (r"(?i)(pix\.emit|pix emit|pagamento pix|ted emit)", "Outros", "lifestyle"),
    (r"(?i)(ifood|rappi|restaurante|mcdonalds|burger|padaria|supermercado|carrefour|pao de acucar|assai)", "Alimentação", "essential"),
    (r"(?i)(uber|99app|posto|ipiranga|combustivel|gasolina|estacionamento|pedagio|sem parar)", "Transporte", "essential"),
    (r"(?i)(aluguel|condominio|enel|sabesp|cpfl|claro|vivo|internet|energia|copel)", "Moradia", "essential"),
    (r"(?i)(farmacia|drogaria|hospital|consulta|laboratorio|unimed|fleury|raia|drogasil)", "Saúde", "essential"),
    (r"(?i)(curso|alura|udemy|escola|colegio|faculdade|livraria)", "Educação", "essential"),
    (r"(?i)(zara|renner|riachuelo|shein|shopee|mercado livre|amazon|loja)", "Compras & Cuidados", "lifestyle"),
    (r"(?i)(netflix|spotify|cinema|steam|playstation|amazon prime|disney|bar|churrascaria)", "Lazer & Conforto", "lifestyle"),
    (r"(?i)(salario|pro-labore|dividendos|rendimento)", "Receitas", "essential"),
]

CAIXA_CATEGORY_RULES = [
    (r"(?i)(deb\.iof|iof|tarifa|tar conta|tarifa bancaria|custas)", "Tarifas & Impostos", "essential"),
    (r"(?i)(juros|multa|mora|encargos)", "Juros & Multas", "waste"),
    (r"(?i)(pagamento de boleto|cartoes caixa|fatura|cartao de credito|cartão de crédito)", "Fatura de Cartão", "essential"),
    (r"(?i)(enel|sabesp|cpfl|claro|vivo|internet|energia|copel|agua|luz)", "Moradia", "essential"),
    (r"(?i)(pix rec|pix recebido|ted rec|recebimento pix)", "Receitas", "essential"),
    (r"(?i)(deb pix|pix emit|pagamento pix|ted emit|doc emit)", "Outros", "lifestyle"),
    (r"(?i)(salario|pro-labore|verteron|pro labore|dividendos|rendimento)", "Receitas", "essential"),
    (r"(?i)(ifood|rappi|restaurante|mcdonalds|burger|padaria|supermercado|carrefour|pao de acucar|assai)", "Alimentação", "essential"),
    (r"(?i)(uber|99app|posto|ipiranga|combustivel|gasolina|estacionamento|pedagio|sem parar)", "Transporte", "essential"),
    (r"(?i)(farmacia|drogaria|hospital|consulta|laboratorio|unimed|fleury|raia|drogasil)", "Saúde", "essential"),
    (r"(?i)(curso|alura|udemy|escola|colegio|faculdade|livraria)", "Educação", "essential"),
    (r"(?i)(zara|renner|riachuelo|shein|shopee|mercado livre|amazon|loja)", "Compras & Cuidados", "lifestyle"),
    (r"(?i)(netflix|spotify|cinema|steam|playstation|amazon prime|disney|bar|churrascaria)", "Lazer & Conforto", "lifestyle"),
]

def find_matching_category(sugg_cat_name: str, workspace_categories: Optional[Dict[str, Any]]) -> Optional[Any]:
    if not workspace_categories:
        return None
    name_clean = sugg_cat_name.lower().strip()
    if name_clean in workspace_categories:
        return workspace_categories[name_clean]
    
    ALIASES = {
        "tarifas & impostos": ["tarifas & impostos", "tarifas e impostos", "taxas e tarifas", "taxas & tarifas", "impostos", "tarifas", "taxas", "encargos bancários", "tarifas bancárias"],
        "juros & multas": ["juros & multas", "juros e multas", "juros bancários", "juros", "multas", "encargos", "juros / multas"],
        "alimentação": ["alimentação", "alimentacao", "mercado", "supermercado", "comida", "refeição"],
        "moradia": ["moradia", "casa", "habitação", "contas de consumo"],
        "transporte": ["transporte", "veículo", "combustível", "carro"],
        "saúde": ["saúde", "saude", "farmácia", "médico"],
        "lazer & conforto": ["lazer & conforto", "lazer", "entretenimento", "viagem"],
        "educação": ["educação", "educacao", "estudos", "cursos"],
        "compras & cuidados": ["compras & cuidados", "compras", "vestuário", "cuidados pessoais"],
        "investimentos": ["investimentos", "investimento", "reserva", "poupança", "ações"],
        "receitas": ["receitas", "receita", "renda", "salário", "pro-labore"],
    }
    
    aliases_for_sugg = ALIASES.get(name_clean, [name_clean])
    for ws_cat_name, ws_cat_obj in workspace_categories.items():
        if ws_cat_name in aliases_for_sugg:
            return ws_cat_obj
        for alias in aliases_for_sugg:
            if alias in ws_cat_name or ws_cat_name in alias:
                return ws_cat_obj
                
    return None

def parse_decimal_br(val_str: str) -> Decimal:
    clean = val_str.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
    clean = re.sub(r"[^\d\.-]", "", clean)
    return Decimal(clean)

def parse_sicoob_pdf(
    file_bytes: bytes,
    workspace_categories: Optional[Dict[str, Any]] = None,
    filename: str = "extrato_sicoob.pdf",
) -> Dict[str, Any]:
    if workspace_categories is None:
        workspace_categories = {}

    full_text = ""
    pages_words = []
    
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            full_text += "\n" + t
            pages_words.append(page.extract_words())

    # 1. Metadados de Cabeçalho
    detected_account = None
    account_match = re.search(r"CONTA:\s*([\d\.-]+)\s*(?:/\s*([^\n\r]+))?", full_text)
    if account_match:
        acc_num = account_match.group(1).strip()
        acc_holder = account_match.group(2).strip() if account_match.group(2) else ""
        detected_account = f"{acc_num} - {acc_holder}".strip(" -")
    else:
        acc_num = "SICOOB"

    detected_coop = None
    coop_match = re.search(r"COOP\.:\s*([\d-]+)\s*(?:/\s*([^\n\r]+))?", full_text)
    if coop_match:
        detected_coop = f"{coop_match.group(1).strip()} / {coop_match.group(2).strip() if coop_match.group(2) else ''}".strip(" /")

    period_start = None
    period_end = None
    statement_year = datetime.now().year
    period_match = re.search(r"PER[IÍ]ODO:\s*(\d{2}/\d{2}/(\d{4}))\s*-\s*(\d{2}/\d{2}/(\d{4}))", full_text)
    if period_match:
        try:
            d1, m1, y1 = map(int, period_match.group(1).split("/"))
            d2, m2, y2 = map(int, period_match.group(3).split("/"))
            period_start = date(y1, m1, d1)
            period_end = date(y2, m2, d2)
            statement_year = y2
        except Exception:
            pass

    # 2. Resumo de Saldos
    statement_balance = None
    available_balance = None
    overdraft_limit = None

    bal_match = re.search(r"\(\+\)\s*SALDO EM CONTA:\s*([\d\.,]+)\s*([DC])", full_text)
    if bal_match:
        raw_bal = parse_decimal_br(bal_match.group(1))
        statement_balance = -raw_bal if bal_match.group(2) == "D" else raw_bal

    limit_match = re.search(r"\(\+\)\s*LIMITE CHEQUE PLUS:\s*([\d\.,]+)\s*([DC])", full_text)
    if limit_match:
        overdraft_limit = parse_decimal_br(limit_match.group(1))

    disp_match = re.search(r"\(=\)\s*SALDO DISPON[IÍ]VEL:\s*([\d\.,]+)\s*([DC])", full_text)
    if disp_match:
        raw_disp = parse_decimal_br(disp_match.group(1))
        available_balance = -raw_disp if disp_match.group(2) == "D" else raw_disp

    # 3. Extração Estruturada de Movimentações
    candidates = []
    total_income = Decimal("0.00")
    total_expense = Decimal("0.00")

    for page_idx, words in enumerate(pages_words):
        # Localiza o cabeçalho da tabela de movimentação nesta página (DATA | HISTÓRICO | VALOR)
        table_headers = [w for w in words if w["text"] == "DATA" and 100 <= w["x0"] <= 145]
        if not table_headers:
            continue
        table_top = table_headers[0]["top"]

        # Localiza o fim da tabela de lançamentos desta página
        end_words = [w for w in words if w["top"] > table_top and w["text"] in ("RESUMO", "ENCARGOS", "OUTRAS", "000")]
        table_bottom = min([w["top"] for w in end_words]) if end_words else 999

        # Identifica se é seção LANÇAMENTOS FUTUROS
        futuros_headers = [w for w in words if "LAN" in w["text"] and "AMENTOS" in w["text"]]
        is_page_futuros = len(futuros_headers) > 0

        # Coleta todas as âncoras de data dentro da tabela
        date_anchors = []
        for w in words:
            if w["top"] > table_top and w["top"] < table_bottom:
                if 100 <= w["x0"] <= 145 and re.match(r"^\d{2}/\d{2}(?:/\d{2,4})?$", w["text"]):
                    date_anchors.append(w)

        date_anchors = sorted(date_anchors, key=lambda a: a["top"])

        for i, anchor in enumerate(date_anchors):
            # Janela de coordenadas para esta linha (8 pontos acima para capturar valores alinhados no topo)
            window_top = anchor["top"] - 8
            window_bottom = date_anchors[i+1]["top"] - 8 if i + 1 < len(date_anchors) else table_bottom

            row_words = [w for w in words if window_top <= w["top"] < window_bottom]

            desc_words = sorted([w for w in row_words if 145 <= w["x0"] < 430], key=lambda x: (round(x["top"], 1), x["x0"]))
            val_words = sorted([w for w in row_words if w["x0"] >= 430], key=lambda x: (round(x["top"], 1), x["x0"]))

            desc_text = " ".join(w["text"] for w in desc_words).strip()
            val_text = " ".join(w["text"] for w in val_words).strip()

            upper_desc = desc_text.upper()
            if any(ignore in upper_desc for ignore in ["SALDO ANTERIOR", "SALDO DO DIA", "SALDO BLOQ", "SALDO BLOQUEADO"]):
                continue

            if not desc_text or not val_text:
                continue

            val_match = re.search(r"([\d\.,]+)\s*([DC\*])?", val_text)
            if not val_match:
                continue

            amt_val = parse_decimal_br(val_match.group(1))
            if amt_val == Decimal("0.00"):
                continue

            flag = val_match.group(2) if val_match.group(2) else ""
            if not flag:
                if "C" in val_text:
                    flag = "C"
                else:
                    flag = "D"

            tx_type = "expense" if flag == "D" else "income"

            raw_date_str = anchor["text"]
            parts = raw_date_str.split("/")
            day = int(parts[0])
            month = int(parts[1])
            year = statement_year
            if len(parts) == 3:
                y_val = int(parts[2])
                year = 2000 + y_val if y_val < 100 else y_val

            try:
                tx_date = date(year, month, day)
            except Exception:
                tx_date = date.today()

            is_future = is_page_futuros

            doc_num = None
            doc_match = re.search(r"DOC\.:\s*([^\s]+)", desc_text)
            if doc_match:
                doc_num = doc_match.group(1).strip()

            lines = desc_text.split("DOC.:")
            primary_title = lines[0].strip()
            for sub in ["Recebimento Pix", "Pagamento Pix", "Pagamento de cartao de credito", "Pagamento de cartão de crédito", "***."]:
                if sub in primary_title:
                    primary_title = primary_title.split(sub)[0].strip()

            if not primary_title:
                primary_title = desc_text

            sugg_cat_name = "Outros"
            sugg_ess = "lifestyle"
            conf = 0.5
            for pattern, cat_name, ess in SICOOB_CATEGORY_RULES:
                if re.search(pattern, desc_text):
                    sugg_cat_name = cat_name
                    sugg_ess = ess
                    conf = 0.95
                    break

            cat_obj = find_matching_category(sugg_cat_name, workspace_categories)

            hash_input = f"{acc_num}:{tx_date.isoformat()}:{amt_val}:{tx_type}:{doc_num or primary_title}"
            ext_id = hashlib.sha256(hash_input.encode()).hexdigest()[:24]

            if tx_type == "income":
                total_income += amt_val
            else:
                total_expense += amt_val

            candidates.append({
                "external_id": ext_id,
                "transaction_date": tx_date,
                "amount": amt_val,
                "type": tx_type,
                "description": primary_title[:255],
                "notes": desc_text if desc_text != primary_title else None,
                "doc_number": doc_num,
                "suggested_category_id": getattr(cat_obj, "id", None) if cat_obj else None,
                "suggested_category_name": sugg_cat_name,
                "suggested_essentiality": sugg_ess,
                "confidence_score": conf,
                "is_future": is_future,
                "reconciliation_status": "future" if is_future else "new",
                "is_duplicate": False,
                "matched_transaction_id": None
            })

    return {
        "filename": filename,
        "format": "PDF (Sicoob SISBR)",
        "detected_account": detected_account,
        "detected_coop": detected_coop,
        "period_start": period_start,
        "period_end": period_end,
        "statement_balance": statement_balance,
        "available_balance": available_balance,
        "overdraft_limit": overdraft_limit,
        "total_found": len(candidates),
        "total_amount_income": total_income,
        "total_amount_expense": total_expense,
        "candidates": candidates
    }


def parse_caixa_pdf(
    file_bytes: bytes,
    workspace_categories: Optional[Dict[str, Any]] = None,
    filename: str = "comprovante_caixa.pdf",
) -> Dict[str, Any]:
    if workspace_categories is None:
        workspace_categories = {}

    lines = []
    full_text = ""

    # 1. Extração via texto digital com fallback automático para OCR
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            extracted_text = ""
            for p in pdf.pages:
                extracted_text += (p.extract_text() or "") + "\n"

            if len(extracted_text.strip()) >= 50:
                full_text = extracted_text
                lines = [l.strip() for l in full_text.split("\n") if l.strip()]
            else:
                # PDF rasterizado (imagem de comprovante de app móvel) -> OCR com Tesseract
                try:
                    import pytesseract
                    from PIL import Image

                    tokens = []
                    for p in pdf.pages:
                        for img_obj in p.images:
                            raw_bytes = img_obj["stream"].get_rawdata()
                            img = Image.open(io.BytesIO(raw_bytes))
                            data = pytesseract.image_to_data(img, lang="por", output_type=pytesseract.Output.DICT)
                            for i in range(len(data["text"])):
                                w = data["text"][i].strip()
                                if w:
                                    tokens.append({
                                        "top": data["top"][i],
                                        "left": data["left"][i],
                                        "width": data["width"][i],
                                        "height": data["height"][i],
                                        "text": w
                                    })

                    if tokens:
                        tokens.sort(key=lambda t: (t["top"], t["left"]))
                        curr_line = []
                        curr_top = None
                        for t in tokens:
                            if curr_top is None:
                                curr_top = t["top"]
                                curr_line.append(t)
                            elif abs(t["top"] - curr_top) <= 15:
                                curr_line.append(t)
                            else:
                                curr_line.sort(key=lambda x: x["left"])
                                lines.append(" ".join(x["text"] for x in curr_line))
                                curr_line = [t]
                                curr_top = t["top"]
                        if curr_line:
                            curr_line.sort(key=lambda x: x["left"])
                            lines.append(" ".join(x["text"] for x in curr_line))

                        full_text = "\n".join(lines)
                except Exception:
                    full_text = extracted_text
                    lines = [l.strip() for l in full_text.split("\n") if l.strip()]
    except Exception:
        pass

    # 2. Metadados de Cabeçalho Caixa
    detected_account = None
    account_match = re.search(r"(?:^|\n)\s*Conta(?:\s*:|\s+)([\d\.\s/-]+)", full_text, re.IGNORECASE)
    client_match = re.search(r"(?:^|\n)\s*Cliente(?:\s*:|\s+)([^\n\r]+)", full_text, re.IGNORECASE)
    client_name = client_match.group(1).strip() if client_match else ""
    acc_num = account_match.group(1).strip() if account_match else "CAIXA"
    if client_name:
        detected_account = f"{acc_num} - {client_name}"
    else:
        detected_account = acc_num

    # Data da consulta / extrato
    period_start = None
    period_end = None
    statement_date_match = re.search(r"Data\s*(\d{2}/\d{2}/(\d{4}))", full_text, re.IGNORECASE)
    if statement_date_match:
        try:
            d, m, y = map(int, statement_date_match.group(1).split("/"))
            period_end = date(y, m, d)
        except Exception:
            pass

    # Saldo
    statement_balance = None
    bal_match = re.search(r"SALDO ANTERIOR\s*(?:R\$\s*)?([\d\.,]+)\s*([CD])?", full_text, re.IGNORECASE)
    if bal_match:
        raw_bal = parse_decimal_br(bal_match.group(1))
        flag = bal_match.group(2) if bal_match.group(2) else "C"
        statement_balance = -raw_bal if flag.upper() == "D" else raw_bal

    candidates = []
    total_income = Decimal("0.00")
    total_expense = Decimal("0.00")

    # Regex para linha de extrato Caixa (múltiplas movimentações):
    row_pattern = re.compile(
        r"^(\d{2}/\d{2}/\d{4})(?:\s*-\s*\d{2}:\d{2}:\d{2})?\s+(\d+)\s+(.*?)\s+([\d\.,]+)\s*([CD])(?:\s+[\d\.,]+\s*[CD€\*\s]*)?$",
        re.IGNORECASE
    )

    for line in lines:
        upper = line.upper()
        if any(ign in upper for ign in ["SALDO ANTERIOR", "SALDO DIA", "SALDO BLOQ", "SALDO TOTAL", "TOTALIZADOR"]):
            continue

        m = row_pattern.match(line)
        if m:
            dt_str, doc_num, desc_raw, val_str, flag = m.groups()
            amt_val = parse_decimal_br(val_str)
            if amt_val == Decimal("0.00"):
                continue

            tx_type = "expense" if flag.upper() == "D" else "income"
            d, mth, y = map(int, dt_str.split("/"))
            tx_date = date(y, mth, d)

            if not period_start or tx_date < period_start:
                period_start = tx_date
            if not period_end or tx_date > period_end:
                period_end = tx_date

            sugg_cat_name = "Outros"
            sugg_ess = "lifestyle"
            conf = 0.5
            for pattern, cat_name, ess in CAIXA_CATEGORY_RULES:
                if re.search(pattern, desc_raw):
                    sugg_cat_name = cat_name
                    sugg_ess = ess
                    conf = 0.95
                    break

            cat_obj = find_matching_category(sugg_cat_name, workspace_categories)

            hash_input = f"CAIXA:{detected_account}:{tx_date.isoformat()}:{amt_val}:{tx_type}:{doc_num}"
            ext_id = hashlib.sha256(hash_input.encode()).hexdigest()[:24]

            if tx_type == "income":
                total_income += amt_val
            else:
                total_expense += amt_val

            candidates.append({
                "external_id": ext_id,
                "transaction_date": tx_date,
                "amount": amt_val,
                "type": tx_type,
                "description": desc_raw[:255],
                "notes": f"Doc: {doc_num} | Linha: {line}",
                "doc_number": doc_num,
                "suggested_category_id": getattr(cat_obj, "id", None) if cat_obj else None,
                "suggested_category_name": sugg_cat_name,
                "suggested_essentiality": sugg_ess,
                "confidence_score": conf,
                "is_future": False,
                "reconciliation_status": "new",
                "is_duplicate": False,
                "matched_transaction_id": None
            })

    # Caso seja um Comprovante Único da Caixa (Pix / TED / Boleto / Transferência)
    if not candidates and any(h in full_text.upper() for h in ["COMPROVANTE", "TRANSFERENCIA", "PAGAMENTO", "PIX"]):
        val_single = re.search(r"Valor(?:\s*total)?:\s*(?:R\$\s*)?([\d\.,]+)", full_text, re.IGNORECASE)
        date_single = re.search(r"Data(?:\s*da\s*opera[çc][ãa]o|\s*do\s*d[ée]bito|/hora)?:\s*(\d{2}/\d{2}/(\d{4}))", full_text, re.IGNORECASE)
        doc_single = re.search(r"(?:C[óo]digo\s*da\s*opera[çc][ãa]o|ID\s*Transa[çc][ãa]o|Identificador|Autentica[çc][ãa]o|Nr\.\s*Doc):\s*([^\n\r]+)", full_text, re.IGNORECASE)
        fav_single = re.search(r"(?:Favorecido|Benefici[áa]rio|Nome|Destino):\s*([^\n\r]+)", full_text, re.IGNORECASE)

        if val_single:
            amt_val = parse_decimal_br(val_single.group(1))
            tx_date = date.today()
            if date_single:
                try:
                    d, mth, y = map(int, date_single.group(1).split("/"))
                    tx_date = date(y, mth, d)
                except Exception:
                    pass

            doc_num = doc_single.group(1).strip() if doc_single else None
            fav_name = fav_single.group(1).strip() if fav_single else "Pagamento Caixa"
            desc = f"Comprovante Caixa - {fav_name}"

            tx_type = "expense"
            if "RECEBIMENTO" in full_text.upper() or "CRÉDITO" in full_text.upper():
                tx_type = "income"
                total_income += amt_val
            else:
                total_expense += amt_val

            sugg_cat_name = "Outros"
            sugg_ess = "lifestyle"
            conf = 0.5
            for pattern, cat_name, ess in CAIXA_CATEGORY_RULES:
                if re.search(pattern, f"{desc} {full_text}"):
                    sugg_cat_name = cat_name
                    sugg_ess = ess
                    conf = 0.95
                    break

            cat_obj = find_matching_category(sugg_cat_name, workspace_categories)
            hash_input = f"CAIXA:{tx_date.isoformat()}:{amt_val}:{tx_type}:{doc_num or desc}"
            ext_id = hashlib.sha256(hash_input.encode()).hexdigest()[:24]

            candidates.append({
                "external_id": ext_id,
                "transaction_date": tx_date,
                "amount": amt_val,
                "type": tx_type,
                "description": desc[:255],
                "notes": f"Autenticação / Doc: {doc_num}" if doc_num else None,
                "doc_number": doc_num,
                "suggested_category_id": getattr(cat_obj, "id", None) if cat_obj else None,
                "suggested_category_name": sugg_cat_name,
                "suggested_essentiality": sugg_ess,
                "confidence_score": conf,
                "is_future": False,
                "reconciliation_status": "new",
                "is_duplicate": False,
                "matched_transaction_id": None
            })

    return {
        "filename": filename,
        "format": "PDF (Caixa Econômica Federal)",
        "detected_account": detected_account,
        "detected_coop": None,
        "period_start": period_start,
        "period_end": period_end,
        "statement_balance": statement_balance,
        "available_balance": None,
        "overdraft_limit": None,
        "total_found": len(candidates),
        "total_amount_income": total_income,
        "total_amount_expense": total_expense,
        "candidates": candidates
    }


def parse_pdf_statement(
    file_bytes: bytes,
    workspace_categories: Optional[Dict[str, Any]] = None,
    filename: str = "extrato.pdf",
) -> Dict[str, Any]:
    """
    Roteador inteligente de PDFs bancários: detecta automaticamente o banco
    (Sicoob, Caixa Econômica Federal, ou genérico) e executa o parser correspondente.
    """
    if workspace_categories is None:
        workspace_categories = {}

    preview_text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for p in pdf.pages[:2]:
                preview_text += (p.extract_text() or "") + "\n"
    except Exception:
        pass

    upper_preview = preview_text.upper()
    upper_name = filename.upper()

    # Se for Caixa ou tiver indicadores de Caixa
    if "CAIXA" in upper_preview or "CAIXA" in upper_name or "COMPROVANTE" in upper_name:
        return parse_caixa_pdf(file_bytes, workspace_categories, filename=filename)
    elif "SICOOB" in upper_preview or "SISBR" in upper_preview or "SICOOB" in upper_name:
        return parse_sicoob_pdf(file_bytes, workspace_categories, filename=filename)

    # Se não identificado diretamente pelo texto inicial, tenta Sicoob e Caixa
    sicoob_res = parse_sicoob_pdf(file_bytes, workspace_categories, filename=filename)
    if sicoob_res["total_found"] > 0:
        return sicoob_res

    caixa_res = parse_caixa_pdf(file_bytes, workspace_categories, filename=filename)
    if caixa_res["total_found"] > 0:
        return caixa_res

    return sicoob_res