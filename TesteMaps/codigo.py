import googlemaps
import csv

API_KEY = "*****"
gmaps = googlemaps.Client(key=API_KEY)

def ler_enderecos(arquivo_csv):
    enderecos = []
    with open(arquivo_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if any(row.values()):
                endereco = f"{row['Rua']}, {row['Número']}, {row['Bairro']}, {row['Cidade']}, {row['Estado']}"
                enderecos.append(endereco)
    return enderecos

def calcular_rota(endereco_origem, endereco_destino, paradas=[]):
    """
    Calcula a melhor rota entre origem e destino, considerando paradas intermediárias.
    Retorna a distância e duração total.
    """
    rota = gmaps.directions(
        origin=endereco_origem,
        destination=endereco_destino,
        waypoints=paradas,  # Lista de endereços para paradas
        optimize_waypoints=True,  # Otimiza a ordem das paradas
        mode="driving"  # Modo de transporte (carro)
    )

    if not rota:
        return "Nenhuma rota encontrada"


    rota_info = rota[0]['legs']
    distancia_total = sum(leg['distance']['value'] for leg in rota_info) / 1000
    duracao_total = sum(leg['duration']['value'] for leg in rota_info) / 60

    return {
        "distancia_km": round(distancia_total, 2),
        "duracao_minutos": round(duracao_total, 2),
        "rota_json": rota
    }

enderecos = ler_enderecos('enderecos.csv')
origem = enderecos[0]
destino = enderecos[-1]
paradas = enderecos[1:-1]

resultado = calcular_rota(origem, destino, paradas)
print(resultado)
