from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyser = SentimentIntensityAnalyzer()
from GoogleNews import GoogleNews
from googletrans import Translator
translator = Translator()
from pytrends.request import TrendReq

class Item(BaseModel):
    mensagem: str
    
app = FastAPI()

@app.post("/trends")
async def get_trends(item: Item):
    pytrend = TrendReq(hl='pt-BR', tz=360)
    keywords = [item.mensagem]
    pytrend.build_payload(
    kw_list=keywords,
    cat=0,
    timeframe='today 1-m',
    geo='BR',
    gprop='news')
    data = pytrend.interest_over_time()
    hoje = str(data[item.mensagem][29])  
    ontem = str(data[item.mensagem][28])
    if data[item.mensagem][29] > data[item.mensagem][28]:
      resultado = 'Os interesse de pesquisa de hoje foram maior que ontem'
    else:
      resultado = 'Os interesse de pesquisa de hoje foram menor que ontem'
    return {"interesse de pesquisa relativo hoje": hoje , "interesse de pesquisa relativo ontem": ontem,"variação":resultado}

@app.post("/analysy")
async def create_item(item: Item):
    result = ""
    googlenews = GoogleNews()
    googlenews.set_lang('pt')
    googlenews.search(item.mensagem)
    googlenews.results()
    result = googlenews.get_texts()[0]
    translations  = translator.translate(result, dest='en')
    textTranslator = translations.text
    score = analyser.polarity_scores(textTranslator) # avaliação de polaridade de sentimento da mensagem
    compound = (analyser.polarity_scores(textTranslator)['compound'])  # capitura da média do sentimento da mensagem
    if compound > 0:
      mensagemSentimento = "noticia positiva" 
    elif compound >= 0:
      mensagemSentimento = "noticia neutra" 
    else:
      mensagemSentimento = "noticia negativa"
    return {"mensagem":googlenews.get_texts()[0],"sentimento":mensagemSentimento}