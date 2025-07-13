const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: true,
    args: ['--no-sandbox']
  }
});

// Mapeo de modelos a URLs de imágenes (formato .jpg para mejor compatibilidad)
const IMAGENES_MODELOS = {
  "ANDORRA": "https://i.imgur.com/S9ctWUN.jpg",
  "BARBUDA": "https://i.imgur.com/vnBqZoq.jpg", 
  "BORA": "https://i.imgur.com/odVNk55.jpg",
  "HOBART": "https://i.imgur.com/whDv56s.jpg",
  "MILAN": "https://i.imgur.com/4rmEV98.jpg",
  "SANTORY": "https://i.imgur.com/Sdg0JZU.jpg"
};

client.on('qr', qr => {
  qrcode.generate(qr, { small: true });
  console.log('📲 Escanea el código QR desde tu WhatsApp');
});

client.on('ready', () => {
  console.log('✅ WhatsApp conectado y listo');
});

async function sendImageFromUrl(chatId, imageUrl, caption = '') {
  try {
    console.log(`📸 Descargando imagen desde: ${imageUrl}`);
    
    // Descargar imagen desde URL con headers para evitar rate limit
    const response = await axios.get(imageUrl, { 
      responseType: 'arraybuffer',
      timeout: 15000, // 15 segundos timeout
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'image/png,image/jpeg,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
      }
    });
    
    // Detectar tipo de contenido
    const contentType = response.headers['content-type'] || 'image/jpeg';
    
    // Crear media desde buffer
    const media = new MessageMedia(
      contentType, 
      Buffer.from(response.data).toString('base64'),
      'modelo.jpg'
    );
    
    // Enviar imagen con caption
    await client.sendMessage(chatId, media, { caption: caption });
    console.log(`✅ Imagen enviada exitosamente`);
    return true;
    
  } catch (error) {
    console.error(`❌ Error enviando imagen: ${error.message}`);
    
    // Fallback: enviar URL como texto
    await client.sendMessage(chatId, `${caption}\n\nImagen: ${imageUrl}`);
    return false;
  }
}

async function processMessageWithImages(chatId, textMessage) {
  try {
    console.log("🔍 Buscando imágenes en el mensaje...");
    
    // Detectar marcadores de imagen: [IMG:MODELO_NAME]
    const imagePattern = /\[IMG:(\w+)\]/g;
    const matches = [...textMessage.matchAll(imagePattern)];
    
    if (matches.length > 0) {
      console.log(`📸 Encontradas ${matches.length} imágenes para enviar`);
      
      // Remover marcadores del texto
      let cleanText = textMessage.replace(imagePattern, '').trim();
      
      // Enviar texto primero (si hay contenido)
      if (cleanText) {
        await client.sendMessage(chatId, cleanText);
        console.log("✅ Texto enviado");
      }
      
      // Enviar cada imagen
      for (const match of matches) {
        const modelName = match[1].toUpperCase();
        const imageUrl = IMAGENES_MODELOS[modelName];
        
        if (imageUrl) {
          const caption = `🦶 Modelo ${modelName}`;
          await sendImageFromUrl(chatId, imageUrl, caption);
          
          // Pausa más larga para evitar rate limit
          await new Promise(resolve => setTimeout(resolve, 3000));
        } else {
          console.warn(`⚠️ No se encontró imagen para modelo: ${modelName}`);
        }
      }
    } else {
      // Detectar URLs de imgur en el texto y convertirlas a imágenes
      const imgurPattern = /https:\/\/i\.imgur\.com\/[\w]+\.png/g;
      const imgurMatches = [...textMessage.matchAll(imgurPattern)];
      
      if (imgurMatches.length > 0) {
        console.log(`📸 Encontradas ${imgurMatches.length} URLs de Imgur para convertir`);
        
        // Remover URLs del texto
        let cleanText = textMessage.replace(imgurPattern, '').trim();
        
        // Enviar texto limpio primero
        if (cleanText) {
          await client.sendMessage(chatId, cleanText);
          console.log("✅ Texto enviado");
        }
        
        // Enviar cada imagen de Imgur
        for (const match of imgurMatches) {
          const imageUrl = match[0];
          const modelName = Object.keys(IMAGENES_MODELOS).find(key => 
            IMAGENES_MODELOS[key] === imageUrl
          );
          
          const caption = modelName ? `🦶 Modelo ${modelName}` : '🦶 Modelo Mailton Kanazo';
          await sendImageFromUrl(chatId, imageUrl, caption);
          
          // Pausa más larga para evitar rate limit
          await new Promise(resolve => setTimeout(resolve, 3000));
        }
      } else {
        // No hay imágenes, enviar texto normal
        await client.sendMessage(chatId, textMessage);
        console.log("✅ Mensaje de texto enviado");
      }
    }
    
  } catch (error) {
    console.error('❌ Error procesando mensaje con imágenes:', error.message);
    // Fallback: enviar mensaje original
    await client.sendMessage(chatId, textMessage);
  }
}

client.on('message', async message => {
  console.log("📥 Mensaje recibido:", message.body);

  try {
    const res = await axios.post('http://localhost:8000/chat/', {
      message: message.body,
      customer_email: `${message.from}@mailton.com`
    });

    // DEBUG: Veamos exactamente qué devuelve la API
    console.log("🔍 DEBUG - Status de respuesta:", res.status);
    console.log("🔍 DEBUG - res.data.reply:", JSON.stringify(res.data.reply, null, 2));

    // Extraer respuesta correctamente del nuevo formato
    let reply;
    if (res.data.reply && typeof res.data.reply === 'object') {
      reply = res.data.reply.response || '🤖 Hubo un problema procesando tu mensaje.';
    } else if (typeof res.data.reply === 'string') {
      reply = res.data.reply;
    } else {
      reply = '🤖 Hubo un problema procesando tu mensaje.';
    }

    console.log("🤖 Respuesta a procesar:", reply);

    // Procesar mensaje con posibles imágenes
    await processMessageWithImages(message.from, reply);

    // LOG ADICIONAL: Información del análisis
    if (res.data.reply && typeof res.data.reply === 'object') {
      console.log("📊 Análisis del mensaje:");
      console.log("  🎯 Intención:", res.data.reply.intent);
      console.log("  🛍️ Productos:", res.data.reply.products_mentioned);
      console.log("  🎨 Colores:", res.data.reply.colors_mentioned);
      console.log("  📏 Tallas:", res.data.reply.sizes_mentioned);
      console.log("  📈 Confianza:", res.data.reply.confidence);
    }

  } catch (err) {
    console.error('❌ Error al enviar al backend:', err.message);
    
    if (err.response) {
      console.error('❌ Status de error:', err.response.status);
      console.error('❌ Datos de error:', err.response.data);
    }
    
    client.sendMessage(message.from, 'Lo siento, hubo un error técnico. Intenta más tarde.');
  }
});

client.initialize();
