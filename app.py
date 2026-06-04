from flask import Flask, render_template_string, request, redirect
import os
import requests

app = Flask(__name__)

# ========================================================
# ⚠️ COLE AS SUAS CHAVES DO SUPABASE AQUI DENTRO DAS ASPAS
SUPABASE_URL = "https://cpuzrnhgxzkrrtomviab.supabase.co"
SUPABASE_KEY = "sb_publishable_VIMjM0Vk_47JKbacz9xJEw_U_byMYBs"
# ========================================================

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
        .container { max-width: 900px; margin: auto; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        h2 { color: #333; border-bottom: 2px solid #d32f2f; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #d32f2f; color: white; }
        tr:hover { background-color: #f1f1f1; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📊 Painel de Avaliações e Leads (Gerente)</h2>
        <p>Abaixo estão os feedbacks salvos permanentemente na nuvem:</p>
        <table>
            <tr>
                <th>Nome</th>
                <th>WhatsApp</th>
                <th>Nota</th>
                <th>Comentário</th>
            </tr>
            {% for f in lista_feedbacks %}
            <tr>
                <td>{{ f.nome }}</td>
                <td>{{ f.whatsapp }}</td>
                <td>{{ f.nota }}</td>
                <td>{{ f.comentario }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
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
    
    # Envia os dados direto para o Supabase salvar permanentemente
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    requests.post(f"{SUPABASE_URL}/rest/v1/feedbacks", json=dados, headers=headers)
    return render_template_string(PAGINA_AGRADECIMENTO)

@app.route('/gerente')
def gerente():
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    # Busca a lista completa diretamente do Supabase ordenando pelos mais novos
    resposta = requests.get(f"{SUPABASE_URL}/rest/v1/feedbacks?select=*&order=id.desc", headers=headers)
    lista_feedbacks = resposta.json() if resposta.status_code == 200 else []
    return render_template_string(PAINEL_GERENTE, lista_feedbacks=lista_feedbacks)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)