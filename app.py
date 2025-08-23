import os
import protocol
import chainlit as cl

from openai import AsyncOpenAI

MODEL_NAME = 'gpt-4o'
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines    

@cl.on_chat_start
async def start():
    client = AsyncOpenAI(api_key=OPENAI_KEY)
    cl.user_session.set('client', client)
    await cl.Message(content=f'''Olá! Sou um Assistente da Secretaria de Saúde do Distrito Federal.
        Por favor, informe a idade, o sexo, a justificativa, o risco e o procedimento solicitado do paciente.''').send()

@cl.step(name='Conferindo se as informações estão completas...', type='tool')
async def info_checker(msg: cl.Message):
    
    client = cl.user_session.get('client')
    response = await client.chat.completions.create(
        model=MODEL_NAME, 
        messages=[
            {'content': f'''Você é um Assistente da Secretaria de Saúde do Distrito Federal.''', 'role': 'system'},
            {'content': f'''O usuário informou a idade, o sexo, a justificativa, o risco e o procedimento solicitado na mensagem?
            Responda **somente** com **SIM** ou **NÃO**. Mensagem: {msg.content}''', 'role': 'user'}
        ], temperature=0
    )

    response = response.choices[0].message.content

    if 'sim' in response.lower():
        return True
    return False

@cl.step(name='Verificando quais informações estão incompletas...', type='tool')
async def info_explanation(msg: cl.Message):
    
    client = cl.user_session.get('client')
    response = await client.chat.completions.create(
        model=MODEL_NAME, 
        messages=[
            {'content': f'''Você é um Assistente da Secretaria de Saúde do Distrito Federal.''', 'role': 'system'},
            {'content': f'''O usuário esqueceu de informar um ou mais dos seguintes campos: idade, sexo, justificativa, risco e procedimento solicitado.
            Indique **somente** quais campos estão faltando na mensagem, sem acrescentar explicações extras. 
            Mensagem: {msg.content}''', 'role': 'user'}
        ], temperature=0
    )

    response = response.choices[0].message.content
    return response

@cl.step(name='Identificando o Área...', type='tool')
async def area_protocol(msg: cl.Message):

    client = cl.user_session.get('client')
    response = await client.chat.completions.create(
        model=MODEL_NAME, 
        messages=[
            {'content': f'''Você é um Assistente da Secretaria de Saúde do Distrito Federal.''', 'role': 'system'},
            {'content': f'''Com base na mensagem, qual dos protocolos deve ser utilizado?
            Mensagem: {msg.content}
            Protocolos: {protocol.AREA}
            Responda **somente** com o **nome** do protocolo.''', 'role': 'user'}
        ], temperature=0
    )

    response = response.choices[0].message.content
    return response

@cl.step(name='Identificando o Protocolo Geral...', type='tool')
async def general_protocol(area: str, msg: cl.Message):

    client = cl.user_session.get('client')
    response = await client.chat.completions.create(
        model=MODEL_NAME, 
        messages=[
            {'content': f'''Você é um Assistente da Secretaria de Saúde do Distrito Federal.''', 'role': 'system'},
            {'content': f'''Com base na mensagem, qual dos protocolos deve ser utilizado?
            Mensagem: {msg.content}
            Protocolos: {getattr(protocol, area.upper())}
            Responda **somente** com o **nome** do protocolo.''', 'role': 'user'}
        ], temperature=0
    )

    response = response.choices[0].message.content
    return response

@cl.step(name='Identificando o Protocolo Específico...', type='tool')
async def specific_protocol(general: str, msg: cl.Message):

    client = cl.user_session.get('client')
    response = await client.chat.completions.create(
        model=MODEL_NAME, 
        messages=[
            {'content': f'''Você é um Assistente da Secretaria de Saúde do Distrito Federal.''', 'role': 'system'},
            {'content': f'''Com base na mensagem, qual dos protocolos deve ser utilizado?
            Mensagem: {msg.content}
            Protocolos: {getattr(protocol, general.upper().replace(' ', '_'))}
            Responda **somente** o **número** do protocolo. Se não souber retorne **0**.''', 'role': 'user'}
        ], temperature=0
    )

    response = response.choices[0].message.content
    return response

@cl.step(name='Detectando se a justificativa atende o Protocolo Específico...', type='tool')
async def protocol_analysis(document: str, msg: cl.Message):

    client = cl.user_session.get('client')
    response = await client.chat.completions.create(
        model=MODEL_NAME, 
        messages=[
            {'content': f'''Você é um Assistente da Secretaria de Saúde do Distrito Federal.''', 'role': 'system'},
            {'content': f'''Com base na mensagem e no conteúdo descritivo mínimo do protocolo, o procedimento deve ser aceito?
            Responda **somente** **SIM** ou **NÃO**. Se **NÃO**, retorne a justificativa.\n
            Mensagem: {msg.content}\n
            Protocolo: {document}''', 'role': 'user'}
        ], temperature=0
    )

    return response.choices[0].message.content

@cl.on_message
async def message(msg: cl.Message):

    status = await info_checker(msg)

    if status:

        area = await area_protocol(msg)
        general = await general_protocol(area, msg)
        specific = await specific_protocol(general, msg)
        
        if specific.isdigit() and int(specific) > 0:
            
            path = 'regulacao/' + area.lower() + '/' + general.lower() + '/' + specific + '.txt'
            document = read_file(path)
            
            justification = await protocol_analysis(document, msg)
            
            if 'sim' in justification.lower():
                await cl.Message(content=f'Justificativa **suficiente**').send()
            else:
                await cl.Message(content=f'Justificativa **insuficiente**\n + {justification}').send()    
        
        else:
        
            await cl.Message(content=f'Protocolo não identificado. Desculpe-me!').send()    

    else: 
        await cl.Message(content=f'''Os seguintes campos estão ausêntes: {info_explanation(msg)}.''').send()

        