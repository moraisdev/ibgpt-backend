from jinja2 import Template


def render_offer_to_html(offer):
    # Preparar dados formatados
    offer_data = {
        "customer_name": offer.customer.company_name,
        "created_at": offer.created_at.strftime("%B de %Y"),
        "calculated_value": (
            f"{offer.calculated_value:.2f}".replace(".", ",")
            if offer.calculated_value
            else "0,00"
        ),
        "periodicity": offer.periodicity,
        "customer_cnpj": offer.customer.company_cnpj,
        "created_date": offer.created_at.strftime("%d/%m/%Y"),
        "calculations": [
            {
                "description": calc.description,
                "basecalculoinss": (
                    f"{calc.values['basecalculoinss']:.2f}".replace(".", ",")
                    if calc.values.get("basecalculoinss")
                    else "0,00"
                ),
                "creditosauditados": (
                    f"{calc.values['creditosauditados']:.2f}".replace(".", ",")
                    if calc.values.get("creditosauditados")
                    else "0,00"
                ),
                "juros": (
                    f"{calc.values['juros']:.2f}".replace(".", ",")
                    if calc.values.get("juros")
                    else "0,00"
                ),
                "valortotal": (
                    f"{calc.values['valortotal']:.2f}".replace(".", ",")
                    if calc.values.get("valortotal")
                    else "0,00"
                ),
            }
            for calc in offer.calculations
        ],
    }

    # Template HTML
    template = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Relatório Analítico de Auditoria</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                line-height: 1.6;
            }
            h1, h2, h3 {
                text-align: center;
            }
            h1 {
                font-size: 24px;
                text-transform: uppercase;
            }
            h2 {
                font-size: 20px;
                text-transform: uppercase;
            }
            h3 {
                font-size: 18px;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            ul li {
                margin-bottom: 5px;
            }
            ul li:before {
                content: '• ';
                color: black;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f4f4f4;
                text-align: center;
            }
            footer {
                text-align: center;
                margin-top: 30px;
                font-size: 0.9em;
                color: #666;
            }
            .page-break {
                page-break-after: always;
            }
        </style>
    </head>
    <body>
        <h1>RELATÓRIO ANALÍTICO DE<br>
        AUDITORIA SOBRE FOLHA DE<br>
        PAGAMENTO</h1>
        <h3>(Natureza jurídica das verbas pagas)</h3>
        <h3>Verbas indenizatórias X Verbas remuneratórias</h3>
        
        <p><strong>Contratante:</strong> {{ customer_name }}</p>
        <p><strong>{{ created_at }}</strong></p>

        <h2>SUMÁRIO</h2>
        <ul>
            <li>1. Apresentação do Instituto Brasileiro de Gestão e Planejamento Tributário - IBGPT</li>
            <li>2. Valores</li>
            <li>3. Cálculos Sintetizados</li>
        </ul>

        <h2>1. APRESENTAÇÃO DO INSTITUTO BRASILEIRO DE GESTÃO E PLANEJAMENTO TRIBUTÁRIO - IBGPT</h2>
        <p>O IBGPT é uma Consultoria e Assessoria Empresarial especializada em Gestão e Planejamento Tributário, bem como uma Instituição de aperfeiçoamento técnico jurídico com mais de uma década de atuação em ambas as áreas. Nossa intenção é facilitar aos contribuintes as dificuldades tributárias, gerando oportunidades e reduzindo impostos.</p>

        <h2>2. VALORES</h2>
        <p>
            Conforme as análises feitas na documentação fornecida pela empresa {{ customer_name }},
            foram identificadas as verbas indenizatórias no período de {{ periodicity }}. Totalizando um saldo
            de crédito a recuperar da empresa de R$ {{ calculated_value }} valores corrigidos pela taxa SELIC.
        </p>

        <h2>3. CÁLCULOS SINTETIZADOS</h2>
        <p><strong>Data:</strong> {{ created_date }}</p>
        <p><strong>CNPJ:</strong> {{ customer_cnpj }}</p>
        <p><strong>Período:</strong> {{ periodicity }}</p>
        <table>
            <thead>
                <tr>
                    <th>Verbas Indenizatórias</th>
                    <th>Base de Cálculo INSS</th>
                    <th>Créditos Auditados</th>
                    <th>Juros</th>
                    <th>Valor Total R$</th>
                </tr>
            </thead>
            <tbody>
                {% for calc in calculations %}
                <tr>
                    <td>{{ calc.description }}</td>
                    <td>{{ calc.BaseCalculoINSS }}</td>
                    <td>{{ calc.CreditosAuditados }}</td>
                    <td>{{ calc.Juros }}</td>
                    <td>{{ calc.ValorTotal }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <footer>
            <p>Relatório gerado automaticamente pelo sistema.</p>
        </footer>
    </body>
    </html>
    """
    rendered_template = Template(template).render(offer_data)
    return rendered_template
