const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: true,
    args: ['--no-sandbox']
  }
});

client.on('qr', qr => {
  qrcode.generate(qr, { small: true });
  console.log('📲 Escanea el código QR desde tu WhatsApp');
});

client.on('ready', () => {
  console.log('✅ WhatsApp conectado y listo');
});

client.on('message', async message => {
  try {
    const res = await axios.post('http://localhost:8000/chat/', {
      message: message.body,
      customer_email: `${message.from}@mailton.com`
    });

    const reply = res.data.ai_response || '🤖 Hubo un problema procesando tu mensaje.';
    client.sendMessage(message.from, reply);
  } catch (err) {
    console.error('❌ Error al enviar al backend:', err.message);
    client.sendMessage(message.from, 'Lo siento, hubo un error técnico. Intenta más tarde.');
  }
});

client.initialize();
