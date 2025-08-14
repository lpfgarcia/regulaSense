import os
import chainlit as cl

from openai import AsyncOpenAI

MODEL_NAME = 'gpt-4o'
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

ADULT = '''Protocolo 1 – Distúrbios de Refração ou Acomodação\n
Protocolo 2 – Catarata\n
Protocolo 3 – Retinopatia ou Outras Doenças de Retina\n
Protocolo 4 – Estrabismo\n
Protocolo 5 – Doenças das Pálpebras, Vias Lacrimais e Órbita\n
Protocolo 6 – Glaucoma\n
Protocolo 7 – Doenças da Córnea e da Superfície Ocular\n
Protocolo 8 – Uveítes\n'''

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines    

@cl.on_chat_start
async def start():
    client = AsyncOpenAI(api_key=OPENAI_KEY)
    cl.user_session.set('client', client)
    await cl.Message(content='Olá! Sou um Assistente da Secretaria de Saúde do Distrito Federal.\n' + 
        'Por favor, informe a idade, sexo, justificativa, risco e procedimento solicitado do paciente.').send()

@cl.step(name='Conferindo se as informações estão completas...', type='tool')
async def info_checker(msg: cl.Message):
    
    client = cl.user_session.get('client')
    response = await client.chat.completions.create(
        model=MODEL_NAME, 
        messages=[
            {'content': f'Você é um Assistente da Secretaria de Saúde do Distrito Federal.', 'role': 'system'},
            {'content': f'No contexto da mensagem, o usuário informou a idade, o sexo, a justificativa, o risco e o procedimento solicitado?\nResponda **somente** **SIM** ou **NÃO**.\n\n Mensagem: {msg.content}', 'role': 'user'}
        ], temperature=0
    )

    response = response.choices[0].message.content

    if 'sim' in response.lower():
        return True
    return False

@cl.step(name='Verificando se é Oftalmologia Pediátrica ou Adulto...', type='tool')
async def type_extractor(msg: cl.Message):

    client = cl.user_session.get('client')
    response = await client.chat.completions.create(
        model=MODEL_NAME, 
        messages=[
            {'content': f'Você é um Assistente da Secretaria de Saúde do Distrito Federal.', 'role': 'system'},
            {'content': f'Com base no contexto da mensagem, qual dos protocolos (Oftalmologia Adulto ou Oftalmologia Pediátrica) deve ser utilizado?\nResponda **somente** **adulto** ou **pediátrica**.\n\n Mensagem: {msg.content}', 'role': 'user'}
        ], temperature=0
    )

    response = response.choices[0].message.content

    if 'pediátrica' in response.lower():
        return 'pediatrica'
    return 'adulto'

@cl.step(name='Detectando qual o Protocolo da Oftalmologia Adulto...', type='tool')
async def type_protocol(msg: cl.Message, patient: str):

    print(patient)
    client = cl.user_session.get('client')
    protocol_list = ADULT if patient == 'adulto' else CHILD
    print(protocol_list)
    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {'content': 'Você é um Assistente da Secretaria de Saúde do Distrito Federal.', 'role': 'system'},
            {'content': f'Com base no contexto da mensagem, qual dos seguintes protocolos da Oftalmologia Adulto deve ser seguido?\nResponda **somente** o número do protocolo. Se não souber, retorne 0.\n\nMensagem: {msg.content}\n\nProtocolos: {protocol_list}', 'role': 'user'}
        ], temperature=0
    )

    return response.choices[0].message.content

@cl.step(name='Identificando se a justificativa atende o protocolo...', type='tool')
async def protocol_analysis(msg: cl.Message, protocol: str):

    client = cl.user_session.get('client')
    response = await client.chat.completions.create(
        model=MODEL_NAME, 
        messages=[
            {'content': 'Você é um Assistente da Secretaria de Saúde do Distrito Federal.', 'role': 'system'},
            {'content': f'Com base no contexto da mensagem, o protocolo do procedimento está sendo seguido de forma adequada?\nResponda **somente** **SIM** ou **NÃO**. Se **NÃO**, retorne a justificativa.\n\nMensagem: {msg.content}\n\nProtocolo: {protocol}', 'role': 'user'}
        ], temperature=0
    )

    return response.choices[0].message.content

@cl.on_message
async def message(msg: cl.Message):

    status = await info_checker(msg)
    if status:
        
        patient = await type_extractor(msg)
        protocol = await type_protocol(msg, patient)

        if protocol.isdigit() and int(protocol) > 0:
            path = 'regulacao/oftalmologia/' + patient + '/' + protocol + '.txt'
            lines = read_file (path)
            justification = await protocol_analysis(msg, lines)
            if 'sim' in justification.lower():
                await cl.Message(content=f'Justificativa **suficiente**').send()
            else:
                await cl.Message(content=f'Justificativa **insuficiente**\n + {justification}').send()    
        else:
            await cl.Message(content=f'Protocolo não identificado. Desculpe-me!').send()    
