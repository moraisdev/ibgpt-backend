import pdfplumber
from tabulate import tabulate
from io import BytesIO


def extract_documents(pdf_content: bytes) -> str:
    formatted_text = []
    try:
        with pdfplumber.open(BytesIO(pdf_content)) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                if tables:
                    formatted_text.append(f"--- Página {page_number} ---\n")
                    for table_number, table in enumerate(tables, start=1):
                        clean_table = [
                            [cell.strip() if cell else "" for cell in row]
                            for row in table
                        ]
                        table_text = tabulate(
                            clean_table, headers="firstrow", tablefmt="plain"
                        )
                        formatted_text.append(f"--- Tabela {table_number} ---\n")
                        formatted_text.append(table_text)
                        formatted_text.append("\n")
                else:
                    text = page.extract_text()
                    if text:
                        formatted_text.append(f"--- Página {page_number} ---\n")
                        formatted_text.append(text)
                    else:
                        formatted_text.append(f"Página {page_number} está vazia.\n")
        return "\n".join(formatted_text)
    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
        return ""
