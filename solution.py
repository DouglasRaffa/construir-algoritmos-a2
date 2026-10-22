from datetime import datetime, timedelta
import requests


def cotar():
    # Obtém a data atual
    hoje = datetime.today()

    # Cria uma sequência de 365 dias
    dias = []

    for i in range(365):
        dia = hoje - timedelta(days=i) #pega hoje e a cada repetição vai diminuindo os dias 
        dias.append(dia) #vai adicionando os dias na lista

    # Inclui dias anteriores para encontrar
    # a cotação de finais de semana e feriados
    inicio = dias[-1] - timedelta(days=10)


    data_inicial = inicio.strftime("%m-%d-%Y")
    data_final = hoje.strftime("%m-%d-%Y")

    # Endereço da API
    url = (
        "https://olinda.bcb.gov.br/olinda/servico/"
        "PTAX/versao/v1/odata/"
        "CotacaoDolarPeriodo(dataInicial=@dataInicial,"
        "dataFinalCotacao=@dataFinalCotacao)"
    )

    # Parâmetros
    parametros = {
        "@dataInicial": f"'{data_inicial}'",
        "@dataFinalCotacao": f"'{data_final}'",
        "$format": "json",
        "$select": "cotacaoCompra,dataHoraCotacao",
        "$top": 500
    }

    # Consulta ao Banco Central
    resposta = requests.get(
        url, params=parametros, timeout=30
    )

    resposta.raise_for_status()

    dados = resposta.json()["value"]

    # Organiza as cotações por data
    cotacoes_por_dia = {}

    for item in dados:
        data = item["dataHoraCotacao"][:10]
        cotacoes_por_dia[data] = item["cotacaoCompra"]

    # Organiza os registros do mais recente para o mais antigo
    cotacoes = []
    ultima_cotacao = None

    for dia in reversed(dias):
        data = dia.strftime("%Y-%m-%d")

        if data in cotacoes_por_dia:
            ultima_cotacao = cotacoes_por_dia[data]

        cotacoes.append(ultima_cotacao)

    # Se o primeiro dia não tiver cotação,
    # utiliza a última anterior disponível
    if cotacoes[0] is None:
        anteriores = [
            item for item in dados
            if item["dataHoraCotacao"][:10]
            < dias[-1].strftime("%Y-%m-%d")
        ]

        if anteriores:
            anteriores.sort(
                key=lambda item: item["dataHoraCotacao"]
            )
            valor = anteriores[-1]["cotacaoCompra"]

            for i in range(len(cotacoes)):
                if cotacoes[i] is None:
                    cotacoes[i] = valor
                else:
                    break

    # Retorna a lista começando por hoje
    cotacoes.reverse()

    return cotacoes


if __name__ == "__main__":
    resultado = cotar()

    print(resultado)
    print("=========================================================================================")
    print("Quantidade:", len(resultado))
    print("Dias sem valor:", resultado.count(None))