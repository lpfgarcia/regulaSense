import os
import protocol

import chainlit as cl
import callbacks as cbk
import prompt_templates as pt

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

MODEL_NAME = 'gpt-5'
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name='GPT-5',
            markdown_description='Modelo eficiente e acessível.',
            icon='public/chat/ses.png',
        )]

@cl.on_chat_start
async def start():
    llm = ChatOpenAI(model=MODEL_NAME, temperature=0, 
        callbacks=[cbk.MessagesHandler()])
    cl.user_session.set('llm', llm)
    await cl.Message(content=pt.CHAT_START).send()

@cl.step(name='Conferindo se as informações estão completas...', type='llm')
async def info_checker(msg: cl.Message):
    
    llm = cl.user_session.get('llm')
    prompt = ChatPromptTemplate.from_messages([
        ('system', f'{pt.SYSTEM}'),
        ('user', f'{pt.PROMPT_CHECK} Mensagem: {msg.content}')
    ])

    chain = prompt | llm
    response = chain.invoke({'mensagem': msg.content})

    if 'SIM' in response.content:
        return True

    response.content = '\n'.join(response.content.splitlines()[1:])
    return response.content

@cl.step(name='Identificando o Área...', type='llm')
async def area_protocol(msg: cl.Message):

    llm = cl.user_session.get('llm')
    prompt = ChatPromptTemplate.from_messages([
        ('system', f'{pt.SYSTEM}'),
        ('user', f'{pt.PROMPT_PROTOCOL} Mensagem: {msg.content} \
            Protocolos: {protocol.AREA}')
    ])

    chain = prompt | llm
    response = chain.invoke({'mensagem': msg.content})

    if 'NENHUM' in response.content:
        return False

    return response.content

@cl.step(name='Identificando o Protocolo Geral...', type='llm')
async def general_protocol(area: str, msg: cl.Message):

    llm = cl.user_session.get('llm')
    prompt = ChatPromptTemplate.from_messages([
        ('system', f'{pt.SYSTEM}'),
        ('user', f'{pt.PROMPT_PROTOCOL} Mensagem: {msg.content} \
            Protocolos: {getattr(protocol, area.upper())}')
    ])

    chain = prompt | llm
    response = chain.invoke({'mensagem': msg.content})

    if 'NENHUM' in response.content:
        return False

    return response.content

@cl.step(name='Identificando o Protocolo Específico...', type='llm')
async def specific_protocol(general: str, msg: cl.Message):

    llm = cl.user_session.get('llm')
    prompt = ChatPromptTemplate.from_messages([
        ('system', f'{pt.SYSTEM}'),
        ('user', f'{pt.PROMPT_ESPECIFIC} Mensagem: {msg.content} \
            Protocolos: {getattr(protocol, general.upper().replace(" ", "_"))}')
    ])

    chain = prompt | llm
    response = chain.invoke({'mensagem': msg.content})

    if 'NENHUM' in response.content:
        return False

    return response.content

@cl.step(name='Apontando se a justificativa atende o Protocolo...', type='llm')
async def protocol_analysis(document: str, msg: cl.Message):

    llm = cl.user_session.get('llm')
    prompt = ChatPromptTemplate.from_messages([
        ('system', f'{pt.SYSTEM}'),
        ('user', f'{pt.PROMPT_JUSTIFICATION} Mensagem: {msg.content} \
            Protocolo: {document}')
    ])

    chain = prompt | llm
    response = chain.invoke({'mensagem': msg.content})

    if 'SIM' in response.content:
        return True

    response.content = '\n'.join(response.content.splitlines()[1:])
    return response.content

@cl.on_message
async def message(msg: cl.Message):

    info = await info_checker(msg)
    if info is not True:
        await cl.Message(content=f'Informações **insuficientes**. Campos ausêntes:\n{info}').send()
        return

    area = await area_protocol(msg)
    if area is False:
        await cl.Message(content=f'Protocolo não identificado.').send()
        return

    general = await general_protocol(area, msg)
    if general is False:
        await cl.Message(content=f'Protocolo não identificado.').send()
        return

    specific = await specific_protocol(general, msg)
    if specific is False:
        await cl.Message(content=f'Protocolo não identificado.').send()
        return

    path =  area.lower() + '/' + general.lower() + '/' + specific + '.txt'
    document = read_file('regulacao/' + path)

    just = await protocol_analysis(document, msg)
    if just is True:
        await cl.Message(content=f'Justificativa **suficiente**.').send()
        return

    await cl.Message(content=f'Justificativa **insuficiente**. Faltam as seguintes informações:\n{just}').send()