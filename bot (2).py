import discord
import tweepy
import os
import re
from flask import Flask
from threading import Thread

# Configuração do Replit para acessar as chaves via secrets
TWITTER_API_KEY = os.environ['TWITTER_API_KEY']
TWITTER_API_SECRET = os.environ['TWITTER_API_SECRET']
TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_SECRET = os.environ['TWITTER_ACCESS_SECRET']
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']

# Autenticação com a API v2 do Twitter
client_twitter = tweepy.Client(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET
)

# Configuração do cliente do Discord
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Habilita a captura do conteúdo das mensagens
client_discord = discord.Client(intents=intents)

# Função para remover @everyone e emojis
def clean_message(message):
    print(f"Conteúdo da mensagem antes da limpeza: {message}")  # Verifica o conteúdo original
    message = re.sub(r'@everyone', '', message)  # Remove @everyone
    message = re.sub(r'<:.+?:\d+>', '', message)  # Remove emojis do tipo <:emoji:123456789>
    message = message.strip()  # Remove espaços extras e quebras de linha
    print(f"Conteúdo da mensagem após a limpeza: {message}")  # Verifica o conteúdo limpo
    return message

# Função para enviar mensagem para o Twitter
def tweet_message(message):
    message = message.strip()  # Remove espaços extras e quebras de linha

    if not message:  # Se a mensagem estiver vazia após remover espaços
        print("Erro: Mensagem vazia, não pode ser postada!")
        return

    # Verifica se a mensagem tem mais de 280 caracteres
    if len(message) > 280:
        print(f"Mensagem muito longa! Dividindo em partes...")

        # Dividindo a mensagem em partes de 280 caracteres
        for i in range(0, len(message), 280):
            message_part = message[i:i + 280]
            try:
                response = client_twitter.create_tweet(text=message_part)
                print(f"Tweet enviado com sucesso! ID: {response.data['id']}")
            except Exception as e:
                print(f"Erro ao enviar tweet: {e}")
        return

    try:
        response = client_twitter.create_tweet(text=message)
        print(f"Tweet enviado com sucesso! ID: {response.data['id']}")
    except Exception as e:
        print(f"Erro ao enviar tweet: {e}")

# Evento de quando o bot do Discord estiver pronto
@client_discord.event
async def on_ready():
    print(f'Bot {client_discord.user} conectado ao Discord!')

# Evento de quando uma mensagem for recebida no Discord
@client_discord.event
async def on_message(message):
    if message.author.bot:  # Verifica se a mensagem é do bot
        if message.author.id == 1044050359586394192:  # ID do bot específico
            tweet_content = clean_message(message.content)  # Limpa a mensagem, removendo @everyone e emojis
            print(f"Conteúdo da mensagem: {tweet_content}")  # Debugging para ver o conteúdo capturado

            if tweet_content:
                tweet_message(tweet_content)  # Envia a mensagem limpa para o Twitter
                print(f"Mensagem do bot enviada para o Twitter: {tweet_content}")
            else:
                print("Erro: Mensagem vazia, não será enviada para o Twitter.")
    else:
        print("Mensagem não é do bot, ignorada.")

# Função para iniciar o servidor Flask
def run_flask():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return 'Bot is running'

    @app.route('/ping')
    def ping():
        return 'Pong'

    app.run(host='0.0.0.0', port=80)

# Inicia o Flask em uma thread separada
def run_bot():
    client_discord.run(DISCORD_TOKEN)

if __name__ == '__main__':
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    run_bot()
