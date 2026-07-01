# Pipeline Weather

Este projeto é uma pipeline ETL em Python para coletar dados climáticos da OpenWeather API, transformá-los e carregá-los em um banco PostgreSQL. A execução é orquestrada pelo Apache Airflow, com o fluxo principal definido em [dags/weather_dag.py](dags/weather_dag.py).

## O que o projeto faz

1. Extrai dados meteorológicos da OpenWeather API.
2. Transforma o payload em um DataFrame tabular com colunas normalizadas.
3. Carrega os dados em um banco PostgreSQL.
4. Orquestra o processo com Apache Airflow para execução recorrente.

## Arquitetura

- [src/extract_data.py](src/extract_data.py): realiza a requisição à API e salva o resultado em [data/weather_data.json](data/weather_data.json).
- [src/transform_data.py](src/transform_data.py): normaliza e transforma os dados para um formato pronto para análise.
- [src/load_data.py](src/load_data.py): conecta ao PostgreSQL e grava os dados em uma tabela.
- [dags/weather_dag.py](dags/weather_dag.py): define a DAG do Airflow para executar o pipeline.
- [docker-compose.yaml](docker-compose.yaml): sobe os serviços de PostgreSQL, Redis e Airflow.

## Pré-requisitos

- Docker Desktop ou Docker Engine
- Docker Compose
- Python 3.12
- uv (opcional, mas recomendado para gerenciar o ambiente)
- WSL 2, caso você esteja no Windows

## Clonando o repositório

```bash
git clone https://github.com/seu-usuario/pipeline_weather.git
cd pipeline_weather
```

## Configuração do ambiente

### 1) Crie o ambiente virtual

Se você estiver usando uv:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

> Se o uv ficar travando por prompts interativos, use o ambiente já existente e instale de forma não interativa, por exemplo com `uv pip install -e .` dentro do ambiente ativo.

### 2) Configure a chave da API

Edite o arquivo [config/.env](config/.env) e ajuste a variável `API_KEY` com sua chave da OpenWeather.

```env
API_KEY='sua_chave_aqui'
```

### 3) Suba o stack do Docker

```bash
docker compose up -d
```

Isso iniciará:

- PostgreSQL em `localhost:5432`
- Redis
- Airflow UI em `http://localhost:8080`

## Executando o pipeline localmente

### Execução direta com Python

```bash
source .venv/bin/activate
python - <<'PY'
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve() / 'src'))
from extract_data import extract_weather_data
from transform_data import data_transformation
from load_data import load_weather_data

api_key = os.getenv('API_KEY', '')
url = f'https://api.openweathermap.org/data/2.5/weather?q=Sao%20Paulo,BR&units=metric&appid={api_key}'
extract_weather_data(url)
df = data_transformation()
load_weather_data('weather_data', df)
PY
```

### Execução via Airflow

Depois de subir os containers:

```bash
open http://localhost:8080
```

No Airflow, procure pela DAG `weather_pipeline` e execute manualmente.

## Estrutura de pastas

- [dags](dags): DAGs do Airflow
- [src](src): código Python do ETL
- [data](data): arquivos intermediários e saída JSON
- [config](config): arquivos de configuração e variáveis de ambiente
- [logs](logs): logs do Airflow

## Solução para problemas comuns

### Problemas de permissão no WSL

Se você estiver usando Ubuntu/WSL e estiver vendo erros de leitura ou escrita, rode:

```bash
sudo chown -R $USER:$USER .
chmod -R u+rwX .
```

### `uv` travando ou pedindo interatividade

Use o ambiente existente e instale de forma não interativa:

```bash
source .venv/bin/activate
uv pip install -e .
```

### Banco PostgreSQL não conecta

Confirme se o container do PostgreSQL está ativo:

```bash
docker compose ps postgres
```

E teste a porta local:

```bash
pg_isready -h 127.0.0.1 -p 5432 -U airflow
```

## Observações

- O projeto foi validado localmente com a execução completa de extração, transformação e carga.
- A DAG do Airflow está configurada para rodar periodicamente a cada hora.
