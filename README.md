# Ingestão e Busca Semântica com LangChain e Postgres

## Objetivo

Você deve entregar um software capaz de:

- Ingestão: Ler um arquivo PDF e salvar suas informações em um banco de dados PostgreSQL com extensão pgVector.
- Busca: Permitir que o usuário faça perguntas via linha de comando (CLI) e receba respostas baseadas apenas no conteúdo do PDF.

## Exemplo no CLI

Faça sua pergunta (digite 'sair' para encerrar):

```
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.

---

Perguntas fora do contexto:

PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

## Tecnologias obrigatórias

- Linguagem: Python
- Framework: LangChain
- Banco de dados: PostgreSQL + pgVector
- Execução do banco de dados: Docker & Docker Compose (docker-compose fornecido no repositório de exemplo)

## Pacotes recomendados

- Split: `from langchain_text_splitters import RecursiveCharacterTextSplitter`
- Embeddings (OpenAI): `from langchain_openai import OpenAIEmbeddings`
- Embeddings (Gemini): `from langchain_google_genai import GoogleGenerativeAIEmbeddings`
- PDF: `from langchain_community.document_loaders import PyPDFLoader`
- Ingestão: `from langchain_postgres import PGVector`
- Busca: `similarity_search_with_score(query, k=10)`

## OpenAI

- Crie uma API Key da OpenAI.
- Você vai precisar de um modelo de embeddings e de um modelo de LLM para responder. Consulte a documentação oficial da OpenAI para ver os modelos disponíveis.

## Gemini

- Crie uma API Key da Google.
- Você vai precisar de um modelo de embeddings e de um modelo de LLM para responder. Consulte a documentação oficial do Google para ver os modelos disponíveis.

Os limites de requisições gratuitas dos modelos podem mudar com frequência. Para informações atualizadas, consulte a documentação oficial do Google.

## Escolha dos modelos

Este desafio não fixa modelos. Nomes e versões mudam com frequência e alguns são descontinuados, então faz parte do desafio consultar a documentação oficial do provedor que você escolher, ver quais modelos estão disponíveis no momento e selecionar os que atendem ao objetivo. Para o volume deste desafio, os modelos mais leves e baratos de cada provedor são suficientes.

Atenção: modelos de embedding diferentes geram vetores com dimensões diferentes. A tabela de vetores é criada na primeira ingestão, já com a dimensão do modelo que você escolheu. Se você trocar de modelo de embeddings depois disso, a ingestão passa a falhar por incompatibilidade de dimensão. Nesse caso é responsabilidade sua apagar a collection existente (ou o volume do banco) e refazer a ingestão do zero com o novo modelo.

## Requisitos

### 1. Ingestão do PDF

- O PDF é dividido em chunks de 1000 caracteres com overlap de 150.
- Cada chunk é convertido em embedding.
- Os vetores são armazenados no PostgreSQL com pgVector.
- Uma nova execução não reenvia o PDF quando ele já está na collection.

### 2. Consulta via CLI

Criar um script Python para simular um chat no terminal.

Passos ao receber uma pergunta:

- Vetorizar a pergunta.
- Buscar os 10 resultados mais relevantes (k=10) no banco vetorial.
- Montar o prompt e chamar a LLM.
- Retornar a resposta ao usuário.

Prompt a ser utilizado:

```
CONTEXTO:
{resultados concatenados do banco de dados}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta do usuário}

RESPONDA A "PERGUNTA DO USUÁRIO"
```

## Estrutura obrigatória do projeto

Faça um fork do repositório para utilizar a estrutura abaixo: https://github.com/devfullcycle/mba-ia-desafio-ingestao-busca

```
├── docker-compose.yml
├── requirements.txt      # Dependências
├── .env                  # Variáveis lidas pela ingestão e pelo chat
├── .env.example          # Exemplo inicial; os nomes usados estão na seção abaixo
├── src/
│   ├── ingest.py         # Script de ingestão do PDF
│   ├── search.py         # Script de busca
│   ├── chat.py           # CLI para interação com usuário
├── document.pdf          # PDF para ingestão
└── README.md             # Instruções de execução
```

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto. A ingestão e o chat leem estes nomes:

```
OPENAI_API_KEY=
OPENAI_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-5-nano
PGVECTOR_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PGVECTOR_COLLECTION=gpt5_collection
```

- `OPENAI_MODEL`: modelo de embeddings da ingestão e da busca.
- `OPENAI_CHAT_MODEL`: modelo que responde no chat. O padrão é `gpt-5-nano`.
- `PGVECTOR_URL` e `PGVECTOR_COLLECTION`: conexão e collection do Postgres. Os valores acima são os mesmos do `docker-compose.yml`.

## VirtualEnv para Python

Crie o ambiente virtual, ative-o e instale as dependências:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Ordem de execução

1. Subir o banco de dados:

```
docker compose up -d
```

2. Executar a ingestão do PDF (`document.pdf`):

```
python src/ingest.py
```

Se esse PDF já estiver na collection, o script identifica os chunks pelo caminho do arquivo e encerra sem enviar de novo.

3. Rodar o chat, com o ambiente virtual ativo:

```
python src/chat.py
```

O terminal fica em loop. Cada pergunta é vetorizada, os 10 trechos mais próximos são buscados no pgVector e a resposta sai só desse contexto. Digite `sair`, `exit` ou `quit` para encerrar.

## Entregável

Repositório público no GitHub contendo todo o código-fonte e README com instruções claras de execução do projeto.