"""
Módulo com funcionalidades extras: filtros, exportação PDF, etc.
"""

from datetime import datetime, timedelta
from models import Compra, Despesa, db
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import io

def gerar_relatorio_compras_pdf(data_inicio=None, data_fim=None, fornecedor_id=None):
    """Gera relatório de compras em PDF."""
    
    # Construir query
    query = Compra.query
    
    if data_inicio:
        query = query.filter(Compra.data >= data_inicio)
    
    if data_fim:
        query = query.filter(Compra.data <= data_fim)
    
    if fornecedor_id:
        query = query.filter(Compra.fornecedor_id == fornecedor_id)
    
    compras = query.order_by(Compra.data.desc()).all()
    
    # Criar PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#006600'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Elementos do documento
    elements = []
    
    # Título
    elements.append(Paragraph('Relatório de Compras - MRX Gestão', title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Informações de filtro
    filtro_text = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if data_inicio or data_fim:
        filtro_text += " | Período: "
        if data_inicio:
            filtro_text += f"de {data_inicio.strftime('%d/%m/%Y')}"
        if data_fim:
            filtro_text += f" até {data_fim.strftime('%d/%m/%Y')}"
    
    elements.append(Paragraph(filtro_text, styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Tabela de compras
    if compras:
        data = [['Material', 'Fornecedor', 'Valor', 'Tipo', 'Data']]
        
        for compra in compras:
            data.append([
                compra.material[:30],
                compra.fornecedor.nome_social[:25],
                f"R$ {compra.valor_tabela:.2f}",
                compra.tipo_coleta,
                compra.data.strftime('%d/%m/%Y')
            ])
        
        # Totalizador
        total = sum(c.valor_tabela for c in compras)
        data.append(['', '', f'TOTAL: R$ {total:.2f}', '', ''])
        
        table = Table(data, colWidths=[2*inch, 2*inch, 1.2*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006600')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#004d00')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph('Nenhuma compra encontrada para os filtros especificados.', styles['Normal']))
    
    # Gerar PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def gerar_relatorio_despesas_pdf(data_inicio=None, data_fim=None, forma_pagamento=None):
    """Gera relatório de despesas em PDF."""
    
    # Construir query
    query = Despesa.query
    
    if data_inicio:
        query = query.filter(Despesa.data >= data_inicio)
    
    if data_fim:
        query = query.filter(Despesa.data <= data_fim)
    
    if forma_pagamento:
        query = query.filter(Despesa.forma_pagamento == forma_pagamento)
    
    despesas = query.order_by(Despesa.data.desc()).all()
    
    # Criar PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#006600'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Elementos do documento
    elements = []
    
    # Título
    elements.append(Paragraph('Relatório de Despesas - MRX Gestão', title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Informações de filtro
    filtro_text = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if data_inicio or data_fim:
        filtro_text += " | Período: "
        if data_inicio:
            filtro_text += f"de {data_inicio.strftime('%d/%m/%Y')}"
        if data_fim:
            filtro_text += f" até {data_fim.strftime('%d/%m/%Y')}"
    
    elements.append(Paragraph(filtro_text, styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Tabela de despesas
    if despesas:
        data = [['Descrição', 'Valor', 'Forma de Pagamento', 'Data']]
        
        for despesa in despesas:
            data.append([
                despesa.nome_social[:35],
                f"R$ {despesa.valor:.2f}",
                despesa.forma_pagamento or '-',
                despesa.data.strftime('%d/%m/%Y')
            ])
        
        # Totalizador
        total = sum(d.valor for d in despesas)
        data.append(['', f'TOTAL: R$ {total:.2f}', '', ''])
        
        table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004d00')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#006600')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph('Nenhuma despesa encontrada para os filtros especificados.', styles['Normal']))
    
    # Gerar PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def filtrar_compras(data_inicio=None, data_fim=None, fornecedor_id=None, material=None):
    """Filtra compras com base em critérios."""
    query = Compra.query
    
    if data_inicio:
        query = query.filter(Compra.data >= data_inicio)
    
    if data_fim:
        query = query.filter(Compra.data <= data_fim)
    
    if fornecedor_id:
        query = query.filter(Compra.fornecedor_id == fornecedor_id)
    
    if material:
        query = query.filter(Compra.material.ilike(f'%{material}%'))
    
    return query.order_by(Compra.data.desc()).all()

def filtrar_despesas(data_inicio=None, data_fim=None, forma_pagamento=None, valor_min=None, valor_max=None):
    """Filtra despesas com base em critérios."""
    query = Despesa.query
    
    if data_inicio:
        query = query.filter(Despesa.data >= data_inicio)
    
    if data_fim:
        query = query.filter(Despesa.data <= data_fim)
    
    if forma_pagamento:
        query = query.filter(Despesa.forma_pagamento == forma_pagamento)
    
    if valor_min:
        query = query.filter(Despesa.valor >= valor_min)
    
    if valor_max:
        query = query.filter(Despesa.valor <= valor_max)
    
    return query.order_by(Despesa.data.desc()).all()

def obter_resumo_periodo(data_inicio, data_fim):
    """Obtém resumo de compras e despesas para um período."""
    
    compras = Compra.query.filter(
        Compra.data >= data_inicio,
        Compra.data <= data_fim
    ).all()
    
    despesas = Despesa.query.filter(
        Despesa.data >= data_inicio,
        Despesa.data <= data_fim
    ).all()
    
    total_compras = sum(c.valor_tabela for c in compras)
    total_despesas = sum(d.valor for d in despesas)
    
    return {
        'total_compras': total_compras,
        'total_despesas': total_despesas,
        'quantidade_compras': len(compras),
        'quantidade_despesas': len(despesas),
        'saldo': total_compras - total_despesas
    }
