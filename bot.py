from telethon import TelegramClient, events, sync
import asyncio
import base64
from Config import Config
import multiFile
import zipfile
from zipfile import ZipFile
import os
import requests
import re

conf = Config()

bot_token = conf.BotToken
api_id = conf.api_id
api_hash = conf.api_hash


async def text_progres(index,max):
	try:
		if max<1:
			max += 1
		porcent = index / max
		porcent *= 100
		porcent = round(porcent)
		make_text = '(' + str(porcent) + '% '
		index_make = 1
		make_text += '100%)'
		make_text += '\n'
		while(index_make<21):
			  if porcent >= index_make * 5: make_text+='■'
			  else: make_text+='□'
			  index_make+=1
		make_text += '\n'
		make_text += '(' + str(index) + '/' + str(max) + ')'
		return make_text
	except Exception as ex:
			return ''
async def get_file_size(file):
    file_size = os.stat(file)
    return file_size.st_size

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def req_file_size(req):
    try:
        return int(req.headers['content-length'])
    except:
        return 0

def get_name(file):
    return str(file).split('.')[0]

def get_url_file_name(url,req):
    try:
        if "Content-Disposition" in req.headers.keys():
            return str(re.findall("filename=(.+)", req.headers["Content-Disposition"])[0])
        else:
            tokens = str(url).split('/');
            return tokens[len(tokens)-1]
    except:
           tokens = str(url).split('/');
           return tokens[len(tokens)-1]
    return ''

def fixed_name(name):
    return str(name).replace('%20',' ')

def clear_cache():
    try:
        files = os.listdir(os.getcwd())
        for f in files:
            if '.' in f:
                if conf.ExcludeFiles.__contains__(f):
                    print('No Se Permitio la eliminacion de '+f)
                else:
                    os.remove(f)
    except Exception as e:
           print(str(e))



async def down_to_tel(urls,bot,ev,msg):
    try:
         multiFile.files.clear()
         conf.parte = 0
         conf.totalsub = 0
         txt_list = {}

         zipname = get_name(str(urls[0]).split('/')[-1])
         mult_file =  multiFile.MultiFile(zipname+'.7z',1024 * 1024 * conf.ChunkSizeTel)
         zip = ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)

         for url in urls:
             req = requests.get(url, stream = True,allow_redirects=True)
             if req.status_code == 200:
                file_size = req_file_size(req)
                file_name = get_url_file_name(url,req)
                file_name = file_name.replace('"',"")
                file_name = fixed_name(file_name)

                await msg.edit('👉 Descargando 📥 .... \n\n' + '📑 Nombre: ' + str(file_name) + '\n' + '🗂 Tamaño: ' + str(sizeof_fmt(file_size)))

                file_wr = open(file_name,'wb')
                print('Descargando...')
                for chunk in req.iter_content(chunk_size = 1024 * 1024 * conf.ChunkFixed):
                        if chunk:
                            file_wr.write(chunk)
                file_wr.close()
                cpartes = (file_size/((conf.ChunkSizeTel)*1250000))

                await msg.edit('👉 Comprimiendo 📦 ..... \n\n' + '📑 Nombre: ' + str(file_name) + '\n' + '📂 Tamaño de las partes: ' + str(conf.ChunkSizeTel) + ' MB' + '\n'+ '💾Cantidad Partes: ' + str(int(round(cpartes +1,1))) +'\n' + '🗂 Tamaño total: ' + str(sizeof_fmt(file_size)))
                zip.write(file_name)
           
                os.unlink(file_name)
                   
                for f in multiFile.files:
                     conf.parte += 1
                     conf.total = len(multiFile.files)
                     f_size = await get_file_size(f)
                     await msg.edit('👉 Subiendo a Telegram ✈ ..... \n\n' + '📑 Nombre: ' + str(f) + '\n'+ '🗂 Tamaño: ' + str(sizeof_fmt(f_size)) + '\n' + '📤 Subiendo fichero: ' + str(conf.parte) + ' de ' + str(conf.total)  )
                     await bot.send_file(ev.message.chat,f)
                     conf.totalsub += f_size
                     os.unlink(f)
         zip.close()
         mult_file.close()
    except Exception as e:
            await msg.edit('(down_chunked) ' + str(e))
            print(str(e))
    await msg.edit('📌 Proceso Finalizado❗')
    await bot.send_message(ev.chat_id, '👉 Subidos '+ str(sizeof_fmt(conf.totalsub)) + ' 🗂')
            



async def process_message(text,bot,ev,msg):
    try:
         if '/up' in text:
             await down_to_tel(text.replace('/up ','').split(';'),bot,ev,msg)
          
         elif '/zip ' in text:
                     if int(text.replace('/zip ','')) > 2000:
                         await bot.send_message(ev.chat_id, '👉 El tamaño de los archivos máximo es 2000 MB 📣')
                         conf.setChunkSizeTel(2000)
                         await msg.edit('👉 El Tamaño de los Zip al subir a Telegram ha cambiado 📣' + '\n' + '⚠️ Ahora son de: ' + str(conf.ChunkSizeTel) + ' MB ⚠️')
                     elif int(text.replace('/zip ','')) <= 0:
                         await bot.send_message(ev.chat_id, '👉 El tamaño de los archivos mínimo es 1 MB 📣')
                         conf.setChunkSizeTel(1)
                         await msg.edit('👉 El Tamaño de los Zip al subir a Telegram ha cambiado 📣' + '\n' + '⚠️ Ahora son de: ' + str(conf.ChunkSizeTel) + ' MB ⚠️')
                     else:
                         conf.setChunkSizeTel(int(text.replace('/zip ','')))
                         await msg.edit('👉 El Tamaño de los Zip al subir a Telegram ha cambiado 📣' + '\n' + '⚠️ Ahora son de: ' + str(conf.ChunkSizeTel) + ' MB ⚠️')
           
         elif '/help' in text:
             await msg.edit('📌 Comandos disponibles 📌')
             await bot.send_message(ev.chat_id, '👉Para subir archivos a Telegram desde un enlace de descarga usa /up (+ link de descarga) 📤\n 👉Para cambiar el tamaño de esos archivos usas /zip (+ tamaño de los zip) 📦')
             await bot.send_message(ev.chat_id, '❓Ejemplo: /up https://enlace/de/descarga ✅\n❓Ejemplo: /zip 1800 ✅')
             await bot.send_message(ev.chat_id, '👉Para saber el tamaño de los archivos zip escriba /info 📋')
         elif '/info' in text:
             await msg.edit('El tamaño al subir a Telegram es\n\n👇👇\n' + str(conf.ChunkSizeTel) + ' MB')
         elif '/start' in text:
             await msg.edit('🚀 Bot para subir enlaces directos a Telegram 🚀\n\n ⚠️ Bienvenido @' + str(conf.AdminUsers) + ' ⚠️ \n 👉 Utiliza el comando /help para ver las funciones del BOT 🔎')
         else:
             await msg.edit('No puedo procesar esto 😔\n\n👉 Utiliza el comando /help para ver las funciones del BOT 🔎')

    except Exception as e:
             await bot.send_message(ev.chat_id, '❌ Error al ejecutar el comando ❌ ')
             await bot.send_message(ev.chat_id, '❓Ejemplo: /up https://enlace/de/descarga ✅\n❓Ejemplo: /zip 1800 ✅')
    pass
    

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def clear_cache():
    try:
        files = os.listdir(os.getcwd())
        for f in files:
            if '.' in f:
                if conf.ExcludeFiles.__contains__(f):
                    print('No Se Permitido la eliminacion de '+f)
                else:
                    os.remove(f)
    except Exception as e:
           print(str(e))


async def get_file_size(file):
    file_size = os.stat(file)
    return file_size.st_size

def get_full_file_name(file):
    tokens = file.split('.')
    name = ''
    index = 0
    for t in tokens:
        if index < len(tokens):
            name += t + '.'
        index += 1
    return name


def clear_cache():
    try:
        files = os.listdir(os.getcwd())
        for f in files:
            if '.' in f:
                if conf.ExcludeFiles.__contains__(f):
                    print('No Se Permitido la eliminación de '+f)
                else:
                    os.remove(f)
    except Exception as e:
           print(str(e))


def is_accesible(user):
    return user in conf.AdminUsers


async def processMy(ev,bot):
    try:
        if is_accesible(ev.message.chat.username):
                        if conf.procesing == False:
                            #clear_cache()
                            text = ev.message.text
                            conf.procesing = True
                            message = await bot.send_message(ev.chat_id, 'Procesando...🔄')
                            if ev.message.file:
                                await bot.send_message(ev.chat_id,'👉 Envía un enlace de descarga directo para subirlo a telegram 🔗 ')
                            elif text:
                                await process_message(text,bot,ev,message)
                            conf.procesing = False
                        else:
                            await bot.send_message(ev.chat_id,'Estoy trabajando Por favor Espere...⏳')
    except Exception as e:
                        await bot.send_message(str(e))
                        conf.procesing = False


def init():
    try:
        bot = TelegramClient( 
            'bot', api_id=api_id, api_hash=api_hash).start(bot_token=bot_token) 

        action = 0
        actual_file = ''

       

        @bot.on(events.NewMessage()) 
        async def process(ev: events.NewMessage.Event):
                text = ev.message.text
                clear_cache()
                if '#watch' in text:
                    await bot.send_message(ev.chat_id,'Esperando...')
                    conf.watching = True
                elif '#start' in text:
                    conf.watching = False
                    await bot.send_message(ev.chat_id,'Proceso Iniciado!')
                    for e in conf.watch_message:
                      await processMy(e,bot)
                    conf.watch_message.clear()
                elif conf.watching==True:
                    conf.watch_message.append(ev)
                elif '#stop' in text:
                      watching = False
                      watch_message.clear()
                elif conf.watching==False:
                      await processMy(ev,bot)


        loop = asyncio.get_running_loop() 
        loop.run_forever()
    except:
        init()
        conf.procesing = False

if __name__ == '__main__': 
   init()
