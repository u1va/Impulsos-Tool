import requests
import colorama
import time
import os

def log(message, **kwargs):
    if len(kwargs) > 0:
        message += f" {colorama.Fore.LIGHTBLACK_EX}→ {colorama.Fore.WHITE}"
        for key in kwargs:
            message += f"{colorama.Fore.LIGHTBLACK_EX}{key}={colorama.Fore.LIGHTCYAN_EX}{kwargs[key]} "
    print(
        f"{colorama.Fore.WHITE}[{colorama.Fore.LIGHTMAGENTA_EX}{time.strftime('%H:%M:%S', time.localtime())}{colorama.Fore.LIGHTBLACK_EX}] {colorama.Fore.WHITE}{message}"
    )

def fail(message, **kwargs):
    log(f"{colorama.Fore.WHITE}[{colorama.Fore.RED}FAIL{colorama.Fore.WHITE}]{colorama.Fore.RED} {message}", **kwargs)

def success(message, **kwargs):
    log(f"{colorama.Fore.WHITE}[{colorama.Fore.LIGHTGREEN_EX}OK{colorama.Fore.WHITE}]{colorama.Fore.LIGHTGREEN_EX} {message}", **kwargs)

def info(message, **kwargs):
    log(f"{colorama.Fore.WHITE}[{colorama.Fore.LIGHTBLUE_EX}INFO{colorama.Fore.WHITE}]{colorama.Fore.LIGHTBLUE_EX} {message}", **kwargs)

#
# Config
#
boost_rota = "https://impulsospublic.squareweb.app/api/v1/boost/convite"
order_status_rota = "https://impulsospublic.squareweb.app/api/v1/order"
api_key = "" # consiga uma api key em nosso discord (https://discord.gg/impulsos)
tokens_file = "tokens.txt"
useds_tokens_file = "tokens_usados.txt"

def carregar_tokens(arquivo=tokens_file):
    linhas_completas = []
    tokens_para_api = []
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue
                linhas_completas.append(linha)
                tokens_para_api.append(linha.split(":")[-1])
    except FileNotFoundError:
        fail(f"Arquivo {arquivo} não encontrado!")
    return linhas_completas, tokens_para_api

def salvar_tokens_usados(linhas_usadas):
    if not linhas_usadas:
        return
    with open(useds_tokens_file, "a", encoding="utf-8") as f:
        for linha in linhas_usadas:
            f.write(linha + "\n")
    info("Tokens salvos em tokens_usados.txt", quantidade=len(linhas_usadas))

def remover_tokens_arquivo(linhas_usadas):
    if not os.path.exists(tokens_file):
        return
    with open(tokens_file, "r", encoding="utf-8") as f:
        tokens_restantes = [linha.strip() for linha in f if linha.strip() not in linhas_usadas]
    with open(tokens_file, "w", encoding="utf-8") as f:
        for t in tokens_restantes:
            f.write(t + "\n")
    info("Tokens removidos de tokens.txt", quantidade=len(linhas_usadas))

def consultar_ordem(order_id: str):
    url = f"{order_status_rota}/{order_id}"
    info("Consultando informações da ordem...", order_id=order_id)
    resp = requests.get(url)
    if resp.status_code == 200:
        dados = resp.json()
        if "order" in dados and "tokens_used" in dados["order"]:
            dados["order"]["tokens_used"] = [t[:10] + "..." for t in dados["order"]["tokens_used"]]
        success("Informações da ordem recebidas", dados=dados)
    else:
        fail(f"Erro {resp.status_code} ao consultar ordem", detalhe=resp.text)

def main():
    colorama.init(autoreset=True)

    linhas_completas, tokens_para_api = carregar_tokens()
    if not tokens_para_api:
        fail("Nenhum token carregado!")
        return

    success("Tokens carregados", quantidade=len(tokens_para_api))

    while True:
        try:
            qtd = int(input(f"{colorama.Fore.LIGHTCYAN_EX}Quantos tokens deseja usar? "))
            if qtd <= 0 or qtd > len(tokens_para_api):
                fail("Número inválido, tente novamente.")
            else:
                break
        except ValueError:
            fail("Digite um número válido.")

    tokens_usados_para_api = tokens_para_api[:qtd]
    linhas_usadas_completas = linhas_completas[:qtd]

    salvar_tokens_usados(linhas_usadas_completas)
    remover_tokens_arquivo(linhas_usadas_completas)

    info("Tokens selecionados", quantidade=qtd)

    invite = input(f"{colorama.Fore.LIGHTCYAN_EX}Digite o convite do servidor (ex: discord.gg/impulsos): ").strip()

    campos = [{"invite": invite}]
    usar_md = input(f"{colorama.Fore.LIGHTCYAN_EX}Quer usar marca d'água? (s/n): ").strip().lower()
    if usar_md == "s":
        nome = input(f"{colorama.Fore.LIGHTCYAN_EX}Digite o nome: ").strip()
        bio = input(f"{colorama.Fore.LIGHTCYAN_EX}Digite a bio: ").strip()
        campos.append({"name": nome})
        campos.append({"bio": bio})
        info("Marca d'água ativada", name=nome, bio=bio)
    else:
        info("Sem marca d'água")

    body = {
        "campos": campos,
        "tokens": tokens_usados_para_api
    }

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    info("Enviando requisição para webhook...")
    resp = requests.post(boost_rota, json=body, headers=headers)

    if resp.status_code == 200:
        resposta = resp.json()
        success("Boost iniciado com sucesso!", resposta=resposta)

        ver_ordem = input(f"{colorama.Fore.LIGHTCYAN_EX}Quer ver as informações da ordem? (s/n): ").strip().lower()
        if ver_ordem == "s":
            order_id = resposta.get("message", "").split()[-1]
            consultar_ordem(order_id)
    else:
        fail(f"Erro {resp.status_code}", detalhe=resp.text)

if __name__ == "__main__":
    main()
