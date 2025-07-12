const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');
const client = new Client();

client.on('qr', qr => {
  qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
  console.log('✅ Cliente WhatsApp está listo');
});

client.on('message', async message => {
  console.log("📥 Mensaje recibido:", message.body);

  try {
    const res = await axios.post('http://localhost:8000/chat/', {
      message: message.body,
      customer_email: `${message.from}@mailton.com`
    });

    // DEBUG: Veamos exactamente qué devuelve la API
    console.log("🔍 DEBUG - Status de respuesta:", res.status);
    console.log("🔍 DEBUG - Datos completos de respuesta:", JSON.stringify(res.data, null, 2));
    console.log("🔍 DEBUG - Tipo de res.data:", typeof res.data);
    console.log("🔍 DEBUG - res.data.reply:", res.data.reply);

    // CAMBIO AQUÍ: Extraer solo el texto de respuesta del objeto
    let reply;
    if (res.data.reply && typeof res.data.reply === 'object') {
      // Si reply es un objeto, extraer solo el campo 'response'
      reply = res.data.reply.response || '🤖 Hubo un problema procesando tu mensaje.';
    } else if (typeof res.data.reply === 'string') {
      // Si reply es un string, usarlo directamente
      reply = res.data.reply;
    } else {
      reply = '🤖 Hubo un problema procesando tu mensaje.';
    }

    console.log("🤖 Respuesta enviada:", reply);
    client.sendMessage(message.from, reply);

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
    
    // Si hay error de respuesta, mostrar detalles
    if (err.response) {
      console.error('❌ Status de error:', err.response.status);
      console.error('❌ Datos de error:', err.response.data);
    }
    
    client.sendMessage(message.from, 'Lo siento, hubo un error técnico. Intenta más tarde.');
  }
});

client.initialize();