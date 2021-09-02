import csv
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
import pandas as pd
import smtplib, ssl
import os
import requests

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def checkCPF(cpf):
    browserCheckCPF = webdriver.Chrome()
    browserCheckCPF.implicitly_wait(10) # seconds
    browserCheckCPF.get("https://www.notamspremiada.ms.gov.br/premiados")
    btnCheckCPF = browserCheckCPF.find_element_by_css_selector('button.modal-trigger')
    btnCheckCPF.click()
    inputCPF = browserCheckCPF.find_element_by_css_selector('#cpf')
    inputCPF.send_keys(cpf)
    btnAnalisar = browserCheckCPF.find_element_by_css_selector('button')
    btnAnalisar.click()
    sleep(2)
    htmlCheckCpfResult = browserCheckCPF.find_element_by_css_selector('div>div>h5')
    message = htmlCheckCpfResult.get_attribute('innerText').split('\n')
    browserCheckCPF.close()
    ##message[0] = 'Ganhou'
    if message[0] == 'Que pena!':
        message = 'Que pena! \n\n Nao foi dessa vez!'
    else:
        message = 'Parabens, voce foi premiado \n\n Cadastre-se no site oficial para receber seu premio \n\n <a href="https://www.notamspremiada.ms.gov.br/cadastre-se"> NOTA MS PREMIADA </a>'
    return message

def sendEmailCheckCpf():
    # me == my email address
    # you == recipient's email address
    sender_email = "automailnfmspremiada@gmail.com"
    receiver_email = "automailnfmspremiada@gmail.com"

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Verificação sorteio Nota MS premiada"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Create the body of the message (a plain-text and an HTML version).
    text = "Olá!\n"
    text += "Tudo bem?\n"
    text += "Você foi sorteado no programa Nota MS Premiada\n"
    text += "Acesse o link abaixo para se cadastrar e receber seu prêmio:\n"
    text += "https://www.notamspremiada.ms.gov.br/cadastre-se"
    html = """\
    <style>
     .gray {
         color: #CCC
     }
    </style>
    <html>
      <head></head>
      <body>
        <p><h2><font color="green">Parabéns!</font></h2><br>
           Você foi sorteado no programa Nota MS Premiada<br><br>
           Suas dezenas vencedoras foram:<br>
           <h3>01-12-35-38-41-48-50-53</h3><br>
           As dezenas sorteadas foram:<br>
           <h3>12-35-38-41-48-50</h3><br>
           Clique <a href="https://www.notamspremiada.ms.gov.br/cadastre-se">AQUI</a> para se cadastrar e receber seu prêmio.
        </p>
      </body>
    </html>
    """

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    # Send the message via local SMTP server.
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    password = os.environ.get('MAIL_PW')
    context = ssl.create_default_context()
    print(sender_email, password)
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

def create_browser_zap():
    ## cria uma instancia de navegador e espera a leitura do QR code no whatsapp
    ## assim podemos enviar várias mensagens usando a mesma instancia e depois fechar quando temrinar os envios
    browserZap = webdriver.Chrome() 
    browserZap.implicitly_wait(10) # seconds
    browserZap.get("https://web.whatsapp.com/")
    
    continueConfirmation = input('Continuar? (s/n)')
    if continueConfirmation !='s':
        browserZap.close()
        print('Processo interrompido!')
        return False
    
    return browserZap

def sendZap(browserZap, message, destiny):
    ## envia mensagem no whatsapp
    ## param: browserZap <- instancia do browser já com whatsapp validado com QR code
    ## param: message <- mensagem a ser enviada
    ## param: destiny <- texto a ser pesquisado para achar o destinatario 
    
    if not browserZap:
        return 'Necessária instância de navagador. Processo interrompido!'
    
    search_box = browserZap.find_element_by_css_selector('label>div>div.copyable-text')
    search_box.send_keys(destiny)
    search_box.send_keys(Keys.ENTER)
    search_box = browserZap.find_element_by_css_selector('div>div>div.copyable-text')
    message_box = browserZap.find_element_by_css_selector('footer>div>div>div>div>div>div.copyable-text')
    browserZap.execute_script("document.querySelector('label>div>div.copyable-text').innerText = '' ")
    message_box.send_keys(message)
    message_box.send_keys(Keys.ENTER)
    ##browserZap.close()