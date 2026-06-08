from flask import Flask, render_template_string, request, redirect, Response
import os
import requests
from functools import wraps
from datetime import datetime

app = Flask(__name__)

# ========================================================
# CONFIGURAÇÃO PROFISSIONAL E SEGURA PARA PRODUÇÃO E VENDA
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# LOGIN DO GERENTE (Puxa do Render)
GERENTE_USER = os.environ.get("GERENTE_USER", "admin")
GERENTE_PASSWORD = os.environ.get("GERENTE_PASSWORD", "divino123")
# ========================================================

def requer_autenticacao(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not (auth.username == GERENTE_USER and auth.password == GERENTE_PASSWORD):
            return Response(
                'Acesso negado. Insira o usuário e senha corretos.', 401,
                {'WWW-Authenticate': 'Basic realm="Login Requerido"'}
            )
        return f(*args, **kwargs)
    return decorated

PAGINA_CLIENTE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sua Opinião - Divino Fogão</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f8f9fa; text-align: center; padding: 20px; }
        .container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }
        h2 { color: #d32f2f; }
        select, input, textarea { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; }
        button { background-color: #d32f2f; color: white; border: none; padding: 14px; width: 100%; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; }
        button:hover { background-color: #b71c1c; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Como foi sua experiência?</h2>
        <p>Sua avaliação nos ajuda a melhorar!</p>
        <form action="/salvar" method="POST">
            <label>Nota para a refeição e atendimento:</label>
            <select name="nota" required>
                <option value="5">⭐⭐⭐⭐⭐ (Excelente)</option>
                <option value="4">⭐⭐⭐⭐ (Muito Bom)</option>
                <option value="3">⭐⭐⭐ (Regular)</option>
                <option value="2">⭐⭐ (Ruim)</option>
                <option value="1">⭐ (Péssimo)</option>
            </select>
            <textarea name="comentario" placeholder="Deixe um comentário ou sugestão (Opcional)" rows="3"></textarea>
            <p><strong>Quer receber cupons e novidades no WhatsApp?</strong></p>
            <input type="text" name="nome" placeholder="Seu Nome">
            <input type="tel" name="whatsapp" placeholder="WhatsApp (Ex: 11999999999)">
            <button type="submit">Enviar Avaliação</button>
        </form>
    </div>
</body>
</html>
"""

PAGINA_AGRADECIMENTO = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Obrigado!</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f8f9fa; text-align: center; padding: 50px; }
        .container { background: white; padding: 40px; border-radius: 15px; max-width: 400px; margin: auto; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }
        h2 { color: #2e7d32; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Obrigado! 🎉</h2>
        <p>Sua opinião foi enviada com sucesso ao Divino Fogão.</p>
    </div>
</body>
</html>
"""

PAINEL_GERENTE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel do Gerente - Divino Fogão</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f6f9; padding: 30px; }
        .container { max-width: 1000px; margin: auto; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        h2 { color: #333; border-bottom: 2px solid #d32f2f; padding-bottom: 10px; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #d32f2f; color: white; }
        tr:hover { background-color: #f1f1f1; }
        .btn-exportar { background-color: #25D366; color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; font-size: 15px; font-weight: bold; display: inline-block; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .btn-exportar:hover { background-color: #1ebd59; }
        /* Estilo para destacar avaliações ruins */
        .nota-ruim { background-color: #ffdde0 !important; color: #c62828; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📊 Painel de Avaliações e Leads (Gerente)</h2>
        <p>Abaixo estão os feedbacks salvos permanentemente na nuvem:</p>
        
        <!-- Botão para Baixar a Lista de WhatsApp -->
        <button class="btn-exportar" onclick="exportarWhatsApps()">📥 Exportar Contatos WhatsApp (Excel/CSV)</button>
        
        <table id="tabela-feedbacks">
            <tr>
                <th>Horário</th>
                <th>Nome</th>
                <th>WhatsApp</th>
                <th>Nota</th>
                <th>Comentário</th>
            </tr>
            {% for f in lista_feedbacks %}
            <!-- Define a classe 'nota-ruim' se a nota for menor ou igual a 2 -->
            <tr class="{% if f.nota|int <= 2 %}nota-ruim{% endif %}">
                <td>{{ f.horario_formatado }}</td>
                <td>{{ f.nome }}</td>
                <td>{{ f.whatsapp }}</td>
                <td>{{ f.nota }} ⭐</td>
                <td>{{ f.comentario }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <script>
        // Atualiza a tela a cada 5 segundos para mostrar feedbacks novos automaticamente
        setInterval(function() {
            location.reload();
        }, 5000);

        // Função profissional para baixar os contatos válidos no formato Excel (CSV)
        function exportarWhatsApps() {
            let csvContent = "data:text/csv;charset=utf-8,\\uFEFF";
            csvContent += "Horário;Nome;WhatsApp\\n";

            const linhas = document.querySelectorAll("#tabela-feedbacks tr");

            for (let i = 1; i < linhas.length; i++) {
                const colunas = linhas[i].querySelectorAll("td");
                if (colunas.length >= 3) {
                    let horario = colunas[0].innerText.trim();
                    let nome = colunas[1].innerText.trim();
                    let whatsapp = colunas[2].innerText.trim();

                    // Só adiciona na lista se tiver deixado um número válido
                    if (whatsapp !== "Não informou" && whatsapp !== "") {
                        nome = nome.replace(/;/g, ","); // Evita quebra de colunas
                        csvContent += `${horario};${nome};${whatsapp}\\n`;
                    }
                }
            }

            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "lista_leads_divino_fogao.csv");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(PAGINA_CLIENTE)

@app.route('/salvar', methods=['POST'])
def salvar():
    dados = {
        "nome": request.form.get('nome') or "Anônimo",
        "whatsapp": request.form.get('whatsapp') or "Não informou",
        "nota": request.form.get('nota'),
        "comentario": request.form.get('comentario') or "Sem comentário"
    }
    
    headers = {
        "apikey": SUPABASE_KEY, 
        "Authorization": f"Bearer {SUPABASE_KEY}", 
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    url_limpa = SUPABASE_URL.strip().rstrip('/')
    requests.post(f"{url_limpa}/rest/v1/feedbacks", json=dados, headers=headers)
    return render_template_string(PAGINA_AGRADECIMENTO)

@app.route('/gerente')
@requer_autenticacao
def gerente():
    headers = {
        "apikey": SUPABASE_KEY, 
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    url_limpa = SUPABASE_URL.strip().rstrip('/')
    resposta = requests.get(f"{url_limpa}/rest/v1/feedbacks?select=*&order=id.desc", headers=headers)
    
    lista_feedbacks = []
    if resposta.status_code == 200:
        raw_feedbacks = resposta.json()
        for f in raw_feedbacks:
            # Pega o created_at do Supabase e formata para o padrão brasileiro (DD/MM/AAAA HH:MM)
            if 'created_at' in f and f['created_at']:
                try:
                    # Formato padrão ISO do Supabase (ex: 2026-06-08T12:00:00.000000+00:00)
                    dt = datetime.fromisoformat(f['created_at'].replace('Z', '+00:00'))
                    f['horario_formatado'] = dt.strftime('%d/%m/%Y %H:%M')
                except:
                    f['horario_formatado'] = "---"
            else:
                f['horario_formatado'] = "---"
            lista_feedbacks.append(f)
            
    return render_template_string(PAINEL_GERENTE, lista_feedbacks=lista_feedbacks)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
