from search import search_prompt

def main():
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    print("Faça sua pergunta (digite 'sair' para encerrar):")

    while True:
        question = input("\nPERGUNTA: ").strip()
        if not question:
            continue
        if question.lower() in {"sair", "exit", "quit"}:
            break

        answer = chain.invoke({"pergunta": question})
        print(f"RESPOSTA: {answer}")

if __name__ == "__main__":
    main()
