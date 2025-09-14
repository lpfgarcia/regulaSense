
SYSTEM = f'''Sou um Assistente da Secretaria de Saúde do Distrito Federal.'''

CHAT_START = f'''"Olá! {SYSTEM}
Para prosseguir, por favor informe os seguintes dados do paciente:
- Idade
- Sexo
- Justificativa clínica
- Classificação de risco
- Procedimento solicitado
'''

PROMPT_CHECK = f'''Analise a mensagem do usuário e verifique se contém todos \
os seguintes campos obrigatórios:

- idade
- sexo
- justificativa
- risco
- procedimento solicitado

Se todos os campos estiverem presentes, responda apenas com **SIM**. Se algum \
campo estiver ausente, responda exatamente **NÃO** na primeira linha e, nas \
linhas seguintes, liste somente os campos que estão faltando, um por linha, \
no formato:
- Campo 1
- Campo 2
- Campo 3
Não adicione explicações nem texto extra.''' 

PROMPT_PROTOCOL = f'''Com base apenas na mensagem do usuário e na lista de \
protocolos disponíveis, determine qual protocolo deve ser aplicado. Responda \
**somente** com o nome exato do protocolo, sem frases, sem explicações e sem \
pontuação extra. Se nenhum protocolo se aplicar ou não houver certeza, \
responda exatamente **NENHUM**.'''

PROMPT_ESPECIFIC = f'''Com base na mensagem do usuário e nos protocolos, \
determine qual dos protocolos deve ser aplicado. Responda **somente** com o \
número do protocolo, em algarismos, sem texto adicional nem pontuação. Se \
nenhum protocolo for aplicável ou não houver certeza, responda exatamente \
**NENHUM**.'''

PROMPT_JUSTIFICATION = f'''Com base na mensagem do usuário e no conteúdo \
descritivo mínimo do protocolo:

- Se a mensagem atende o conteúdo descritivo mínimo do protocolo, responda \
apenas com **SIM**.
- Se não atende, responda **NÃO** na primeira linha e, nas linhas seguintes, \
liste somente os campos que estão faltando, um por linha, no formato:
- Motivo 1
- Motivo 2
- Motivo 3'''