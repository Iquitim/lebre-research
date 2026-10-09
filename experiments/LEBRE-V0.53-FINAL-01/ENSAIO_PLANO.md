# Verificações antes da aprovação do pré-registro (09/10/2026), plano antes de rodar

**Pedido do responsável pelo projeto, depois de ler o pré-registro (commit `15ea297`).** Nenhum valor da reserva é lido.

1. **Presença dos arquivos, só por nomes** (`ensaio_arquivos.py`): para cada série reservada, o arquivo de tempo do
   Open-Meteo (16 usinas e 4 subsistemas), o arquivo de carga de 2026, os 24 arquivos mensais do ONS, os 10 arquivos do
   FRED; o nome de cada usina reservada na coluna de nomes dos arquivos do ONS; cada bacia na lista de arquivos dos zips do
   CAMELS-BR; cada medidor no cabeçalho do arquivo de medidores do BDG2.
2. **Ensaio geral em bacias e prédios** (`ensaio_v052.py`): v0.53 (commit `4a2620e`, cópia fixa) e v0.52 nas séries de
   CAMELS-BR e BDG2 **já gastas** pela v0.52 (desenvolvimento: 10 bacias e 5 medidores; reserva 2 da v0.52: 20 e 20),
   todas conferidas contra a reserva da v0.53 antes de carregar. **Regra (declarada antes):** o pré-registro segue para
   aprovação se não houver erro, nem passo de avaliação com previsão não finita, nem série com acréscimo de custo > 1.100 FP.
   Se houver, o problema é corrigido no desenvolvimento, registrado, e o pré-registro é refeito. As razões v0.53 ÷ v0.52 são
   reportadas só como informação: **não são evidência** (dados já usados).
