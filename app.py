from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import re

app = Flask(__name__)
CORS(app)

# Banco de piadas massivo e categorizado
PIADAS_DATABASE = {
    "tecnologia": [
        "Por que o computador foi ao médico? Porque estava com um vírus!",
        "Existem 10 tipos de pessoas no mundo: as que entendem binário e as que não entendem.",
        "O que o HTML disse para o CSS? 'Você me dá estilo!'",
        "Por que o desenvolvedor faleceu? Porque ele não viu o 'break'!",
        "Qual é a ferramenta favorita dos programadores? O 'CTRL + C' e 'CTRL + V'.",
        "Por que o Wi-Fi foi preso? Porque estava transmitindo sinal sem permissão!",
        "O que um bit disse para o outro? 'A gente se vê no próximo ciclo!'",
        "Como o programador bebe café? Em Java!",
        "O que o programador falou quando a casa pegou fogo? 'É um problema de ambiente, na minha máquina funcionava!'",
        "Por que o teclado não dorme? Porque ele tem muitas teclas 'Control'!",
        "Qual é o animal favorito do programador? O Python!"
    ],
    "animais": [
        "O que o pinto disse para o outro? 'Piu!'",
        "Qual é o animal que não presta? O paca. Porque Paca-sso!",
        "Por que o cachorro entrou na igreja? Porque era da raça 'Soberano'!",
        "O que a cobra falou para o sapo? 'Nossa, você é um pulo!'",
        "Por que o boi vai para a praia? Para ver as 'vacas' marinhas!",
        "Qual é o peixe mais elegante? O peixe-palhaço em dia de gala!",
        "O que o gato disse quando caiu do telhado? 'Miau-miau, me arrebentei!'",
        "Qual é o dinossauro que ama limpezas? O Varredossauro!",
        "O que o urso disse para o outro? 'Hoje o dia está meio urso...'",
        "Qual o animal que mais gosta de matemática? A coruja, porque ela é 'Sábia'!"
    ],
    "escola": [
        "Professor: 'Joãozinho, me diga dois pronomes.' Joãozinho: 'Quem? Eu?'",
        "Por que o livro de matemática se suicidou? Porque tinha muitos problemas.",
        "Qual é a nota que os estudantes de química mais gostam? A nota 'Bárion'!",
        "O que o lápis disse para o papel? 'Estou ligado em você!'",
        "Na aula de geografia: 'Onde fica a cadeia alimentícia?' 'Acho que fica perto do presídio!'",
        "Joãozinho, o que você vai ser quando crescer? 'Livre, espero!'",
        "Por que a borracha é o objeto mais humilde? Porque apaga os erros dos outros."
    ],
    "ciencia": [
        "Por que o elétron nunca é preso? Porque ele é muito leve e tem carga negativa!",
        "O que um átomo disse para o outro? 'Perdi um elétron!' 'Tem certeza?' 'Tenho, estou positivo!'",
        "Qual é a fórmula da água benta? H-2-Ó-Glória!",
        "Por que os biólogos gostam tanto de células? Porque elas são o núcleo da questão!",
        "O que a célula falou para a fotossíntese? 'Você me ilumina!'"
    ],
    "trabalho": [
        "Por que o engenheiro olhou para o espelho? Para ver o reflexo das suas obras!",
        "O que o chefe disse para o funcionário pontual? 'Você chegou cedo demais para pedir aumento!'",
        "Por que o eletricista é o profissional mais rápido? Porque ele trabalha no estalo de um raio!",
        "Qual é o cumulo da economia de escritório? Usar o mesmo clipe até ele virar agulha.",
        "Por que o marceneiro é muito calmo? Porque ele resolve tudo no serrote!"
    ],
    "cumulos": [
        "Qual é o cúmulo da paciência? Dobrar a água.",
        "Qual é o cúmulo da rapidez? Fechar a gaveta com a chave dentro.",
        "Qual é o cúmulo do azar? Ser atropelado por um carro parado.",
        "Qual é o cúmulo da força? Dobrar a esquina!",
        "Qual é o cúmulo da surdez? Ouvir o barulho do silêncio."
    ],
    "cotidiano": [
        "O que a impressora disse para a outra? 'Essa folha é sua ou é impressão minha?'",
        "Por que a planta não fala? Porque ela é muda!",
        "Por que o café foi preso? Porque foi pego em flagrante coado!",
        "O que o zero disse para o oito? 'Belo cinto!'",
        "Por que o relógio foi ao psicólogo? Porque estava muito atrasado com a vida.",
        "O que a lâmpada falou quando acendeu? 'Estou iluminada!'",
        "O que a mesa disse para a cadeira? 'Senta que lá vem história!'",
        "Por que a xícara é ótima em fofoca? Porque gosta de um bom café com conversa!"
    ],
    "geral": [
        "Como se chama o piromaníaco com pressa? Queima-roupa!",
        "Por que o fantasma entrou no elevador? Para subir o espírito!",
        "Qual é o prato favorito do motorista? Macarrão ao molho de pneu!",
        "O que a tomada disse para o plugue? 'Sinto uma conexão entre nós!'",
        "Por que a tesoura não joga futebol? Porque ela sempre corta a jogada!"
    ]
}

# Mapeamento de palavras-chave usando Regex
KEYWORD_MAP = {
    "tecnologia": r'\b(tech|tecnologia|computador|pc|dev|programador|codigo|code|html|css|python|java|wifi|software|bit)\b',
    "animais": r'\b(animal|animais|gato|cachorro|pet|bicho|pinto|vaca|peixe|cobra|urso|dinossauro)\b',
    "escola": r'\b(escola|estudo|professor|aula|aluno|joaozinho|matematica|livro|borracha|nota)\b',
    "ciencia": r'\b(ciencia|fisica|quimica|biologia|atomo|eletron|celula|formula)\b',
    "trabalho": r'\b(trabalho|emprego|chefe|escritorio|empresa|engenheiro|eletricista|profissao)\b',
    "cumulos": r'\b(cumulo|extremo|maximo)\b',
    "cotidiano": r'\b(casa|cafe|impressora|relogio|lampada|mesa|planta|xicara|dia)\b'
}

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    message = data.get('message', '').lower()
    history = data.get('history', [])  # Lista de piadas já exibidas para evitar repetição

    # 1. Identificar categoria via Regex
    categoria_encontrada = None
    for cat, pattern in KEYWORD_MAP.items():
        if re.search(pattern, message):
            categoria_encontrada = cat
            break

    if not categoria_encontrada:
        categoria_encontrada = random.choice(list(PIADAS_DATABASE.keys()))

    # 2. Filtrar piadas não vistas na categoria selecionada
    piadas_disponiveis = [p for p in PIADAS_DATABASE[categoria_encontrada] if p not in history]

    # Se todas as piadas da categoria já foram vistas, limpa o histórico daquela categoria
    if not piadas_disponiveis:
        piadas_disponiveis = PIADAS_DATABASE[categoria_encontrada]

    piada_escolhida = random.choice(piadas_disponiveis)

    return jsonify({
        "bot": piada_escolhida,
        "categoria": categoria_encontrada,
        "total_piadas_categoria": len(PIADAS_DATABASE[categoria_encontrada]),
        "status": "success"
    })

@app.route('/api/stats', methods=['GET'])
def stats():
    total = sum(len(v) for v in PIADAS_DATABASE.values())
    return jsonify({
        "total_piadas": total,
        "categorias": list(PIADAS_DATABASE.keys())
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)